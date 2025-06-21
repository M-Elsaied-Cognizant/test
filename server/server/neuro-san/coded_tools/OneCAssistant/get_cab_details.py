from typing import Any, Dict, Union
import logging
import json
import bleach
from neuro_san.interfaces.coded_tool import CodedTool
from coded_tools.application_api.onec_fetch_cab_details import CabAPI
from botcommonlib.utilities.utils import get_intent_id
from botcommonlib.utilities.redisHelper import get_redis_item
from botcommonlib.utilities.config import ErrorMessage
from botcommonlib.utilities.utils import AdaptiveCard
import requests
import asyncio
import time

MOCK_RESPONSE = {
    'BookingDetails': [
        {
            'BookingID': '12345',
            'PickupLocation': 'Tower A',
            'DropLocation': 'Tower B',
            'PickupTime': '2023-10-01T08:00:00',
            'Status': 'Confirmed'
        },
        {
            'BookingID': '67890',
            'PickupLocation': 'Tower C',
            'DropLocation': 'Tower D',
            'PickupTime': '2023-10-01T18:00:00',
            'Status': 'Completed'
        }
    ],
    'Warning': 'Ensure to cancel your cab booking in advance if not required.'
}

# Configure logger

class CabBookingDetailsTool(CodedTool):
    """
    CodedTool implementation which fetches booked cab  details of an associate.
    """

    def __init__(self):
        """
        Constructs a Cab Booking Details Tool for Cognizant's OneCognizant intranet.
        """
        self.cab_api = CabAPI()

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
                    "associate_id": The associate ID for whom the cab booking details are to be fetched.

        :return:
            In case of successful execution:
                A dictionary containing the cab booking details.
            otherwise:
                A text string with an error message in the format:
                "Error: <error message>"
        """
        logger = logging.getLogger(self.__class__.__name__)
        args["AssociateID"] = sly_data["associate_id"]
        logger.debug("Fetching CabBookingDetailsTool with args: %s", args)
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

        if self.cab_api.is_configured:
            fallback = ErrorMessage.Fallback
            try:
                # IntentId = get_intent_id("get_upcomingtripDetails")
                FuncDef = get_redis_item(f"AIAssistant_4139_T_get_upcomingtripDetails")
                FuncDef = json.loads(FuncDef)
                IntentId = str(FuncDef[0].get('IntentID', 'NA'))
                ResponseType = FuncDef[0].get('ResponseType')
                # print("IntentId-----", IntentId)
                sly_data["IntentId"] = IntentId
                start_time = time.time()
                booking_details = await self.cab_api.get_cab_booking_details(args,sly_data)
                response_time = time.time() - start_time
                logger.info(f"CabBookingDetailsTool API response: {booking_details} {type(booking_details)}")
                logger.info("CabBookingDetailsTool API response time: %.2f seconds", response_time)
                if not booking_details:
                    return fallback
                sly_data["Response"] = booking_details
                logger.info("Returning CabBookingDetailsTool Description: %s", FuncDef[0].get('Description'))
                return FuncDef[0].get('Description')

                # final_response = {
                #     "Response": booking_details,
                #     "IntentId": IntentId
                # }
                # return booking_details

            except Exception as e:
                logger.error("Exception CabBookingDetailsTool: %s", str(e))
                sly_data["IntentId"] = ""
                return fallback
        else:
            logger.warning("CabAPI is not configured. Using mock response.")
            booking_details = MOCK_RESPONSE



# if __name__ == "__main__":
#     associate_id = bleach.clean(input("Enter associate ID: "))
#     get_cab_details_tool = CabBookingDetailsTool()
#     try:
#         booking_details = asyncio.run(get_cab_details_tool.async_invoke(args={"AssociateID":associate_id}, sly_data={"associate_id":associate_id}))
#         print("CabBookingDetailsTool Response: ", booking_details)
#     except Exception as e:
#         print("Error in CabBookingDetailsTool: ", str(e))