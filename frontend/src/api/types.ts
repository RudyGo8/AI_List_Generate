export interface ApiResult<T = unknown> {
  success: boolean
  msg: string
  data: T
  usage?: Record<string, unknown> | null
}

export interface TranslateResponse {
  translated_content: string
}

export interface BatchTranslateItem {
  content: string
  translated: string
}

export interface BatchTranslateResponse {
  translated_content_list: BatchTranslateItem[]
}

export interface OcrResponse {
  word_list: string
}

export interface ShopResponse {
  task_id?: number
  status?: string
  [key: string]: unknown
}
