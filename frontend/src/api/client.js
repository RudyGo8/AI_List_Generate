import { request } from './http'

export function translate(content, desLangType) {
  return request('/api/r1/c/translate', {
    body: { content, des_lang_type: desLangType }
  })
}

export function batchTranslate(contentList, desLangType) {
  return request('/api/r1/c/batchtranslate', {
    body: { content_list: contentList, des_lang_type: desLangType }
  })
}

export function ocr(imageUrlList) {
  return request('/api/r1/c/ocr', {
    body: { image_url_list: imageUrlList }
  })
}

export function createShopTask(payload) {
  return request('/api/r1/shop/ailist', {
    body: payload
  })
}

export function getShopTask(taskId) {
  return request(`/api/r1/shop/ailist/task/${taskId}`, {
    method: 'GET'
  })
}
