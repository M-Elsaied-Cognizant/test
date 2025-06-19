import bleach
import json
import re
import ast
import traceback
from typing import Dict, Any, Optional
from neuro_san.session.http_service_agent_session import HttpServiceAgentSession
from neuro_san.internals.messages.chat_message_type import ChatMessageType
from neuro_san.message_processing.basic_message_processor import BasicMessageProcessor
from flask import jsonify
from .utility import clean_json
from app.config import Neurosan_config, ErrorMessage, RedisConfig
from app.redisHelper import set_redis_hashmap, get_redis_hashmap, set_redis_expiry
from botcommonlib.utilities.applogging import logger

FALLBACK_RESPONSE = {
    "Response": ErrorMessage.Fallback,
    "IntentId": "NA",
    "Response_source": "NA",
    "Agent_Name": "NA",
    "Is_Autonomous_Agent": "NA",
    "Is_ChatContext_Required": "NA",
    "Is_SessionID_Required": "NA",
    "Agent_Generated_Session_ID": "NA"
}

def ask_query(query_payload: Dict[str, Any]) -> tuple:
    """
    Handles the query payload and validates the input.
    """
    query = bleach.clean(query_payload.get("query", ""))
    metadata = clean_json(query_payload.get("metadata", {}))
    sly_data = clean_json(query_payload.get("sly_data", {}))
    sly_data["session_id"] = metadata.get("session_id", "None")
    sly_data["query_id"] = metadata.get("query_id", "None")

    if "agent_name" not in query_payload or not query_payload.get("agent_name"):
        agent_name = Neurosan_config.NEUROSAN_AGENT_NAME
    else:
        agent_name = bleach.clean(query_payload.get("agent_name", "").strip()) or Neurosan_config.NEUROSAN_AGENT_NAME
    if not agent_name:
        return jsonify({"error": "Agent name cannot be empty or missing"}), 400

    # Create an instance of neurosan_predictor
    predictor = neurosan_predictor(query, sly_data, metadata, agent_name)
    response = predictor.neurosan_predict()
    return jsonify(response), 200

