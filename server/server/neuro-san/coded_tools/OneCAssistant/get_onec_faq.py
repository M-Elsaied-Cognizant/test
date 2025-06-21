import asyncio
import bleach
import json
from typing import Any
from typing import Dict
from typing import Union
import os
from neuro_san.interfaces.coded_tool import CodedTool
from botcommonlib.utilities.config import ErrorMessage
from coded_tools.application_api.onec_faq import OneCFAQ
from botcommonlib.utilities.utils import AdaptiveCard
import time
import logging

MOCK_RESPONSE = {
    "answer": [
        {
            "intent_id": "101", 
            "is_fallback": "no", 
            "response": {
                "actions": [], 
                "body": [
                    {
                        "text": "This is MOCK Response", 
                        "type": "TextBlock", 
                        "wrap": True
                    }
                ], 
                "type": "AdaptiveCard", 
                "version": "1.5"
            }, 
            "response_type": "simple"
        }
    ], 
    "feedback": True, 
    "msg": "Successfully fetched the response", 
    "session_id": "1111111111-0000000000", 
    "status": True
}

class GetOneCFAQTool(CodedTool):
    """
    CodedTool implementation to get the answer for Cognizant Enterprise related queries.
    """
    
    def __init__(self):
        self.onec_faq = OneCFAQ()
        self.AdaptiveCard = AdaptiveCard()

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        :param args: An argument dictionary whose keys are the parameters
                to the coded tool and whose values are the values passed for them
                by the calling agent. This dictionary is to be treated as read-only.

        :param sly_data: A dictionary whose keys are defined by the agent hierarchy,
                but whose values are meant to be kept out of the chat stream.

        :return:
            In case of successful execution:
                A dictionary with response to the FAQ details.
            otherwise:
                a text string an error message in the format:
                "Error: <error message>"
        """
        logger = logging.getLogger(self.__class__.__name__)
        origin_str = args.get("origin_str", "")
        
        
        if isinstance(origin_str, str):
            # print("origin_str--", name_before_dot)
            sly_data["AgentName"]=origin_str
        else:
            print("origin_str is not a valid string")
        
        sly_data["Is_Autonomous_Agent"] = False  # Example value
        sly_data["Is_ChatContext_Required"] = False  # Example value
        sly_data["Is_SessionID_Required"] = False  # Example value
        sly_data["Agent_Generated_Session_ID"] = None  # Example value
        if self.onec_faq.is_configured:
            fallback = ErrorMessage.Fallback
            response_data = None  # Initialize response_data with a default value
            try:
                logger.debug("Fetching GetOneCFAQTool with args: %s", args)
                # Replacing with the sly_data to make sure the laptop pass generated should be to the person who logged in
                args["user_id"] = sly_data["associate_id"]
                start_time = time.time()
                onecfaq = await self.onec_faq.get_onec_faq(args, sly_data)
                logger.info(f"OneCFAQ Response: {onecfaq} {type(onecfaq)}")
                response_time = time.time() - start_time
                if isinstance(onecfaq, str):
                    onecfaq = json.loads(onecfaq)
                sly_data["ResponseSource"]=onecfaq.get('response_source','')
                sly_data["IntentId"] = onecfaq.get('IntentId','')
                logger.info("GetOneCFAQTool API response time: %.2f seconds", response_time)

                # Extract and parse the 'Response' field
                response_data = onecfaq.get('Response')
                if isinstance(response_data, str):
                    try:
                        response_data = json.loads(response_data)
                        # Ensure the parsed data is a list
                        # if isinstance(response_data, dict):
                        #     response_data = [response_data]
                    except json.JSONDecodeError as e:
                        logger.error("JSONDecodeError in 'Response': %s", str(e))
                        response_data = None
                # elif isinstance(response_data, dict):
                #     response_data = [response_data]
                # If already a list, keep as is
                logger.debug("OneCFAQ Modified Response: %s (%s)", response_data, type(response_data))
                logger.info("OneCFAQ ResponseType: %s", onecfaq.get("ResponseType"))
                sly_data["Response"] = response_data
                if onecfaq.get("ResponseType") == "EDIT_FORM":
                    return onecfaq.get('Description')
                # elif onecfaq.get("ResponseType") == "VIEW_FORM":
                else:
                    result, result_str = self.AdaptiveCard.extract_data_from_adaptive_card_data(response_data)
                    # logger.info("Extracted Adaptive Card Result: %s %s", result, type(result))
                    # logger.info("Extracted Adaptive Card Result_str: %s %s", result_str, type(result_str))
                    return result_str
                    # return onecfaq.get('Description')
                # else:
                #     return response_data
                    logger.debug(f"OneCFAQ Modified Response: {response_data} {type(onecfaq)}")
            except Exception as e:
                logger.error("Exception GetOneCFAQTool: %s", str(e))
                sly_data["IntentId"] = ""
                return fallback
        else:
            logger.warning("GetOneCFAQ is not configured. Using mock response")
            response_data = MOCK_RESPONSE  # Use mock response if not configured

        # return response_data

# if __name__ == "__main__":
#     get_onec_FAQ_tool = GetOneCFAQTool()
#     associate_id = bleach.clean(input("Enter associate id: "))
#     query = bleach.clean(input("Enter Query: "))
#     try:
#         onecfaq_response = asyncio.run(get_onec_FAQ_tool.async_invoke(args={"user_id":associate_id, "query":query}, sly_data={"associate_id":associate_id}))
#         print("GetOneCFAQTool Response: ", onecfaq_response)
#     except Exception as e:
#         print("Error in GetOneCFAQTool: ", {str(e)})