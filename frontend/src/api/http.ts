const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:1235'

export interface RequestOptions {
  method?: 'GET' | 'POST'
  body?: unknown
  scene?: string
}

function buildHeaders(scene?: string): HeadersInit {
  const accessKey = localStorage.getItem('accesskey') || import.meta.env.VITE_ACCESS_KEY || ''
  const accessSecret = localStorage.getItem('accesssecret') || import.meta.env.VITE_ACCESS_SECRET || ''
  const aiScene = scene || localStorage.getItem('ai_scene') || import.meta.env.VITE_AI_SCENE || 'default'

  return {
    'Content-Type': 'application/json',
    accesskey: accessKey,
    accesssecret: accessSecret,
    'x-ai-scene': aiScene
  }
}

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options.method || 'POST',
    headers: buildHeaders(options.scene),
    body: options.body ? JSON.stringify(options.body) : undefined
  })

  const text = await response.text()
  const data = text ? JSON.parse(text) : {}

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${JSON.stringify(data)}`)
  }

  return data as T
}
