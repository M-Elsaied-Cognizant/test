from .redisHelper import get_redis_item
import json
import bleach
import logging

# Configure logger
# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
def get_intent_id_from_args(args):
    """
    Extracts the intent ID from the provided arguments.

    :param args: A dictionary containing the arguments.
    :return: The intent ID if present, otherwise None.
    """
    # Extracting 'origin_str' as a string
    try:
        logger.info("Extracting IntentId from args: %s", args)
        origin_str = args.get("origin_str", "")
        origin_str = bleach.clean(origin_str)
        if isinstance(origin_str, str):
            func_name = origin_str.split('.')[-1]
            logger.info("Extracting IntentId for function %s", func_name)
            redis_item = get_redis_item(f"AIAssistant_4139_T_{func_name}")
            if redis_item:
                redis_item = json.loads(redis_item)
                IntentId = str(redis_item[0].get('IntentID','NA'))
                logger.debug("IntentId for func %s: '%s'", func_name, IntentId)
            else:
                IntentId = "NA"
        else:
            IntentId = "NA"
    except Exception as e:
        logger.error("Error extracting IntentId: %s", str(e))
        IntentId = "NA"
    
    return IntentId

def get_intent_id(func_name):
    """
    Extracts the intent ID from the provided arguments.

    :param args: A dictionary containing the arguments.
    :return: The intent ID if present, otherwise None.
    """
    # Extracting 'origin_str' as a string
    try:
        logger.info("Extracting IntentId for function %s", func_name)
        redis_item = get_redis_item(f"AIAssistant_4139_T_{func_name}")
        if redis_item:
            redis_item = json.loads(redis_item)
            IntentId = str(redis_item[0].get('IntentID', 'NA'))
            logger.debug("IntentId for func %s: '%s'", func_name, IntentId)
        else:
            IntentId = "NA"
    except Exception as e:
        logger.error("Error extracting IntentId: %s", str(e))
        IntentId = "NA"

    return IntentId

class AdaptiveCard:

    @staticmethod
    def extract_data_from_adaptive_card_data(card):
        import json  # Ensure json is imported
        if isinstance(card, str):
            try:
                card = json.loads(card)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON string provided.")

        if isinstance(card, list):
            results = [AdaptiveCard.extract_data_from_adaptive_card_data(c) for c in card]
            extracted_data_list = [r[0] for r in results]
            extracted_parts_list = [r[1] for r in results]
            return extracted_data_list, " ".join(extracted_parts_list)

        if not isinstance(card, dict):
            raise ValueError("Input must be a JSON string, dict, or list of dicts.")

        extracted_data = {}
        extracted_parts = []
        current_key = None

        def extract_elements(elements):
            nonlocal current_key
            if not isinstance(elements, list):
                return
            for element in elements:
                if not isinstance(element, dict) or 'type' not in element:
                    continue
                element_type = element['type']
                if element_type == 'TextBlock':
                    text = element.get('text', '').strip()
                    if current_key:
                        extracted_data[current_key] = text
                        current_key = None
                    else:
                        current_key = text.lower().replace(" ", "_")
                        extracted_parts.append(text)
                elif element_type == 'Image':
                    image_url = element.get('url', '')
                    extracted_data[current_key or f"image_{len(extracted_data)}"] = image_url
                    extracted_parts.append(f"Image URL: {image_url}")
                    alt_text = element.get("altText")
                    if alt_text:
                        extracted_parts.append(f"Image Alt Text: {alt_text}")
                    current_key = None
                elif element_type == 'ActionSet':
                    actions = []
                    for action in element.get('actions', []):
                        action_type = action.get('type')
                        title = action.get('title', '')
                        if action_type == 'Action.OpenUrl':
                            url = action.get('url', '')
                            actions.append(f"{title} (URL: {url})")
                            extracted_parts.append(f"Button: {title} (URL: {url})")
                        elif action_type == 'Action.Submit':
                            data = action.get('data', {})
                            data_str = json.dumps(data) if isinstance(data, dict) else str(data)
                            actions.append(f"{title} (Data: {data_str})")
                            extracted_parts.append(f"Button: {title} (Data: {data_str})")
                    extracted_data[current_key or f"action_{len(extracted_data)}"] = actions
                    current_key = None
                elif element_type == 'ColumnSet':
                    for column in element.get('columns', []):
                        extract_elements(column.get('items', []))
                elif element_type == 'FactSet':
                    for fact in element.get('facts', []):
                        title = fact.get('title', '')
                        value = fact.get('value', '')
                        if title and value:
                            extracted_parts.append(f"{title} {value}")
                            extracted_data[title.lower().replace(" ", "_")] = value
                elif 'items' in element:
                    extract_elements(element['items'])
                if "selectAction" in element:
                    action = element.get("selectAction")
                    action_type = action.get("type")
                    if action_type == "Action.OpenUrl":
                        url = action.get("url")
                        if url:
                            extracted_parts.append(f"Clickable Link: {url}")
                    elif action_type == "Action.Submit":
                        data = action.get("data")
                        if data:
                            data_str = json.dumps(data) if isinstance(data, dict) else str(data)
                            extracted_parts.append(f"Clickable Action Data: {data_str}")

        extract_elements(card.get('body', []))
        card_actions = card.get('actions', [])
        for action in card_actions:
            action_type = action.get('type')
            title = action.get('title', '')
            if action_type == 'Action.OpenUrl':
                url = action.get('url', '')
                extracted_parts.append(f"Button: {title} (URL: {url})")
            elif action_type == 'Action.Submit':
                data = action.get('data', {})
                data_str = json.dumps(data) if isinstance(data, dict) else str(data)
                extracted_parts.append(f"Button: {title} (Data: {data_str})")
        return extracted_data, " ".join(extracted_parts)

        # {
        #     "Response": extracted_data,
        #     "Response_string": " ".join(extracted_parts)
        # }
