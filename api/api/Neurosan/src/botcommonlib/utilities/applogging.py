import logging
from azure.data.tables import TableServiceClient, TableEntity
from azure.identity import DefaultAzureCredential
import datetime as dt

from app.config import TableStorageConfig, DeploymentConfig, ApplicationConfig

connection_string = TableStorageConfig.AZURE_TABLE_STORAGE_CONNECTION_STRING
TableName = TableStorageConfig.AZURE_TABLE_STORAGE_TABLE_NAME_FOR_LOG

if DeploymentConfig.DEPLOYMENT_ENVIRONMENT == "LOCAL":
    # For local development, use the connection string directly
    # connection_string =  connection_string + TableStorageConfig.TABLESTORAGECONNECTIONPWD
    table_service_client = TableServiceClient(endpoint=connection_string)
else:
    # For non-local environments, use DefaultAzureCredential
    credential = DefaultAzureCredential()
    table_service_client = TableServiceClient(endpoint=connection_string, credential=credential)

class AzureTableHandler(logging.Handler):
    def __init__(self, table_service_client, table_name):
        super().__init__()
        self.table_client = table_service_client.create_table_if_not_exists(table_name=table_name)

    def emit(self, record):
        try:
            log_data = self.format(record)
            entity = TableEntity()
            entity["PartitionKey"] = log_data["PartitionKey"]
            entity["RowKey"] = log_data["RowKey"]
            entity["AssociateId"] = log_data.get("AssociateId")
            entity["ExceptionMessage"] = log_data["ExceptionMessage"]
            entity["FileName"] = log_data["FileName"]
            entity["FunctionName"] = log_data["FunctionName"]
            entity["LineNumber"] = log_data["LineNumber"]
            entity["Logtype"] = log_data["Logtype"]
            entity["RecordName"] = log_data["RecordName"]
            entity["request_id"] = log_data.get("request_id")
            entity["query_id"] = log_data.get("query_id")
            entity["source"] = log_data.get("source")
            entity["message_type"] = log_data.get("message_type")

            self.table_client.create_entity(entity=entity)
        except Exception as e:
            logging.error(f"Failed to insert entity for entity:{str(entity)} with ex: {e}")

class CustomJSONFormatter(logging.Formatter):
    def format(self, record):
        return {
            "PartitionKey": "1CNEUROSANAPI",
            "RowKey": dt.datetime.now(dt.timezone.utc).isoformat(),
            "AssociateId": getattr(record, "user_id", "None"),
            "ExceptionMessage": record.getMessage(),
            "FileName": record.pathname,
            "FunctionName": record.funcName,
            "LineNumber": record.lineno,
            "Logtype": record.levelname,
            "RecordName": record.name,
            "request_id": getattr(record, "request_id", "None"),
            "query_id": getattr(record, "query_id", "None"),
            "source": getattr(record, "source", "None"),
            "message_type": getattr(record, "message_type", "None"),
        }

class LogRecordFilter(logging.Filter):
    """
    Custom logging filter for specific record names.
    """
    def filter(self, record):
        excluded_record_names = TableStorageConfig.ExcludedLogRecordNames
        # print("Excluded Record Names: ", excluded_record_names)
        if excluded_record_names:
            excluded_record_names = excluded_record_names.split(',')
        else:
            excluded_record_names = []

        if record.name in excluded_record_names:
            return False
        return True

# Initialize the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO if ApplicationConfig.APPLICATION_TRACING_ENABLED == "true" else logging.ERROR)

# Initialize AzureTableHandler
azure_handler = AzureTableHandler(table_service_client=table_service_client, table_name=TableName)
azure_handler.setFormatter(CustomJSONFormatter())

# Attach the filter to the AzureTableLogger
log_filter = LogRecordFilter()
logger.addFilter(log_filter)

# Add the handler to the logger
logger.addHandler(azure_handler)

# azure_handler = logging.StreamHandler()
# # Attach the filter to the AzureTableLogger
# log_filter = LogRecordFilter()
# logger.addFilter(log_filter)
#
# # Add the handler to the logger
# logger.addHandler(azure_handler)