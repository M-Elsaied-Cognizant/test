import requests
import logging
import json
import asyncio
import httpx
from botcommonlib.utilities.config import SnowVAConfig

class SnoW:
    def __init__(self):
        self.api_url = SnowVAConfig.SNOW_VA_URL
        self.is_configured = True
        self.logger = logging.getLogger(self.__class__.__name__)

    
    async def snow_va_request(self,query,sly_data):
        """Call the ServiceNow API using the generated token."""
        try:
            body= {
                "action": sly_data.get("action", None),
                "user_id": sly_data.get("user_id", None),
                "email_id": sly_data.get("email_id", None),
                "user_query": query,
                "intent_id": sly_data.get("intent_id", None),
                "query_id": sly_data.get("query_id", None),
                "AzureSignalRconnectionID": sly_data.get("AzureSignalRconnectionID", None),
                "session_id": sly_data.get("session_id", None),
                "LiveAgentTopic":sly_data.get("LiveAgentTopic",None),
                "prevCardId":sly_data.get("prevCardId",None),
                "channel": sly_data.get("channel", None),
                "cardid": sly_data.get("cardid", None),
                "agent_name": sly_data.get("agent_name", None)
            }
            
            self.logger.info(f"SnowVA Body: {json.dumps(body, indent=2)}")
            self.logger.info(f"Snow VA URL:{self.api_url}")
            async with httpx.AsyncClient(verify=False) as client:
                headers = {
                    
                    "Content-Type": "application/json"
                }
                response = await client.post(self.api_url, headers=headers, json=body)

                self.logger.info(f"API Response Code: {response.status_code}")
                if response.status_code == 200:
                    return response.status_code
                else:
                    self.logger.error(f"Error: {response.status_code}, Response: {response.text}")
                    return None
        except Exception as e:
            self.logger.error(f"Error occurred while calling API: {e}")
            return None

        