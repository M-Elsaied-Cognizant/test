from typing import Any, Dict, Union
import logging
import bleach
from neuro_san.interfaces.coded_tool import CodedTool
# from coded_tools.application_api.onec_fetch_cab_details import CabAPI
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
            "text": "We are currently experiencing technical difficulties in retrieving the otp details for cab booking. Please try again later.",
            "wrap": true,
            "weight": "Bolder"
        }
    ]
}
""")

# Configure logger

class CabBookingDetailsAndOtpTool(CodedTool):
    """
    CodedTool implementation which fetches booked cab details and otp of an associate.
    """

    def __init__(self):
        """
        Constructs a OTP details for Cab Booking Tool for Cognizant's OneCognizant intranet.
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
                    "associate_id": The associate ID for whom the OTP details for Cab Booking are to be fetched.

        :return:
            In case of successful execution:
                A dictionary containing the OTP details for Cab Booking.
            otherwise:
                A text string with an error message in the format:
                "Error: <error message>"
        """
        logger = logging.getLogger(self.__class__.__name__)
        try:
            args["AssociateID"] = sly_data["associate_id"]
            logger.debug("Fetching GetCabAllocationDetailsAndOTPForAI with args: %s", args)
            origin_str = args.get("origin_str", "")


            if isinstance(origin_str, str):
                sly_data["AgentName"]=origin_str
            else:
                logger.error("origin_str is not a valid string: %s", origin_str)

            if self.onetransport_api.is_configured:
                fallback = ErrorMessage.Fallback
                try:
                    IntentId = get_intent_id("get_cabdetailsAndOtpForAi")
                    sly_data["IntentId"] = IntentId
                    start_time = time.time()
                    booking_details_and_otp = await self.onetransport_api.fetch_cab_otp(args,sly_data)
                    response_time = time.time() - start_time
                    logger.info(f"GetCabAllocationDetailsAndOTPForAI API response: {booking_details_and_otp} {type(booking_details_and_otp)}")
                    logger.info("GetCabAllocationDetailsAndOTPForAI API response time: %.2f seconds", response_time)
                    if not booking_details_and_otp:
                        logger.error("Error: Empty response from GetCabAllocationDetailsAndOTPForAI API")
                        return fallback
                except Exception as e:
                    logger.error("Exception GetCabAllocationDetailsAndOTPForAI: %s", str(e))
                    sly_data["IntentId"] = ""
                    return fallback
            else:
                logger.warning("OneCOneTransportAPI is not configured. Using mock response.")
                booking_details_and_otp = ERROR_RESPONSE

            return booking_details_and_otp
        except Exception as e:
            logger.error("Unexpected error in CabBookingDetailsAndOtpTool async_invoke: %s", str(e))
            return ErrorMessage.Fallback
