from typing import Any, Dict, Union
import logging
from neuro_san.interfaces.coded_tool import CodedTool
from botcommonlib.utilities.config import ErrorMessage
from coded_tools.application_api.onec_quickso_api import OneCQuickSOAPI
from botcommonlib.utilities.utils import get_intent_id
import time
import json
import bleach
import asyncio

ERROR_RESPONSE = json.loads("""
{
    "type": "AdaptiveCard",
    "$schema": "https://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.5",
    "body": [
        {
            "type": "TextBlock",
            "text": "We are currently experiencing technical difficulties in retrieving the SO status. Please try again later.",
            "wrap": true,
            "weight": "Bolder"
        }
    ]
}
""")

class ViewSOStatusAgent(CodedTool):
    """
    CodedTool implementation which fetches the SO status.
    """

    def __init__(self):
        """
        Constructer to get the SO status.
        """
        self.onec_quickso_api = OneCQuickSOAPI()

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        logger = logging.getLogger(self.__class__.__name__)
        try:            
            args["AssociateID"] = sly_data["associate_id"]
            logger.info("Initiated view_so_status_agent with args: %s", args)

            origin_str = args.get("origin_str", "")
            if isinstance(origin_str, str):
                sly_data["AgentName"] = origin_str
            else:
                logger.error("origin_str is not a valid string: %s", origin_str)

            if self.onec_quickso_api.is_configured:
                try:
                    sly_data["IntentId"] = get_intent_id("GetQuickSOStatusofSOId")
                    start_time = time.time()
                    so_status = await self.onec_quickso_api.fetch_so_status(args, sly_data)
                    response_time = time.time() - start_time
                    logger.info(f"ViewSOStatusAgent API response: {so_status} {type(so_status)}")
                    logger.info("ViewSOStatusAgent API response time: %.2f seconds", response_time)

                    if not so_status:   
                        logger.error("Empty response from ViewSOStatusAgent API")
                        return ErrorMessage.Fallback
                except Exception as e:
                    logger.error("Exception in ViewSOStatusAgent: %s", str(e))
                    sly_data["IntentId"] = ""
                    return ErrorMessage.Fallback
            else:
                logger.error("OneCQuickSOAPI is not configured. Using mock response.")
                so_status = ERROR_RESPONSE

            return so_status
        except Exception as e:
            logger.error("Unexpected error in ViewSOStatusAgent async_invoke: %s", str(e))
            return ErrorMessage.Fallback
        
# if __name__ == "__main__":
#     associate_id = bleach.clean(input("171545"))
#     try:
#         so_status = ViewSOStatusAgent()
#         response = asyncio.run(so_status.async_invoke(args={"LoggedinId": associate_id}, sly_data={"associate_id": associate_id}))
#         print("ViewSOStatusAgent Response: ", response)
#     except Exception as e:
#         print("Error in ViewSOStatusAgent: ", str(e))
