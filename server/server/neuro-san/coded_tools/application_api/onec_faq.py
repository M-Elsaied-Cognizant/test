import os
import bleach
import logging
import aiohttp
import requests
from aiohttp import ClientError
from dotenv import load_dotenv

load_dotenv()


class OneCFAQ:

    def __init__(self):
        self.url = os.environ.get("QUERYING_API_URL")
        self.is_configured = True
        self.logger = logging.getLogger(self.__class__.__name__)
        
    # async HTTP request
    async def get_onec_faq(self, request_json, sly_data):
        payload = {
            "query": "",
            "user_id": sly_data.get("associate_id", ""),
            "GlobalApp_Id":sly_data.get("App_id", ""),
            "CountryCode":sly_data.get("Location", ""),
            "Dept_ID":sly_data.get("Dept_id", ""),
            "Grade_Code":sly_data.get("grade", ""),
            "Bot_Id": sly_data.get("bot_id", os.environ.get('querying_bot_id')),
            "session_id": sly_data.get("request_id", "None"),
            "query_id": sly_data.get("query_id", "None")
        }
        payload.update(request_json)
        
        self.logger.debug("get_onec_faq Payload: %s", payload)
        # response = requests.post(self.url, json=payload, verify=False)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, json=payload, timeout=90, ssl=False) as response:
                    if response.headers['Content-Type'] == 'application/json':
                        return await response.json()
                    else:
                        return await response.text()
        except Exception as ex:
            self.logger.error("Failed Exception OneCFAQ: %s", str(ex))
            raise Exception(f"Failed Exception OneCFAQ: {str(ex)}")
        except ClientError as ex:
            self.logger.error("Failed ClientError OneCFAQ: %s", str(ex))
            raise Exception("Failed ClientError OneCFAQ: %s", str(ex))

    # # Sync HTTP request    
    # def get_onec_faq(self, request_json, sly_data):
    #     payload = {
    #         "query": "",
    #         "GlobalApp_Id":sly_data.get("App_id", ""),
    #         "CountryCode":sly_data.get("Location", ""),
    #         "Dept_ID":sly_data.get("Dept_id", ""),
    #         "Grade_Code":sly_data.get("grade", ""),
    #         "Bot_Id": sly_data.get("bot_id", os.environ.get('querying_bot_id')),
    #         "user_id": ""
    #     }
    #     payload.update(request_json)
    #     # print("OneCFAQ url: ", self.url)
    #     logger.debug("OneCFAQ Payload: %s", payload)
    #     try:
    #         # Sync HTTP request
    #         response = requests.post(self.url, json=payload, verify=False)
    #         response.raise_for_status()
    #         logger.debug("OneCFAQ response: %s", response.text)
    #         if response.headers['Content-Type'] == 'application/json':
    #             return response.json()
    #         else:
    #             return response.text
    #     except requests.exceptions.RequestException as ex:
    #         logger.error("Failed RequestException OneCFAQ: %s - %s", response.status, response.text)
    #         raise Exception(f"Failed RequestException OneCFAQ: {response.status}, {response.text}")
    #     except requests.exceptions.JSONDecodeError as e:
    #         logger.error("Failed JSONDecodeError OneCFAQ: %s - %s", response.status, response.text)
    #         raise Exception(f"Failed JSONDecodeError OneCFAQ: {response.status}, {response.text}")
    #     except Exception as e:
    #         logger.error("Failed OneCFAQ: %s - %s", response.status, response.text)
    #         raise Exception(f"Failed OneCFAQ: {response.status}, {response.text}")

# # Example usage
# if __name__ == "__main__":
#     associate_id = bleach.clean(input("Enter associate ID: "))
#     user_query = bleach.clean(input("Enter your query: "))
#     try:
#         onec_faq = OneCFAQ()
#         request = {"query": user_query, "user_id": associate_id}
#         sly_data = {"App_id": "", "Location": "", "Dept_id": "", "grade": "", "bot_id": os.environ.get('querying_bot_id')}
#         response = onec_faq.get_onec_faq(request, sly_data)
#         print("OneCFAQ Response: ", response)
#     except Exception as e:
#         print("Error in OneCFAQ: ", str(e))