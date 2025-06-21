import os
import bleach
import aiohttp
import requests
import logging
import json
from botcommonlib.utilities.config import CabAPIConfig
from dotenv import load_dotenv


load_dotenv()


class CabAPI:
    """
    CabAPI for managing cab booking requests in Cognizant's OneCognizant intranet.
    """
    def __init__(self):
        """
        Constructs a CabAPI for managing cab booking requests.
        """
        self.is_configured = True
        self.BASE_URL = CabAPIConfig.CAB_BASE_URL
        self.TOKEN_URL = CabAPIConfig.CAB_TOKEN_URL
        self.CAB_CLIENT_ID = CabAPIConfig.CAB_CLIENT_ID
        self.CAB_CLIENT_SECRET = CabAPIConfig.CAB_CLIENT_SECRET
        self.logger = logging.getLogger(self.__class__.__name__)

    async def get_access_token(self,associate_id):
        """
        Get the access token.
        URL: /token
        @param client_id: The API client ID.
        @param client_secret: The API client secret.
        @return: An access token.
        """
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'AssociateID':associate_id
        }
        # url = f"{self.BASE_URL}/token"
        data = {
            'client_id': self.CAB_CLIENT_ID,
            'client_secret': self.CAB_CLIENT_SECRET,
            'grant_type': 'client_credentials'
        }
        try:
            # sync
            # response = requests.post(self.TOKEN_URL, headers=headers, data=data, verify=False)
            # response.raise_for_status()  # Raise an error for bad responses
            # response_data = response.json()
            
            # async
            async with aiohttp.ClientSession() as session:
                async with session.post(self.TOKEN_URL, headers=headers, data=data, ssl=False) as response:
                    response.raise_for_status()  # Raise an error for bad responses
                    response_data = await response.json()  # Await the response.json() call
            
            access_token = response_data.get('access_token')
           
            if access_token:
                self.logger.debug("CabAPI access token retrieved successfully.")
                return access_token
            else:
                self.logger.warning("CabAPI access token is not available or invalid.")
                raise Exception("Access token is not available or invalid.")
        except Exception as e:
            self.logger.error("Failed Exception CabAPI Token: %s", str(e))
            raise Exception(f"Failed Exception CabAPI Token: {str(e)}")
        except aiohttp.ClientError as e:
            self.logger.error("Failed ClientError CabAPI token: %s", str(e))
            raise Exception(f"Failed ClientError CabAPI token: {str(e)}")
        # Sync Exceptions
        # except requests.exceptions.RequestException as e:
        #     self.logger.error("Failed RequestException CabAPI Token: %s", str(e))
        #     raise Exception(f"Failed RequestException CabAPI Token: {str(e)}")
        # except requests.exceptions.JSONDecodeError as e:
        #     self.logger.error("Failed JSONDecodeError CabAPI Token: %s", str(e))
        #     raise Exception(f"Failed JSONDecodeError CabAPI Token: {str(e)}")

    def cancel_cab_request(self, associate_id, booking_id):
        """
        Cancel a cab booking request.
        URL: /CancelCabRequestforAi
        @param associate_id: The associate ID.
        @param booking_id: The cab booking ID to cancel.
        @return: JSON response from the API.
        """
        access_token = self.get_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'SourceType': 'Web'
        }
        url = f"{self.BASE_URL}/CancelCabRequestforAi"
        payload = {
            "AssociateID": associate_id,
            "VehicleTripId": booking_id
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, verify=False)
            response.raise_for_status()  # Raise an error for bad responses
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error("Failed CancelCabRequestforAi request: %s", str(e))
            raise Exception(f"Failed CancelCabRequestforAi request: {response.status} - {response.text if response else 'N/A'}")

    async def get_cab_booking_details(self, request_json,sly_data):
        """
        Get cab booking details for the current day.
        URL: /GetCabBookingOfCurrentDay
        @param request_json: The request payload.
        @return: JSON response with cab booking details.
        """
        associate_id=sly_data.get('associate_id')
        access_token = await self.get_access_token(associate_id)
        headers = {
            'Authorization': f'Bearer {access_token}',
            'SourceType': 'Web'
        }
        url = f"{self.BASE_URL}/GetCabBookingOfCurrentDay"
        
        try:
            # sync
            # response = requests.post(url, headers=headers, json=request_json, verify=False)
            # response.raise_for_status()  # Raise an error for bad responses
            # response_data = response.json()

            # async
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=request_json, ssl=False) as response:
                    response.raise_for_status()  # Raise an error for bad responses
                    response_data = await response.json()  # Await the response.json() call
                    # self.logger.debug("GetCabBookingOfCurrentDay request successful.")
                    return response_data

            return response_data
        except Exception as e:
            self.logger.error("Failed Exception GetCabBookingOfCurrentDay: %s", str(e))
            raise Exception(f"Failed Exception GetCabBookingOfCurrentDay: {str(e)}")
        except aiohttp.ClientError as e:
            self.logger.error("Failed ClientError GetCabBookingOfCurrentDay request: %s", str(e))
            raise Exception(f"Failed ClientError GetCabBookingOfCurrentDay request: {str(e)}")
        # Sync Exceptions
        # except requests.exceptions.RequestException as e:
        #     self.logger.error("Failed RequestException GetCabBookingOfCurrentDay request: %s", str(e))
        #     raise Exception(f"Failed RequestException GetCabBookingOfCurrentDay request: {str(e)}")
# # Example usage:
# if __name__ == "__main__":

#     cab_api = CabAPI()
#     associate_id = bleach.clean( input("Enter associate ID: "))
#     # # Cancel a cab booking
#     # try:
#     #     cancel_response = cab_api.cancel_cab_request(client_id, client_secret, associate_id, booking_id)
#     #     print("Cancel Response:", cancel_response)
#     # except Exception as e:
#     #     print(e)

#     # Get cab booking details
#     try:
#         booking_details = cab_api.get_cab_booking_details({"AssociateID": associate_id})
#         print("get_cab_booking_details Details:", booking_details)
#     except Exception as e:
#         print("Error in get_cab_booking_details:", e)