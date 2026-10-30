import { createI18n } from 'vue-i18n'
import zh from './zh-CN'
import en from './en'
export type Locale = 'zh-CN' | 'en'
function initialLocale(): Locale {
 const saved = localStorage.getItem('learnhub-locale')
 return saved === 'en' || saved === 'zh-CN' ? saved : navigator.language.startsWith('en') ? 'en' : 'zh-CN'
}
export const i18n = createI18n({ legacy: false, locale: initialLocale(), fallbackLocale: 'zh-CN', messages: { 'zh-CN': zh, en } })
export let explicitlySelected = false
export function setLocale(value: Locale, explicit = false) {
 if (explicit) explicitlySelected = true
 i18n.global.locale.value = value
 localStorage.setItem('learnhub-locale', value)
 document.documentElement.lang = value
}
