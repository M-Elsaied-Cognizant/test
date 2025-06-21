import logging
import aiohttp
from botcommonlib.utilities.config import TransactionOneTransportCabOTPConfig, TransactionOneTransportIGSQRCodeConfig, TransactionPortfolioAPICredentialsConfig
from dotenv import load_dotenv

load_dotenv()

class OneCOneTransportAPI:
    """
    Manager for fetching Cab OTP and IGS QR Code details from the OneC OneTransport API.
    """
    def __init__(self):
        """
        Constructs an OneCOneTransportAPI instance.
        """
        self.is_configured = True
        self.Transaction_OneTransport_988_CabOTP_TokenAPI_URL = TransactionOneTransportCabOTPConfig.Transaction_OneTransport_988_CabOTP_TokenAPI_URL
        self.Transaction_OneTransport_988_CabOTP_BaseAPI_URL = TransactionOneTransportCabOTPConfig.Transaction_OneTransport_988_CabOTP_BaseAPI_URL
        self.Transaction_OneTransport_988_IGSQRCode_TokenAPI_URL = TransactionOneTransportIGSQRCodeConfig.Transaction_OneTransport_988_IGSQRCode_TokenAPI_URL
        self.Transaction_OneTransport_988_IGSQRCode_BaseAPI_URL = TransactionOneTransportIGSQRCodeConfig.Transaction_OneTransport_988_IGSQRCode_BaseAPI_URL
        self.Transaction_Portfolio_CSIT_ClientId = TransactionPortfolioAPICredentialsConfig.Transaction_Portfolio_CSIT_ClientId
        self.Transaction_Portfolio_CSIT_ClientSecret = TransactionPortfolioAPICredentialsConfig.Transaction_Portfolio_CSIT_ClientSecret
        self.logger = logging.getLogger(self.__class__.__name__)

    async def cab_otp_get_access_token(self, associate_id):
        """
        Fetches an access token for the One transport cab otp API.

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
            'client_id': self.Transaction_Portfolio_CSIT_ClientId,  # Sensitive data, do not log
            'client_secret': self.Transaction_Portfolio_CSIT_ClientSecret,  # Sensitive data, do not log
            'grant_type': 'client_credentials'
        }
       
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.Transaction_OneTransport_988_CabOTP_TokenAPI_URL,
                    headers=request_headers,
                    data=request_payload,
                    ssl=False
                ) as response:
                    response.raise_for_status()
                    response_data = await response.json()

            access_token = response_data.get('access_token')
            if access_token:
                self.logger.info("view cab otp access token successfully retrieved. | Last4Char_Tkn: %s", access_token[-4:])
                return access_token
            else:
                self.logger.warning("view cab otp access token is not available or invalid.")
                raise Exception("view cab otp access token is not available or invalid.")

        except aiohttp.ClientError as e:
            # Log the specific aiohttp.ClientError
            self.logger.error(f"Failed ClientError view cab otp get_access_token: {str(e)}")
            raise Exception(f"Failed ClientError view cab otp get_access_token: {str(e)}")    
        except Exception as e:
            # Log a generic error message for all other exceptions
            self.logger.error(f"Failed Exception view cab otp get_access_token: {str(e)}")
            raise Exception(f"Failed Exception view cab otp get_access_token: {str(e)}")

    async def fetch_cab_otp(self, request_json, sly_data):
        """
        Fetch OTP for cab booking.

        Args:
            request_json (Dict[str, Any]): The request payload.
            sly_data (Dict[str, str]): Additional data containing associate_id.

        Returns:
            Dict[str, Any]: JSON response from the API.
        """
        
        self.logger.info("Initiating fetch_cab_otp with args: %s | sly_data: %s | Token URL: %s | Base URL: %s | Last4Char_CId: %s | Last4Char_CSec: %s", 
                         request_json, sly_data, self.Transaction_OneTransport_988_CabOTP_TokenAPI_URL, self.Transaction_OneTransport_988_CabOTP_BaseAPI_URL,
                         self.Transaction_Portfolio_CSIT_ClientId[-4:], self.Transaction_Portfolio_CSIT_ClientSecret[-4:])

        access_token = await self.cab_otp_get_access_token(sly_data.get("associate_id"))

        request_headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'SourceType': 'Web'
        }
        
        try:       
            self.logger.info("Sending request to GetCabAllocationDetailsAndOTPForAI: %s", self.Transaction_OneTransport_988_CabOTP_BaseAPI_URL)

            # Remove 'origin','origin_str' and 'query from request_json
            request_json.pop('origin', None)
            request_json.pop('origin_str', None)
            request_json.pop('query', None)

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.Transaction_OneTransport_988_CabOTP_BaseAPI_URL,
                    headers=request_headers,
                    json=request_json,
                    ssl=False
                ) as response:
                    response.raise_for_status()
                    response_data = await response.text()
            return response_data
        
        except aiohttp.ClientError as e:
            # Log the specific aiohttp.ClientError
            self.logger.error(f"ClientError in fetch_cab_otp. | Exception: {str(e)} | Payload: {request_json} | URL: {self.Transaction_OneTransport_988_CabOTP_BaseAPI_URL}")
            raise Exception(f"ClientError in fetch_cab_otp. | Exception: {str(e)} | Payload: {request_json} | URL: {self.Transaction_OneTransport_988_CabOTP_BaseAPI_URL}")
        except Exception as e:
            # Log a generic error message for all other exceptions
            self.logger.error(f"Exception in fetch_cab_otp. | Exception: {str(e)} | Payload: {request_json} | URL: {self.Transaction_OneTransport_988_CabOTP_BaseAPI_URL}")
            raise Exception(f"Exception in fetch_cab_otp. | Exception: {str(e)} | Payload: {request_json} | URL: {self.Transaction_OneTransport_988_CabOTP_BaseAPI_URL}")
        
    async def igs_qr_code_get_access_token(self, associate_id):
        """
        Fetches an access token for the One transport igs_qr_code API.

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
            'client_id': self.Transaction_Portfolio_CSIT_ClientId,  # Sensitive data, do not log
            'client_secret': self.Transaction_Portfolio_CSIT_ClientSecret,  # Sensitive data, do not log
            'grant_type': 'client_credentials'
        }
       
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.Transaction_OneTransport_988_IGSQRCode_TokenAPI_URL,
                    headers=request_headers,
                    data=request_payload,
                    ssl=False
                ) as response:
                    response.raise_for_status()
                    response_data = await response.json()

            access_token = response_data.get('access_token')
            if access_token:
                self.logger.info("view IGS QR Code access token successfully retrieved. | Last4Char_Tkn: %s", access_token[-4:])
                return access_token
            else:
                self.logger.warning("view IGS QR Code access token is not available or invalid.")
                raise Exception("view IGS QR Code access token is not available or invalid.")

        except aiohttp.ClientError as e:
            # Log the specific aiohttp.ClientError
            self.logger.error(f"Failed ClientError view IGS QR Code get_access_token: {str(e)}")
            raise Exception(f"Failed ClientError view IGS QR Code get_access_token: {str(e)}")    
        except Exception as e:
            # Log a generic error message for all other exceptions
            self.logger.error(f"Failed Exception view IGS QR Code get_access_token: {str(e)}")
            raise Exception(f"Failed Exception view IGS QR Code get_access_token: {str(e)}")

    async def fetch_igs_qr_code(self, request_json, sly_data):
        """
        Fetch QR Code for IGS/Inter Gate Shuttel.

        Args:
            request_json (Dict[str, Any]): The request payload.
            sly_data (Dict[str, str]): Additional data containing associate_id.

        Returns:
            Dict[str, Any]: JSON response from the API.
        """
        
        self.logger.info("Initiating fetch_igs_qr_code with args: %s | sly_data: %s | Token URL: %s | Base URL: %s | Last4Char_CId: %s | Last4Char_CSec: %s", 
                         request_json, sly_data, self.Transaction_OneTransport_988_IGSQRCode_TokenAPI_URL, self.Transaction_OneTransport_988_IGSQRCode_BaseAPI_URL,
                         self.Transaction_Portfolio_CSIT_ClientId[-4:], self.Transaction_Portfolio_CSIT_ClientSecret[-4:])

        access_token = await self.igs_qr_code_get_access_token(sly_data.get("associate_id"))

        request_headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'SourceType': 'Web'
        }
        
        try:       
            self.logger.info("Sending request to ShowIGSQRCodeforAI: %s", self.Transaction_OneTransport_988_IGSQRCode_BaseAPI_URL)

            # Remove 'origin', 'origin_str' and 'query from request_json
            request_json.pop('origin', None)
            request_json.pop('origin_str', None)
            request_json.pop('query', None)

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.Transaction_OneTransport_988_IGSQRCode_BaseAPI_URL,
                    headers=request_headers,
                    json=request_json,
                    ssl=False
                ) as response:
                    response.raise_for_status()
                    response_data = await response.text()
            return response_data
        
        except aiohttp.ClientError as e:
            # Log the specific aiohttp.ClientError
            self.logger.error(f"ClientError in fetch_igs_qr_code | Exception: {str(e)} | Payload: {request_json} | URL: {self.Transaction_OneTransport_988_IGSQRCode_BaseAPI_URL}")
            raise Exception(f"ClientError in fetch_igs_qr_code | Exception: {str(e)} | Payload: {request_json} | URL: {self.Transaction_OneTransport_988_IGSQRCode_BaseAPI_URL}")
        except Exception as e:
            # Log a generic error message for all other exceptions
            self.logger.error(f"Exception in fetch_igs_qr_code | Exception: {str(e)} | Payload: {request_json} | URL: {self.Transaction_OneTransport_988_IGSQRCode_BaseAPI_URL}")
            raise Exception(f"Exception in fetch_igs_qr_code | Exception: {str(e)} | Payload: {request_json} | URL: {self.Transaction_OneTransport_988_IGSQRCode_BaseAPI_URL}")
    