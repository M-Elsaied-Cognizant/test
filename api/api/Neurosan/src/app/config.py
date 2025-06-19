import os
from dotenv import load_dotenv
load_dotenv()

class Neurosan_config:
    NEUROSAN_HOST=os.getenv("NEUROSAN_HOST", "").strip()
    NEUROSAN_PORT=os.getenv("NEUROSAN_PORT", "").strip()
    NEUROSAN_AGENT_NAME=os.environ.get("NEUROSAN_AGENT_NAME", "").strip()
    NEUROSAN_CHAT_FILTER=os.getenv("NEUROSAN_CHAT_FILTER", "MINIMAL").strip()
    IsChatContextEnabled = True if os.environ.get("IsChatContextEnabled", "false").lower() == "true"  else False

    # Validate environment variables
    if not NEUROSAN_AGENT_NAME:
        raise ValueError("Environment variable NEUROSAN_AGENT_NAME is missing or empty.")
    if not NEUROSAN_HOST:
        raise ValueError("Environment variable NEUROSAN_HOST is missing or empty.")
    if not NEUROSAN_PORT.isdigit():
        raise ValueError("Environment variable NEUROSAN_PORT must be a valid number.")

class RedisConfig:
    REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "")
    REDIS_HOST_NAME = os.environ.get("REDIS_HOST_NAME", "")
    REDIS_PORT = os.environ.get("REDIS_PORT", "")
    REDIS_LOGICAL_DB = os.environ.get("REDIS_LOGICAL_DB")
    REDIS_KEY_CHAT_CONTEXT_PREFIX = "AIAssistant_4139_M_ChatContext_"
    REDIS_TTL = int(os.environ.get("REDIS_TTL", "3600"))  # Default to 1 hour if not set


class TableStorageConfig:
    AZURE_TABLE_STORAGE_CONNECTION_STRING = os.environ.get(
        "AZURE_TABLE_STORAGE_CONNECTION_STRING")
    AZURE_TABLE_STORAGE_TABLE_NAME_FOR_LOG = os.environ.get(
        "AZURE_TABLE_STORAGE_TABLE_NAME_FOR_LOG")
    ExcludedLogRecordNames = os.environ.get('ExcludedLogRecordNames', '')

class DeploymentConfig:
    DEPLOYMENT_ENVIRONMENT = os.environ.get("DEPLOYMENT_ENVIRONMENT", "LOCAL")

class ErrorMessage:
    Fallback = [{"type":"AdaptiveCard","body":[{"type":"TextBlock","text":"We're experiencing some technical difficulties at the moment. Apologies for the inconvenience caused! Our support engineers will monitor and resolve the issue. Please try again sometime later. Thank you for your patience and understanding! #02","wrap":"true"}],"actions":[],"version":"1.5"}]
    Fallback_Noresponse = [{"type":"AdaptiveCard","body":[{"type":"TextBlock","text":"No response received from the system. Please try again later. #02","wrap":"true"}],"actions":[],"version":"1.5"}]
    Fallback_Content_Filter = [{"type": "AdaptiveCard", "body": [{"type": "TextBlock", "text": "The response was filtered due to the prompt triggering content management policy. #02", "wrap": "true"}], "actions": [], "version": "1.5"}]

class ApplicationConfig:
    APPLICATION_TRACING_ENABLED = os.environ.get(
        "APPLICATION_TRACING_ENABLED", "false").lower()
