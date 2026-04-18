'''
@create_time: 2026/4/18 下午5:52
@Author: GeChao
@File: modelscope_data.py
'''
import pandas as pd

df = pd.read_csv("./product_description_generation/test.csv")
print(df.head())
print(df.columns)

