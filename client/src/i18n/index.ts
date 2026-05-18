import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import uk from './uk.json'
import en from './en.json'

const STORAGE_KEY = 'archkanban.lang'

const saved = (typeof window !== 'undefined' && localStorage.getItem(STORAGE_KEY)) || 'uk'

void i18n
  .use(initReactI18next)
  .init({
    resources: {
      uk: { translation: uk },
      en: { translation: en },
    },
    lng: saved,
    fallbackLng: 'uk',
    interpolation: { escapeValue: false },
  })

export function changeLanguage(lang: 'uk' | 'en') {
  void i18n.changeLanguage(lang)
  if (typeof window !== 'undefined') {
    localStorage.setItem(STORAGE_KEY, lang)
    document.documentElement.lang = lang
  }
}

export default i18n
