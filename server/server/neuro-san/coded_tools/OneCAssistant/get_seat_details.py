from typing import Any, Dict, Union
import os
import json
import logging
import bleach
from neuro_san.interfaces.coded_tool import CodedTool
from botcommonlib.utilities.config import ErrorMessage
from coded_tools.application_api.onec_fetch_seat_details import AssociateSeatDetailsManager
from botcommonlib.utilities.utils import get_intent_id
from botcommonlib.utilities.redisHelper import get_redis_item
import requests
import asyncio
import time

MOCK_RESPONSE = {
    'SeatDetails': {
        'Building': 'Tower A',
        'Floor': '5th Floor',
        'SeatNumber': 'A5-123',
        'Status': 'Occupied'
    },
    'Warning': 'Ensure to update your seat details if there are any changes.'
}

# Configure logger


class AssociateSeatDetailsTool(CodedTool):
    """
    CodedTool implementation which fetches the booked seat details of an associate.
    """

    def __init__(self):
        """
        Constructer to get the Booked  seat details of an associate.
        """
        self.seat_manager = AssociateSeatDetailsManager()

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
                    "associate_id": The associate ID for whom the seat details are to be fetched.

        :return:
            In case of successful execution:
                A dictionary containing the seat details.
            otherwise:
                A text string with an error message in the format:
                "Error: <error message>"
        """
        logger = logging.getLogger(self.__class__.__name__)
        args["LoggedinId"] = sly_data["associate_id"]
        logger.debug("Fetching AssociateSeatDetailsTool with args: %s", args)
        origin_str = args.get("origin_str", "")

        if isinstance(origin_str, str):
            # print("origin_str--", name_before_dot)
            sly_data["AgentName"]=origin_str
        else:
            print("origin_str is not a valid string")

        # sly_data["Is_Autonomous_Agent"] = False  # Example value
        # sly_data["Is_ChatContext_Required"] = False  # Example value
        # sly_data["Is_SessionID_Required"] = False  # Example value
        # sly_data["Agent_Generated_Session_ID"] = None  # Example value

        if self.seat_manager.is_configured:
            fallback = ErrorMessage.Fallback
            try:
                # IntentId = get_intent_id("get_upcomingtripDetails")
                FuncDef = get_redis_item("AIAssistant_4139_T_get_upcomingtripDetails")
                FuncDef = json.loads(FuncDef)
                IntentId = str(FuncDef[0].get('IntentID', 'NA'))
                ResponseType = FuncDef[0].get('ResponseType')
                sly_data["IntentId"] = IntentId
                start_time = time.time()
                seat_details = await self.seat_manager.fetch_associate_seat_details(args, sly_data)
                response_time = time.time() - start_time
                logger.info(f"AssociateSeatDetailsTool Response: {seat_details} {type(seat_details)}")
                logger.info("AssociateSeatDetailsTool API response time: %.2f seconds", response_time)

                if not seat_details:
                    return fallback

                sly_data["Response"] = seat_details
                logger.info("Returning AssociateSeatDetails Description: %s", FuncDef[0].get('Description'))
                return FuncDef[0].get('Description')

                # final_response = {
                #     "Response": seat_details,
                #     "IntentId": IntentId
                # }
                # return seat_details

            except Exception as e:
                logger.error("Exception AssociateSeatDetailsTool: %s", str(e))
                sly_data["IntentId"] = ""
                return fallback
        else:
            logger.warning("AssociateSeatDetailsTool is not configured. Using mock response.")
            seat_details = MOCK_RESPONSE

    
# if __name__ == "__main__":
#     associate_id = bleach.clean(input("Enter associate ID: "))
#     try:
#         get_seat_details_tool = AssociateSeatDetailsTool()
#         response = asyncio.run(get_seat_details_tool.async_invoke(args={"LoggedinId": associate_id}, sly_data={"associate_id": associate_id}))
#         print("AssociateSeatDetailsTool Response: ", response)
#     except Exception as e:
#         print("Error in AssociateSeatDetailsTool: ", str(e))