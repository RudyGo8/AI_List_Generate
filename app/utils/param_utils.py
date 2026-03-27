'''
@create_time: 2026/3/27 下午3:47
@Author: GeChao
@File: param_utils.py
'''
import re
import ast


def extract_list(text):
    """从AI返回的文本中提取JSON列表
    '翻译结果是：["Hello","World","China"] 完成！' ->  ["Hello","World","China"]
    """
    try:
        pattern = r'\[\s*(".*?")\s*(,\s*".*?")*\s*\]'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            list_str = match.group(0)
            _list = ast.literal_eval(list_str)
            return _list
        else:
            print("未找到匹配的JSON列表。")
            return None
    except Exception as error:
        print(error)
        return None
