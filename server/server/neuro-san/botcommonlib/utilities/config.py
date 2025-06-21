import os
from dotenv import load_dotenv
load_dotenv()
    
class RedisConfig:
    REDIS_HOSTNAME = os.environ.get("REDIS_HOSTNAME", "")
    REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "")
    REDIS_HOST_NAME = os.environ.get("REDIS_HOST_NAME", "")
    REDIS_PORT = os.environ.get("REDIS_PORT", "")
    REDIS_LOGICAL_DB = os.environ.get("REDIS_LOGICAL_DB")

class TransactionPortfolioAPICredentialsConfig:
    Transaction_Portfolio_CSIT_ClientId = os.environ.get("Transaction_Portfolio_CSIT_ClientId", "")
    Transaction_Portfolio_CSIT_ClientSecret = os.environ.get("Transaction_Portfolio_CSIT_ClientSecret", "")
    Transaction_Portfolio_ITOperations_ClientId = os.environ.get("Transaction_Portfolio_ITOperations_ClientId", "")
    Transaction_Portfolio_ITOperations_ClientSecret = os.environ.get("Transaction_Portfolio_ITOperations_ClientSecret", "")
    Transaction_Portfolio_FinOps_ClientId = os.environ.get("Transaction_Portfolio_FinOps_ClientId", "")
    Transaction_Portfolio_FinOps_ClientSecret = os.environ.get("Transaction_Portfolio_FinOps_ClientSecret", "")
    Transaction_Portfolio_Fulfilment_ClientId = os.environ.get("Transaction_Portfolio_Fulfilment_ClientId", "")
    Transaction_Portfolio_Fulfilment_ClientSecret = os.environ.get("Transaction_Portfolio_Fulfilment_ClientSecret", "")
    Transaction_Portfolio_HR_ClientId = os.environ.get("Transaction_Portfolio_HR_ClientId", "")
    Transaction_Portfolio_HR_ClientSecret = os.environ.get("Transaction_Portfolio_HR_ClientSecret", "") 
    Transaction_Portfolio_DEIT_ClientId = os.environ.get("Transaction_Portfolio_DEIT_ClientId", "")
    Transaction_Portfolio_DEIT_ClientSecret = os.environ.get("Transaction_Portfolio_DEIT_ClientSecret", "")
    Transaction_Portfolio_ITDA_ClientId = os.environ.get("Transaction_Portfolio_ITDA_ClientId", "")
    Transaction_Portfolio_ITDA_ClientSecret = os.environ.get("Transaction_Portfolio_ITDA_ClientSecret", "")

class TransactionQuickSOViewSOStatusConfig:
    Transaction_QuickSO_428_SOStatus_BaseAPI_URL = os.environ.get("Transaction_QuickSO_428_SOStatus_BaseAPI_URL")
    Transaction_QuickSO_428_SOStatus_TokenAPI_URL = os.environ.get("Transaction_QuickSO_428_SOStatus_TokenAPI_URL")

class CabAPIConfig:
    CAB_BASE_URL = os.environ.get("CAB_BASE_URL")
    CAB_TOKEN_URL = os.environ.get("CAB_TOKEN_URL")
    CAB_CLIENT_ID = os.environ.get("CAB_CLIENT_ID")
    CAB_CLIENT_SECRET = os.environ.get("CAB_CLIENT_SECRET")

class TransactionOneTransportCabOTPConfig:
    Transaction_OneTransport_988_CabOTP_BaseAPI_URL = os.environ.get("Transaction_OneTransport_988_CabOTP_BaseAPI_URL")
    Transaction_OneTransport_988_CabOTP_TokenAPI_URL = os.environ.get("Transaction_OneTransport_988_CabOTP_TokenAPI_URL")

class TransactionOneTransportIGSQRCodeConfig:
    Transaction_OneTransport_988_IGSQRCode_BaseAPI_URL = os.environ.get("Transaction_OneTransport_988_IGSQRCode_BaseAPI_URL")
    Transaction_OneTransport_988_IGSQRCode_TokenAPI_URL = os.environ.get("Transaction_OneTransport_988_IGSQRCode_TokenAPI_URL")
    
class PLAConfig:
    PLA_BASE_URL = os.environ.get("PLA_BASE_URL")
    PLA_TOKEN_URL = os.environ.get("PLA_TOKEN_URL")
    PLA_CLIENT_ID = os.environ.get("PLA_CLIENT_ID")
    PLA_CLIENT_SECRET = os.environ.get("PLA_CLIENT_SECRET")

class FlexiSeatAPIConfig:
    FLEXI_SEAT_BASE_URL=os.environ.get("FLEXI_SEAT_BASE_URL")
    FLEXISEAT_CLIENT_ID=os.environ.get("FLEXISEAT_CLIENT_ID")
    FLEXISEAT_CLIENT_SECRET=os.environ.get("FLEXISEAT_CLIENT_SECRET")
class SnowVAConfig:
    SNOW_VA_URL=os.environ.get("SNOW_VA_URL")
class TableLogConfig:
    LogTableName = os.environ.get("LogTableName")
    TableConnectionString = os.environ.get("TableConnectionString")

class ErrorMessage:
    Fallback = """[{"type":"AdaptiveCard","body":[{"type":"TextBlock","text":"We're experiencing some technical difficulties at the moment. Apologies for the inconvenience caused! Our support engineers will monitor and resolve the issue. Please try again sometime later. Thank you for your patience and understanding! #03","wrap":"true"}],"actions":[],"version":"1.5"}]"""