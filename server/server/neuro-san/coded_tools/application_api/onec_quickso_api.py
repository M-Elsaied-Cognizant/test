import logging
import aiohttp
from botcommonlib.utilities.config import TransactionPortfolioAPICredentialsConfig, TransactionQuickSOViewSOStatusConfig
from dotenv import load_dotenv

load_dotenv()

class OneCQuickSOAPI:
    """
    Manager for fetching So details from the OneC QuickSo API.
    """
    def __init__(self):
        """
        Constructs an OneCQuickSOAPI instance.
        """
        self.is_configured = True
        self.Transaction_QuickSO_428_SOStatus_TokenAPI_URL = TransactionQuickSOViewSOStatusConfig.Transaction_QuickSO_428_SOStatus_TokenAPI_URL
        self.Transaction_QuickSO_428_SOStatus_BaseAPI_URL = TransactionQuickSOViewSOStatusConfig.Transaction_QuickSO_428_SOStatus_BaseAPI_URL
        self.Transaction_Portfolio_Fulfilment_ClientId = TransactionPortfolioAPICredentialsConfig.Transaction_Portfolio_Fulfilment_ClientId
        self.Transaction_Portfolio_Fulfilment_ClientSecret = TransactionPortfolioAPICredentialsConfig.Transaction_Portfolio_Fulfilment_ClientSecret
        self.logger = logging.getLogger(self.__class__.__name__)

    async def get_access_token(self, associate_id):
        """
        Fetches an access token from the QuickSO API.

        Args:
            associate_id (str): The associate ID required for authentication.

        Returns:
            Optional[str]: The access token if successfully retrieved, otherwise None.

        Raises:
            aiohttp.ClientError: If there is an issue with the HTTP request.
            Exception: If the access token is missing or invalid.
        """
        # Define the request headers for the token request
        request_headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'AssociateID': associate_id,
        }
        # Define the request payload for the token request
        request_payload = {
            'client_id': self.Transaction_Portfolio_Fulfilment_ClientId,  # Sensitive data, do not log
            'client_secret': self.Transaction_Portfolio_Fulfilment_ClientSecret,  # Sensitive data, do not log
            'grant_type': 'client_credentials'
        }
       
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.Transaction_QuickSO_428_SOStatus_TokenAPI_URL,
                    headers=request_headers,
                    data=request_payload,
                    ssl=False
                ) as response:
                    response.raise_for_status()
                    response_data = await response.json()

            access_token = response_data.get('access_token')
            if access_token:
                self.logger.info("QuickSO View SO Status access token successfully retrieved. | Last4Char_Tkn: %s", access_token[-4:])
                return access_token
            else:
                self.logger.warning("QuickSO View SO Status access token is not available or invalid.")
                raise Exception("QuickSO View SO Status access token is not available or invalid.")

        except aiohttp.ClientError as e:
            # Log the specific aiohttp.ClientError
            self.logger.error(f"Failed ClientError OneCQuickSOAPI get_access_token: {str(e)}")
            raise Exception(f"Failed ClientError OneCQuickSOAPI get_access_token: {str(e)}")    
        except Exception as e:
            # Log a generic error message for all other exceptions
            self.logger.error(f"Failed Exception OneCQuickSOAPI get_access_token: {str(e)}")
            raise Exception(f"Failed Exception OneCQuickSOAPI get_access_token: {str(e)}")

    async def fetch_so_status(self, request_json, sly_data):
        """
        Fetch SO status from the OneC QuickSo API.

        Args:
            request_json (Dict[str, Any]): The request payload.
            sly_data (Dict[str, str]): Additional data containing associate_id.

        Returns:
            Dict[str, Any]: JSON response from the API.
        """
        
        self.logger.info("Initiating fetch_so_status with args: %s | sly_data: %s | Token URL: %s | Base URL: %s | Last4Char_CId: %s | Last4Char_CSec: %s", 
                         request_json, sly_data, self.Transaction_QuickSO_428_SOStatus_TokenAPI_URL, self.Transaction_QuickSO_428_SOStatus_BaseAPI_URL,
                         self.Transaction_Portfolio_Fulfilment_ClientId[-4:], self.Transaction_Portfolio_Fulfilment_ClientSecret[-4:])

        access_token = await self.get_access_token(sly_data.get("associate_id"))

        request_headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'SourceType': 'Web'
        }
        
        try:       
            self.logger.info("Sending request to GetQuickSOStatusofSOId: %s", self.Transaction_QuickSO_428_SOStatus_BaseAPI_URL)

            # Remove 'origin' and 'origin_str' from request_json
            request_json.pop('origin', None)
            request_json.pop('origin_str', None)

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.Transaction_QuickSO_428_SOStatus_BaseAPI_URL,
                    headers=request_headers,
                    json=request_json,
                    ssl=False
                ) as response:
                    response.raise_for_status()
                    response_data = await response.text()
            return response_data
        
        except aiohttp.ClientError as e:
            # Log the specific aiohttp.ClientError
            self.logger.error(f"ClientError in fetch_so_status. | Exception: {str(e)} | Payload: {request_json} | URL: {self.Transaction_QuickSO_428_SOStatus_BaseAPI_URL}")
            raise Exception(f"ClientError in fetch_so_status. | Exception: {str(e)} | Payload: {request_json} | URL: {self.Transaction_QuickSO_428_SOStatus_BaseAPI_URL}")
        except Exception as e:
            # Log a generic error message for all other exceptions
            self.logger.error(f"Exception in fetch_so_status. | Exception: {str(e)} | Payload: {request_json} | URL: {self.Transaction_QuickSO_428_SOStatus_BaseAPI_URL}")
            raise Exception(f"Exception in fetch_so_status. | Exception: {str(e)} | Payload: {request_json} | URL: {self.Transaction_QuickSO_428_SOStatus_BaseAPI_URL}")