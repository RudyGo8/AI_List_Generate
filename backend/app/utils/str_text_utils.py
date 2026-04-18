'''
@create_time: 2026/4/18 上午10:36
@Author: GeChao
@File: str_text_utils.py
'''

import json


import json

def to_list(value):
  if isinstance(value, list):
      return value
  if not isinstance(value, str):
      return []

  text = value.strip()
  if not text:
      return []

  # 处理你这种外层多一层引号的情况
  if text.startswith('"[') and text.endswith(']"'):
      text = text[1:-1]

  try:
      parsed = json.loads(text)
      if isinstance(parsed, list):
          return [str(x).strip() for x in parsed if str(x).strip()]
  except Exception:
      pass

  return []


def norm_text(text: str) -> str:
    return str(text or "").strip().lower()


def norm_path(path: str) -> str:
    # 统一分隔符、空格、大小写
    text = str(path or "").strip().lower()
    text = text.replace(" / ", ">").replace("/", ">")
    parts = [p.strip() for p in text.split(">") if p.strip()]
    return " > ".join(parts)


def to_float(v):
    try:
        return float(v)
    except Exception:
        return 0.0
