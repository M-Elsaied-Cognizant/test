import bleach
import html

def clean_json(json_obj):
    if isinstance(json_obj, dict):
        return {key: clean_json(value) for key, value in json_obj.items()}
    elif isinstance(json_obj, list):
        return [clean_json(element) for element in json_obj]
    elif isinstance(json_obj, str):
        return html.unescape(json_obj)
    else:
        return json_obj