class neurosan_predictor:
    """
    Class to handle the prediction using the Neurosan API.
    """
    def __init__(self, query: str, sly_data: Dict[str, Any], metadata: Dict[str, Any], agent_name: str):
        self.user_input = query
        self.user_sly_data = sly_data
        self.user_metadata = metadata
        self.agent_name = agent_name
        self.extra_data = {
            "user_id": str(metadata.get("user_id")),
            "request_id": metadata.get("session_id"),
            "query_id": str(metadata.get("query_id")),
        }
        channel = metadata.get("channel", "").lower()
        if channel == "teams":
            RedisChatContextKeyPrefix = "AIAssistant_4139_T_ChatContext_"
        elif channel == "web":
            RedisChatContextKeyPrefix = "AIAssistant_4139_W_ChatContext_"
        elif channel == "mobile":
            RedisChatContextKeyPrefix = "AIAssistant_4139_M_ChatContext_"
        else:
            RedisChatContextKeyPrefix = None
        if RedisChatContextKeyPrefix:
            self.Redis_ChatContextKey = f"{RedisChatContextKeyPrefix}{metadata.get('session_id')}"
            set_redis_expiry(self.Redis_ChatContextKey, RedisConfig.REDIS_TTL)
        else:
            self.Redis_ChatContextKey = None

    def neurosan_predict(self) -> Dict[str, Any]:
        """
        Predicts the response using the Neurosan API.
        """
        try:
            logger.info(f"neurosan_predict request for '{self.user_input}'", extra=self.extra_data)
            agent_session = self._initialize_agent_session()
            chat_context = None
            if self.Redis_ChatContextKey:
                chat_context = get_redis_hashmap(self.Redis_ChatContextKey, "chat_histories")

            chat_request = self._build_chat_request(chat_context)
            # logger.info(f"-----chat_request: {chat_request} {type(chat_request)}-----")
            responses, sly_data_dict = self._process_chat_responses(agent_session, chat_request)

            # RedisChatContextKey = f"{RedisConfig.REDIS_KEY_CHAT_CONTEXT_PREFIX}{self.user_metadata['session_id']}"
            # store_chat_context(RedisChatContextKey, chat_context, sly_data_dict.get("AgentName", "NA").split(".")[0])

            validated_response = self.validate_neurosan_response(responses, sly_data_dict)
            logger.info(f"Validated Response: {validated_response} {type(validated_response)}", extra=self.extra_data)
            if "error" in validated_response:
                raise
            logger.info(f"neurosan_predict ended for '{self.user_input}'", extra=self.extra_data)
            return validated_response

        except Exception as e:
            logger.error(f"Exception in neurosan_predict: {traceback.format_exc()}", extra=self.extra_data)
            return FALLBACK_RESPONSE

    def _process_chat_responses(self, agent_session: HttpServiceAgentSession, chat_request: Dict[str, Any]) -> tuple:
        """
        Processes chat responses from the agent session.
        """
        responses = []
        chat_context = None
        stream_input = BasicMessageProcessor()

        for response in agent_session.streaming_chat(chat_request):
            if not isinstance(response, dict):
                logger.warning("Invalid response type, skipping iteration.", extra=self.extra_data)
                continue
            responses.append(response)
            stream_input.process_message(response.get("response", {}))

        sly_data_dict = stream_input.get_sly_data()
        last_chat_response = None

        if sly_data_dict is None:
            sly_data_dict = {}
            Agent_Name = self.agent_name
            Is_Autonomous_Agent = False
        else:
            Agent_Name = sly_data_dict.get("AgentName").split(".")[0] if sly_data_dict.get("AgentName") else self.agent_name
            Is_Autonomous_Agent = sly_data_dict.get("Is_Autonomous_Agent", False)
            if "Response" in sly_data_dict:
                last_chat_response = sly_data_dict.get("Response")

        if last_chat_response is None:
            last_chat_response = stream_input.get_answer()
            last_chat_response = _clean_response_data(last_chat_response)
        # -----Logic for chat_context-----
        if Neurosan_config.IsChatContextEnabled and self.Redis_ChatContextKey:
            chat_context = stream_input.get_chat_context()
            set_redis_hashmap(self.Redis_ChatContextKey, "chat_histories", chat_context)

        previous_agent_name = None
        if self.Redis_ChatContextKey:
            previous_agent_name = get_redis_hashmap(self.Redis_ChatContextKey, "AgentName")
            set_redis_hashmap(self.Redis_ChatContextKey, "AgentName", Agent_Name)

        logger.info(f"Is_Autonomous_Agent:{Is_Autonomous_Agent}")
        if Is_Autonomous_Agent:
            # Initialize conversation if no previous agent or a different agent was used before
            if previous_agent_name in [None, "NA"] or previous_agent_name != Agent_Name:
                Init_Conversation = True
            else:
                Init_Conversation = False
        else:
            Init_Conversation = False

        sly_data_dict["Init_Conversation"]=Init_Conversation
        sly_data_dict["previous_agent_name"] = Agent_Name
        # -----Logic for chat_context-----
        return last_chat_response, sly_data_dict

    def validate_neurosan_response(self, response_data: Any, sly_data: dict) -> Dict[str, Any]:
        """
        Validates the response data and handles content filtering errors.
        """
        logger.info("Validating Neurosan response", extra=self.extra_data)
        if not response_data:
            logger.warning("Response data is empty, returning fallback response", extra=self.extra_data)
            fallback_response = FALLBACK_RESPONSE.copy()
            fallback_response["Response"] = ErrorMessage.Fallback_Noresponse
            return fallback_response

        # Ensure response_data is a string before content filtering
        if isinstance(response_data, list) or isinstance(response_data, dict):
            response_data_str = json.dumps(response_data)  # Convert list/dict to JSON string
        elif isinstance(response_data, str):
            response_data_str = response_data  # Already a string
        else:
            logger.error("Unsupported response_data type, returning fallback response", extra=self.extra_data)
            return FALLBACK_RESPONSE.copy()

        # Check for content filtering errors
        content_filter_result = handle_content_filtering(response_data_str)
        if content_filter_result:
            logger.warning("Content filtering triggered, returning fallback response", extra=self.extra_data)
            return content_filter_result

        response_data_parsed = None
        try:
            if isinstance(response_data_str, str):
                try:
                    response_data_parsed = ast.literal_eval(response_data_str)
                except (ValueError, SyntaxError):
                    response_data_parsed = clean_json(json.loads(response_data_str))
                if "Response" in response_data_parsed:
                    if isinstance(response_data_parsed["Response"], str):
                        try:
                            response_data_parsed = ast.literal_eval(response_data_parsed["Response"])
                        except (ValueError, SyntaxError):
                            logger.error("ast.literal_eval failed, returning original string")
                            try:
                                response_data_parsed = json.loads(response_data_parsed["Response"])
                            except (ValueError, SyntaxError):
                                logger.error("json.loads also failed, falling back to ast.literal_eval")
                                response_data_parsed = response_data_parsed["Response"]
                    else:
                        response_data_parsed = response_data_parsed["Response"]
        except json.JSONDecodeError:
            logger.error("Failed to parse response data, returning fallback response", extra=self.extra_data)
            response_data_parsed = [{"type": "AdaptiveCard", "body": [{"type": "TextBlock", "text": response_data_str, "wrap": "true"}], "actions": [], "version": "1.5" }]

        # If response_data is valid, return it with additional metadata
        if isinstance(response_data_parsed, (list, dict)):
            if "error" in response_data_parsed:
                # Fallback in case of unexpected issues
                logger.error("Unexpected issue with response data, ...response_data_parsed... returning fallback response", extra=self.extra_data)
                return FALLBACK_RESPONSE.copy()

            return {
                "Response": response_data_parsed,
                "IntentId": sly_data.get("IntentId", "NA"),
                "Response_source": sly_data.get("ResponseSource", "NEUROSAN"),
                "Agent_Name": sly_data.get("AgentName", "NA").split(".")[0],
                "Init_Conversation": sly_data.get("Init_Conversation", False),
                "Is_Autonomous_Agent": sly_data.get("Is_Autonomous_Agent", False),
                "Is_ChatContext_Required": sly_data.get("Is_ChatContext_Required", False),
                "Is_SessionID_Required": sly_data.get("Is_SessionID_Required", False),
                "Agent_Generated_Session_ID": sly_data.get("Agent_Generated_Session_ID", None),
            }

    def _initialize_agent_session(self) -> HttpServiceAgentSession:
        """
        Initializes the HttpServiceAgentSession.
        """
        # To get the agent name from Redis to support the user to talk to the same agent in the next queries
        # redis_agent_name = get_redis_hashmap(f"{RedisConfig.REDIS_KEY_CHAT_CONTEXT_PREFIX}{self.user_metadata['session_id']}", "AgentName")
        # agent_name = redis_agent_name if redis_agent_name and redis_agent_name not in [None, 'NA'] else Neurosan_config.NEUROSAN_AGENT_NAME
        # logger.info(f"Initializing agent session for agent: {self.agent_name}", extra=self.extra_data)

        return HttpServiceAgentSession(
            host=Neurosan_config.NEUROSAN_HOST,
            port=Neurosan_config.NEUROSAN_PORT,
            agent_name=self.agent_name if self.agent_name else Neurosan_config.NEUROSAN_AGENT_NAME,
            metadata={
                "user_id": str(self.user_metadata.get("user_id", "")),
                "request_id": self.user_metadata.get("session_id", ""),
                "query_id": str(self.user_metadata.get("query_id", "")),
                "channel": self.user_metadata.get("channel", "")
            },
            timeout_in_seconds=180
        )

    def _build_chat_request(self, chat_context: str) -> Dict[str, Any]:
        """
        Builds the chat request payload.
        """
        chat_request = {
            "user_message": {
                "type": ChatMessageType.HUMAN,
                "text": self.user_input
            },
            "chat_filter": {
                "chat_filter_type": Neurosan_config.NEUROSAN_CHAT_FILTER
            },
            "sly_data": {
                "associate_id": str(self.user_sly_data.get("associate_id", "")),
                "Dept_id": str(self.user_sly_data.get("Dept_id", "")),
                "Location": str(self.user_sly_data.get("Location", "")),
                "App_id": str(self.user_sly_data.get("App_id", "")),
                "user_query": str(self.user_sly_data.get("query", "")),
                "bot_id": str(self.user_sly_data.get("bot_id", "")),
                "request_id": str(self.user_sly_data.get("session_id", "")),
                "query_id": str(self.user_sly_data.get("query_id", "")),
                "action": str(self.user_sly_data.get("action", "")),
                "user_id": str(self.user_sly_data.get("user_id", "")),
                "email_id": str(self.user_sly_data.get("email_id", "")),
                "intent_id": str(self.user_sly_data.get("intent_id", "")),
                "AzureSignalRconnectionID": str(self.user_sly_data.get("AzureSignalRconnectionID", "")),
                "session_id": str(self.user_sly_data.get("session_id", "")),
                "channel": str(self.user_sly_data.get("channel", "")),
                "cardid": str(self.user_sly_data.get("cardid", "")),
                "agent_name": str(self.user_sly_data.get("agent_name", ""))
            }
        }
        if chat_context and Neurosan_config.IsChatContextEnabled:
            chat_request["chat_context"] = {"chat_histories": json.loads(chat_context)}
        return chat_request

