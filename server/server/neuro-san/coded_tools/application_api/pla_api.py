
from botcommonlib.utilities.config import PLAConfig
import os
import logging
import aiohttp
from aiohttp import ClientError
from dotenv import load_dotenv

load_dotenv()


class PersonalizedLearningAssistantAPI:
    """
    Personalized Learning Assistant API for Cognizant's intranet.
    """

    def __init__(self):
        """
        Constructs a Personalized Learning Assistant API.
        """
        self.base_url = PLAConfig.PLA_BASE_URL
        self.token_url = PLAConfig.PLA_TOKEN_URL
        self.client_id = PLAConfig.PLA_CLIENT_ID
        self.client_secret = PLAConfig.PLA_CLIENT_SECRET
        self.is_configured = True
        self.logger = logging.getLogger(self.__class__.__name__)

    async def get_access_token(self):
        """
        Get the access token.
        @return: an access token
        """
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.token_url, headers=headers, data=data, ssl=False) as response:
                    response.raise_for_status()
                    token_response = await response.json()
                    access_token = token_response.get('access_token')
                    if not access_token:
                        self.logger.error("Access token not found in the response.")
                        raise ValueError("Access token not found in the response.")
                    self.logger.debug("Access token retrieved successfully.")
                    return access_token
        except Exception as ex:
            self.logger.error("Failed to fetch access token: %s", str(ex))
            raise Exception(f"Failed to fetch access token: {str(ex)}")
        except ClientError as ex:
            self.logger.error("ClientError while fetching access token: %s", str(ex))
            raise Exception(f"ClientError while fetching access token: {str(ex)}")

    async def ask_query(self, query, associate_id):
        """
        Send a user query to the Personalized Learning Assistant API.
        @param query: The user query string.
        @param associate_id: The user ID.
        @return: JSON response from the API.
        """
        
        try:
            access_token = await self.get_access_token()
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                'SourceType': 'Web'
            }

            payload = {
                "User_query": query,
                "PM_Category": "Academy",
                "Associate_level": "E40",
                "User_ID": associate_id,
                "Service_ID": "123456",
                "Adaptive_card_identifier": "True"
            }
            self.logger.debug("ask_query Payload: %s", payload)
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=headers, json=payload, ssl=False) as response:
                    response.raise_for_status()
                    if response.headers['Content-Type'] == 'application/json':
                        return await response.json()
                    else:
                        return await response.text()
        except Exception as ex:
            self.logger.error("Failed Exception in ask_query: %s", str(ex))
            raise Exception(f"Failed Exception in ask_query: {str(ex)}")
        except ClientError as ex:
            self.logger.error("Failed ClientError in ask_query: %s", str(ex))
            raise Exception(f"Failed ClientError in ask_query: {str(ex)}")