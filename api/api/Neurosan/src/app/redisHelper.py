"""
Utility to deal with Redis
"""
import bleach
import redis
import logging
from .config import RedisConfig
import json

logger = logging.getLogger(__name__)
try:
    redis_client = redis.StrictRedis(host=RedisConfig.REDIS_HOST_NAME, port=RedisConfig.REDIS_PORT,
                    password=RedisConfig.REDIS_PASSWORD, db=RedisConfig.REDIS_LOGICAL_DB, ssl=True, decode_responses=True)
    
except Exception as e:
    logger.error(f"Error in loading environment variables: {e}")
    
def get_redis_lrange(key_, index, upper_index):
    """
    Returns objects from redis list within these indexes
    """
    try:
        return redis_client.lrange(key_, index, upper_index)
    except Exception as ex:
        logger.warning(f"Critical error in getRedisLrange({key_}, {index}) - {ex}")
        raise ex


def set_redis_expiry(key_, time_):
    """
    Set expiration to redis keys
    """
    try:
        redis_client.expire(key_, time_)
    except Exception:
        logger.exception(f"Critical error in setRedisExpiry - {key_}, {time_}")


def get_redis_hashmap(key_, mapping_):
    """
    Returns contents from redis hashmap
    """
    try:
        return redis_client.hget(key_, mapping_) or None
    except Exception as ex:
        logger.warning(f"Critical error in getRedisHashmap - {ex}")
        raise ex


def get_all_redis_hashmap(key_):
    """
    Returns all items from redis hash map
    """
    try:
        response = {}
        response = redis_client.hgetall(key_) or {}
    except Exception:
        logger.exception("Critical error in getAllRedisHashmap")
        response = {}
    return response


def set_redis_chat_hashmap(key_, mapping_, value_):
    """
    Set object to a redis hashmap
    """
    try:
        if isinstance(value_, dict):
            # Serialize the dictionary to a JSON string
            for k, v in value_.items():
                redis_client.hset(key_, k, v if not isinstance(v, (dict, list)) else json.dumps(v))
        else:
            redis_client.hset(key_, mapping_, value_)
    except Exception as ex:
        logger.exception(f"Critical error in setRedisHashmap {str(ex)}")

def get_chat_all_redis_hashmap(key_):
    """
    Returns all items from redis hash map
    """
    try:
        response = redis_client.hgetall(key_) or {}
        # Deserialize JSON strings back to Python objects
        for k, v in response.items():
            try:
                response[k] = json.loads(v)
            except json.JSONDecodeError:
                pass  # Keep the value as-is if it's not JSON
    except Exception:
        logger.exception("Critical error in getAllRedisHashmap")
        response = {}
    return response
def set_redis_hashmap(key_, mapping_, value_):
    """
    Set object to a redis hashmap
    """
    try:
        if isinstance(value_, dict):
            if value_.keys():
                # Serialize non-string values
                safe_dict = {
                    k: v if isinstance(v, (str, int, float, bytes)) else json.dumps(v)
                    for k, v in value_.items()
                }
                redis_client.hmset(key_, safe_dict)
            else:
                logger.exception(f"Trying to set with empty dict - {value_}"[:500])
        else:
            redis_client.hset(key_, mapping_, value_)
    except Exception:
        logger.exception("Critical error in setRedisHashmap")


def get_redis_list(key_):
    """
    Returns redis list
    """
    try:
        if redis_client.exists(key_) == 0:
            return None
        return redis_client.lrange(key_, 0, -1) or None
    except Exception:
        logger.exception("Critical error in getRedisList")
        return None


def push_redis_list(key_, value_):
    """
    Push to redis list
    """
    try:
        if isinstance(value_, list):
            redis_client.rpush(key_, *value_)
        else:
            redis_client.rpush(key_, value_)
    except Exception:
        logger.exception("Critical error in pushRedisList")


def get_redis_item(key_):
    """
    Returns redis item
    """
    try:
        logger.info(f"get_redis_item started. key: {key_}") 
        key_ = bleach.clean(key_)
        response = None
        if redis_client.exists(key_) != 0:
            response = bleach.clean(redis_client.get(key_)) or None
        if response == "null":
            response = None
        # logger.info(f"get_redis_item ended. response: {response}")
    except Exception:
        logger.exception("Critical error in getRedisItem")
        response = None
    return response


def set_redis_item(key_, value_):
    """
    Set a redis item
    """
    try:
        redis_client.set(key_, value_)
    except Exception:
        logger.exception("Critical error in setRedisItem")


def delete_redis_key(key_):
    """
    Delete key from redis hashmap
    """
    try:
        redis_client.delete(key_)
    except Exception:
        logger.exception("Critical error in delete_redis_key")
        
