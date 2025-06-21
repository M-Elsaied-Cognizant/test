from typing import Any
from typing import Dict
from typing import Union
import os
import time
from neuro_san.interfaces.coded_tool import CodedTool
from coded_tools.application_api.pla_api import PersonalizedLearningAssistantAPI
import logging
from botcommonlib.utilities.config import ErrorMessage

MOCK_RESPONSE = {
    "associateId": "123456",
    "plaAPI": {
        "associateId": "123456",
        "associateName": "John Doe"
    }
}
class PLATool(CodedTool):
    """
    CodedTool implementation which gets the personalized learning assistant for a user.
    """
    
    def __init__(self):
        self.pla_api = PersonalizedLearningAssistantAPI()

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        :param args: An argument dictionary whose keys are the parameters
                to the coded tool and whose values are the values passed for them
                by the calling agent. This dictionary is to be treated as read-only.

                
        :param sly_data: A dictionary whose keys are defined by the agent hierarchy,
                but whose values are meant to be kept out of the chat stream.

                This dictionary is largely to be treated as read-only.
                It is possible to add key/value pairs to this dict that do not
                yet exist as a bulletin board, as long as the responsibility
                for which coded_tool publishes new entries is well understood
                by the agent chain implementation and the coded_tool implementation
                adding the data is not invoke()-ed more than once.

                Keys expected for this implementation are:
                    None

        :return:
            In case of successful execution:
                A dictionary with personalized learning assistant details.
            otherwise:
                a text string an error message in the format:
                "Error: <error message>"
        """
            
        # print(">>>>>>>>>>>>>>>>>>> Getting Personalized Learning Assistant >>>>>>>>>>>>>>>>>>")
        logger = logging.getLogger(self.__class__.__name__)
        try:
            fallback = ErrorMessage.Fallback
            if self.pla_api.is_configured:
                
                origin_str = args.get("origin_str", "")
                
                if isinstance(origin_str, str):
                    # print("origin_str--", name_before_dot)
                    sly_data["AgentName"]=origin_str
                else:
                    print("origin_str is not a valid string")
                        
                sly_data["Is_Autonomous_Agent"] = True  # Example value
                sly_data["Is_ChatContext_Required"] = False  # Example value
                sly_data["Is_SessionID_Required"] = False  # Example value
                sly_data["Agent_Generated_Session_ID"] = None  # Example value
                associate_id = sly_data["associate_id"]
                
               
                
                
                query = args.get("query", "need-query")
                sly_data["IntentId"] = "NA"
                
                start_time = time.time()
                pla_api = await self.pla_api.ask_query(query,associate_id)
                logger.info(f"PLA Response: {pla_api} {type(pla_api)}")
                end_time = time.time()
                response_time = end_time - start_time
                logger.info("PLATool API response time: %.2f seconds", response_time)
            
                # print("Personalized Learning Assistant:", pla_api)
                # print(">>>>>>>>>>>>>>>>>>>DONE !!!>>>>>>>>>>>>>>>>>>")
                return pla_api
            else:
                print("WARNING: Personalized Learning Assistant is not configured. Using mock response")
                return MOCK_RESPONSE
        except Exception as e:
            return fallback


