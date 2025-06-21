import os
import json
import logging
from azure.data.tables import TableServiceClient
from azure.identity import DefaultAzureCredential
from botcommonlib.utilities.config import TableLogConfig
from datetime import datetime
import re
import logging
from dotenv import load_dotenv
load_dotenv()

class LogRecordFilter(logging.Filter):
    """
    Custom logging filter for specific record names.
    """
    def filter(self, record):
        excluded_record_names = os.environ.get('ExcludedLogRecordNames').split(',')
        # print("Excluded Record Names: ", excluded_record_names)
        if record.name in excluded_record_names or record.getMessage().startswith("Task exception was never retrieved"):
            # print(f"Record {record.name} is excluded from logging.")
            return False
        # print(f"Record {record.name} is included in logging.")
        return True


class AzureTableStorageHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        connection_string = TableLogConfig.TableConnectionString
        table_name = TableLogConfig.LogTableName
        # print("Connection String: ", connection_string)
        self.table_service_client = TableServiceClient(endpoint=connection_string,
                                                       credential = DefaultAzureCredential()
                                                       )
        self.table_client = self.table_service_client.get_table_client(table_name)
        self.table_service_client.create_table_if_not_exists(table_name)

    def emit(self, record):
        log_entry = self.format(record)
        excluded_record_names = os.environ.get('ExcludedLogRecordNames').split(',')
        # if record.name not in excluded_record_names:
        try:
            log_data = {}
            log_data = json.loads(log_entry)
        except json.JSONDecodeError as ex:
            patterns = {
                'PartitionKey': r'"PartitionKey": "(.*?)",',
                'RowKey': r'"RowKey": "(.*?)",',
                'AssociateId': r'"AssociateId": "(.*?)",',
                'ExceptionMessage': r'"ExceptionMessage": "(.*?)", "FileName":',
                'FileName': r'"FileName": "(.*?)",',
                'FunctionName': r'"FunctionName": "(.*?)",',
                'LineNumber': r'"LineNumber": "(.*?)",',
                'Logtype': r'"Logtype": "(.*?)",',
                'RecordName': r'"RecordName": "(.*?)",',
                'request_id': r'"request_id": "(.*?)",',
                'query_id': r'"query_id": "(.*?)",',
                'source': r'"source": "(.*?)",',
                'message_type': r'"message_type": "(.*?)"',
            }

            for key, pattern in patterns.items():
                match = re.search(pattern, log_entry, re.DOTALL if key == 'ExceptionMessage' else 0)
                log_data[key] = (match.group(1).replace('"', "'")
                                               .replace('\\n','')) if key == 'ExceptionMessage' and match \
                                               else (match.group(1) if match else None)
        try:
            self.table_client.create_entity(entity=log_data)
        except Exception as e:
            logging.error(f"Failed to insert entity for entity:{str(log_data)} with ex: {e}")

