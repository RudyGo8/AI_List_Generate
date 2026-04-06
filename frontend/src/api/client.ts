import { request } from './http'
import type {
  ApiResult,
  BatchTranslateResponse,
  OcrResponse,
  ShopResponse,
  TranslateResponse
} from './types'

export function translate(content: string, desLangType: string) {
  return request<ApiResult<TranslateResponse>>('/api/r1/c/translate', {
    body: { content, des_lang_type: desLangType }
  })
}

export function batchTranslate(contentList: string[], desLangType: string) {
  return request<ApiResult<BatchTranslateResponse>>('/api/r1/c/batchtranslate', {
    body: { content_list: contentList, des_lang_type: desLangType }
  })
}

export function ocr(imageUrlList: string[]) {
  return request<ApiResult<OcrResponse>>('/api/r1/c/ocr', {
    body: { image_url_list: imageUrlList }
  })
}

export function createShopTask(payload: {
  site: string
  des_lang_type: string
  spu_image_url?: string
  product_title?: string
  category_name?: string
  notice_url?: string
}) {
  return request<ApiResult<ShopResponse>>('/api/r1/shop/ailist', {
    body: payload
  })
}
