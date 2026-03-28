'''
@create_time: 2026/3/27 下午3:47
@Author: GeChao
@File: param_utils.py
'''
import datetime
import re
import ast


def extract_list(text):
    """
    Extract JSON list from the given text.
    'The translation result is: ["Hello","World","China"] Done!' ->  ["Hello","World","China"]
    """
    try:
        pattern = r'\[\s*(".*?")\s*(,\s*".*?")*\s*\]'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            list_str = match.group(0)
            _list = ast.literal_eval(list_str)
            return _list
        else:
            print("No JSON list found in the text.")
            return None
    except Exception as error:
        print(error)
        return None


def list_url_to_str(list_data):
    if not list_data:
        return None
    elif isinstance(list_data, list):
        # Convert list elements to strings and join with commas
        return ",".join(map(str, list_data))
    else:
        return str(list_data)


def usage_addition(usage_one, usage_two):
    if not usage_one:
        return usage_two
    result = {}
    for key in usage_one:
        values_one = usage_one.get(key, 0)
        values_two = usage_two.get(key, 0)
        values_one = values_one if values_one else 0
        values_two = values_two if values_two else 0

        result[key] = values_one + values_two

    return result


def list_to_str(list_data):
    if not list_data:
        return None
    # Convert list to comma-separated string
    elif isinstance(list_data, list):
        return ",".join(list_data)
    else:
        return list_data


def filter_product_response(response_content: dict = None):
    if not response_content:
        return None
    resp = response_content
    del resp['id']
    del resp['product_src_id']
    del resp['version']
    del resp['create_time']
    del resp['create_user']
    del resp['update_user']
    return resp


def json_serial(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()  # datetime -> ISO 8601 format
    raise TypeError(f"Type {type(obj)} not serializable")
