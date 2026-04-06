import { createRouter, createWebHistory } from 'vue-router'
import TranslateView from '../views/TranslateView.vue'
import OcrView from '../views/OcrView.vue'
import ShopView from '../views/ShopView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/translate' },
    { path: '/translate', component: TranslateView },
    { path: '/ocr', component: OcrView },
    { path: '/shop', component: ShopView }
  ]
})

export default router