def _clean_response_data(response_data: str) -> str:
    """
    Cleans and formats the response data.
    """
    if not response_data:
        return ""

    # Ensure response_data is a string
    if isinstance(response_data, str):
        # Clean the response data
        response_data = response_data.replace("```json", "").replace("```", "").replace("\\\\", "")
    return clean_json(response_data)

def handle_content_filtering(response_data: str) -> Optional[Dict[str, Any]]:
    """
    Checks for content filtering errors in the response data.
    """
    error_code = re.search(r"Error code: (\d+)", response_data)
    content_filter_result = re.search(r"'content_filter_result': ({.*?})", response_data)

    if error_code and content_filter_result:
        Fallback = FALLBACK_RESPONSE.copy()
        Fallback["Response"] = ErrorMessage.Fallback_Content_Filter
        return Fallback
    return None

# def store_chat_context(Rediskey, chat_context, agent_name):
#     """
#     Stores the chat context and sly_data in the redis.
#     """
#     # logger.info(f"chat context: {chat_context}\n{type(chat_context)}")
#     # logger.info(f"sly_data: {sly_data}\n{type(sly_data)}")
#
#     if isinstance(chat_context, dict) and "chat_histories" in chat_context:
#         # Initialize a dictionary to hold split data
#         # split_data = {}
#
#         # Iterate through chat_histories
#         for chat in chat_context.get("chat_histories", None):
#             chat["messages"] = [
#                 message for message in chat.get("messages", [])
#                 if message.get("type") != "SYSTEM"
#             ]
#         chat_context["AgentName"] = agent_name
#
#     print(f"chat_context after processing: {chat_context}\n{type(chat_context)}")
#     set_redis_hashmap(Rediskey, None, chat_context)