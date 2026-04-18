---
license: Apache License 2.0
text:
  text-generation:
    language:
      - zh
    type:
      - data-to-text
tags:
  - product description generation
---

## 概述：

商品文案描述生成数据集属于下游data-to-text类任务，可以用于训练商品的卖点或文案描述生成模型

## 数据集描述：

本数据集包括测试集（3848）。其中，每一条数据有两个属性，分别是输入句子text1和输出句子text2。其中输入句子是商品的卖点词，输出句子为一段描述该商品的文案。

## 范例：

{"text1":"砧板/菜板，梯形，深度，食物，组合，底座，菜板","text2":"一个组合两块菜板，轻松生熟分开，深度凹槽设计，收集食物汁水，整洁台面，梯形分散受力底座，切菜时更稳固。"}
## Clone with HTTP
* http://www.modelscope.cn/datasets/lcl193798/product_description_generation.git