'''
@create_time: 2026/3/28 上午10:57
@Author: GeChao
@File: get_data_utils.py
'''
import requests


def product_crawler(item_url):
    try:
        url = "inner api xxx"
        response = requests.post(url, data={"itemDetailUrl": item_url, "source": "xxx"})
        response.raise_for_status()
        data = response.json()
        if data.get("code") == 0 and "obj" in data:
            return data["obj"]
        else:
            return None
    except Exception as error:
        print(error)
        return None


def fetch_product(product_info):
    """
    :param product_info:
    spu_img_url*
    related_items*
    duplicate_image_urls
    name*
    supplier
    price_ranges
    alibabaResponse*
    :return: json
    """
    if not product_info:
        return None
    try:
        spu_img_url = product_info.get("imgUrls", "")

        related_items = product_info.get("relatedItems", [])

        duplicate_image_urls = list(set([item["skuImageUrl"] for item in related_items if "skuImageUrl" in item]))

        name = product_info.get("name", "Unknown Product")
        supplier = product_info.get("supplyLoginId", "Unknown Supplier")
        price_ranges = product_info.get("priceRanges", [])
        response = product_info.get("Response", {})

        if response:
            category = response.get("categoryName", "")
            attributes = response.get("attributes", [])
            attributes = [{"attributeName": item["attributeName"], "value": item["value"]} for item in attributes]
        else:
            category = ""
            attributes = []

        ret_data = {
            "spu_image_url": spu_img_url,
            "sku_image_url_list": duplicate_image_urls,
            "product_title": name,
            "category_name": category,
            "attributes": attributes,
            "supplier_name": supplier,
            "price_ranges": price_ranges
        }
        return ret_data
    except Exception as error:
        print(error)
        return None


def get_product(product_url):
    '''
    get product info
    :param product_url: https://detail.1688.com/offer/xxx
    :return: json/None
    '''
    product_info = product_crawler(product_url)
    print("product_info:", product_info)
    return fetch_product(product_info)


