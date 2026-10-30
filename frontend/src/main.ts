import { createApp } from 'vue'
import App from './App.vue'
import {createPinia} from 'pinia'
import {i18n,setLocale} from './locales'
import {router} from './router'
import './styles/main.css'

setLocale(i18n.global.locale.value as 'en'|'zh-CN')
createApp(App).use(createPinia()).use(i18n).use(router).mount('#app')
