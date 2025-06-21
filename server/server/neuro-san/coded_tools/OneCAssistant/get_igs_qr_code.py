from typing import Any, Dict, Union
import logging
import bleach
from neuro_san.interfaces.coded_tool import CodedTool
from coded_tools.application_api.onec_onetransport_api import OneCOneTransportAPI
from botcommonlib.utilities.utils import get_intent_id
from botcommonlib.utilities.config import ErrorMessage
import requests
import asyncio
import time
import json

ERROR_RESPONSE = json.loads("""
{
    "type": "AdaptiveCard",
    "$schema": "https://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.5",
    "body": [
        {
            "type": "TextBlock",
            "text": "We are currently experiencing technical difficulties in retrieving the QR Code for Inter Gate Shuttel. Please try again later.",
            "wrap": true,
            "weight": "Bolder"
        }
    ]
}
""")

class IGSQRCodeTool(CodedTool):
    """
    CodedTool implementation which fetches QR code for Inter Gate Shuttel of an associate.
    """

    def __init__(self):
        """
        Constructs a QR code for Inter Gate Shuttel Tool for Cognizant's OneCognizant intranet.
        """
        self.onetransport_api = OneCOneTransportAPI()

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        :param args: An argument dictionary whose keys are the parameters
                to the coded tool and whose values are the values passed for them
                by the calling agent. This dictionary is to be treated as read-only.

                The argument dictionary expects the following keys:
                    None

        :param sly_data: A dictionary whose keys are defined by the agent hierarchy,
                but whose values are meant to be kept out of the chat stream.

                This dictionary is largely to be treated as read-only.
                It is possible to add key/value pairs to this dict that do not
                yet exist as a bulletin board, as long as the responsibility
                for which coded_tool publishes new entries is well understood
                by the agent chain implementation and the coded_tool implementation
                adding the data is not invoke()-ed more than once.

                Keys expected for this implementation are:
                    "associate_id": The associate ID for whom the QR code for Inter Gate Shuttel are to be fetched.

        :return:
            In case of successful execution:
                A dictionary containing QR code for Inter Gate Shuttel.
            otherwise:
                A text string with an error message in the format:
                "Error: <error message>"
        """
        logger = logging.getLogger(self.__class__.__name__)
        try:
            args["AssociateID"] = sly_data["associate_id"]
            logger.debug("Fetching ShowIGSQRCodeforAI with args: %s", args)
            origin_str = args.get("origin_str", "")


            if isinstance(origin_str, str):
                sly_data["AgentName"]=origin_str
            else:
                logger.error("origin_str is not a valid string: %s", origin_str)

            if self.onetransport_api.is_configured:
                fallback = ErrorMessage.Fallback
                try:
                    IntentId = get_intent_id("get_IGSQRCodeforAi")
                    sly_data["IntentId"] = IntentId
                    start_time = time.time()
                    igs_qr_code = await self.onetransport_api.fetch_igs_qr_code(args,sly_data)
                    response_time = time.time() - start_time
                    logger.info(f"ShowIGSQRCodeforAI API response: {igs_qr_code} {type(igs_qr_code)}")
                    logger.info("ShowIGSQRCodeforAI API response time: %.2f seconds", response_time)
                    if not igs_qr_code:
                        logger.error("Error: Empty response from ShowIGSQRCodeforAI API")
                        return fallback
                except Exception as e:
                    logger.error("Exception ShowIGSQRCodeforAI: %s", str(e))
                    sly_data["IntentId"] = ""
                    return fallback
            else:
                logger.warning("OneCOneTransportAPI is not configured. Using mock response.")
                igs_qr_code = ERROR_RESPONSE

            final_response = {
                "Response": igs_qr_code,
                "IntentId": IntentId
            }
            return igs_qr_code
        except Exception as e:
            logger.error("Unexpected error in IGSQRCodeTool async_invoke: %s", str(e))
            return ErrorMessage.Fallback
