import os
import bleach
import requests
import logging
import aiohttp
from botcommonlib.utilities.config import FlexiSeatAPIConfig
from dotenv import load_dotenv

load_dotenv()

class AssociateSeatDetailsManager:
    """
    Manager for fetching associate seat details from Cognizant's API.
    """
    def __init__(self):
        """
        Constructs an AssociateSeatDetailsManager.
        """
        self.is_configured = True
        self.BASE_URL = FlexiSeatAPIConfig.FLEXI_SEAT_BASE_URL
        self.FLEXISEAT_CLIENT_ID = FlexiSeatAPIConfig.FLEXISEAT_CLIENT_ID
        self.FLEXISEAT_CLIENT_SECRET = FlexiSeatAPIConfig.FLEXISEAT_CLIENT_SECRET
        self.logger = logging.getLogger(self.__class__.__name__)

    async def get_access_token(self, associate_id):
        """
        Get the access token.
        @param associate_id: The associate ID.
        @return: An access token.
        """
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'AssociateID': associate_id,
        }
        data = {
            'client_id': self.FLEXISEAT_CLIENT_ID,
            'client_secret': self.FLEXISEAT_CLIENT_SECRET,  # Sensitive data, do not log
            'grant_type': 'client_credentials'
        }
       
        try:
            TOKEN_URL = f"{self.BASE_URL}/token"
            # sync
            # response = requests.post(TOKEN_URL, headers=headers, data=data, verify=False)
            # response.raise_for_status()  # Raise an error for bad responses
            # response_data = response.json()
            # async
            async with aiohttp.ClientSession() as session:
                async with session.post(TOKEN_URL, headers=headers, data=data, ssl=False) as response:
                    response.raise_for_status()  # Raise an error for bad responses
                    response_data = await response.json()  # Await the response.json() call

            access_token = response_data.get('access_token')
            if access_token:
                # Log only a generic message without sensitive data
                self.logger.debug("SeatAPI access token successfully retrieved.")
                return access_token
            else:
                self.logger.warning("SeatAPI access token is not available or invalid.")
                raise Exception("SeatAPI access token is not available or invalid.")

        except Exception as e:
            self.logger.error("Failed Exception AssociateSeatDetailsManager Token: %s", str(e))
            raise Exception(f"Failed Exception AssociateSeatDetailsManager Token: {str(e)}")
        except aiohttp.ClientError as e:
            self.logger.error("Failed ClientError AssociateSeatDetailsManager token: %s", str(e))
            raise Exception(f"Failed ClientError AssociateSeatDetailsManager token: {str(e)}")
        # Sync Exceptions
        # except requests.exceptions.RequestException as e:
        #     self.logger.error("Failed RequestException AssociateSeatDetailsManager Token: %s", str(e))
        #     raise Exception(f"Failed RequestException AssociateSeatDetailsManager Token: {str(e)}")

    async def fetch_associate_seat_details(self, request_json, sly_data):
        """
        Fetch associate seat details.
        @param request_json: The request payload.
        @param sly_data: Additional data containing associate_id.
        @return: JSON response from the API.
        """
        access_token = await self.get_access_token(sly_data.get("associate_id"))
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'SourceType': 'Web'
        }
        payload = request_json
        
        try:
            SEAT_DETAILS_URL = f"{self.BASE_URL}/AIFetchAssociateSeatDetails"
            self.logger.debug("Sending request to fetch associate seat details.")
            # sync
            # response = requests.post(SEAT_DETAILS_URL, headers=headers, json=payload, verify=False)
            # response.raise_for_status()  # Raise an error for bad responses
            # response_data = response.json()

            # async
            async with aiohttp.ClientSession() as session:
                async with session.post(SEAT_DETAILS_URL, headers=headers, json=payload, ssl=False) as response:
                    response.raise_for_status()  # Raise an error for bad responses
                    response_data = await response.json()  # Await the response.json() call
                    # self.logger.debug("Successfully fetched associate seat details.")

            return response_data
        except Exception as e:
            # Log a generic error message
            self.logger.error("Failed Exception AIFetchAssociateSeatDetails: %s", str(e))
            raise Exception(f"Failed Exception AIFetchAssociateSeatDetails: {str(e)}")
        except aiohttp.ClientError as e:
            self.logger.error("Failed ClientError AIFetchAssociateSeatDetails request: %s", str(e))
            raise Exception(f"Failed ClientError AIFetchAssociateSeatDetails request: {str(e)}")
        # Sync Exceptions
        # except requests.exceptions.RequestException as e:
        #     self.logger.error("Failed RequestException AIFetchAssociateSeatDetails request: %s", str(e))
        #     raise Exception(f"Failed RequestException AIFetchAssociateSeatDetails request: {str(e)}")

# # Example usage:
# if __name__ == "__main__":
#     associate_id = bleach.clean(input("Enter associate ID: "))
#     try:
#         seat_manager = AssociateSeatDetailsManager()
#         seat_details = seat_manager.fetch_associate_seat_details({"LoggedinId": associate_id})
#         print("fetch_associate_seat_details Details: ", seat_details)
#     except Exception as e:
#         print("Error in fetch_associate_seat_details: ", e)