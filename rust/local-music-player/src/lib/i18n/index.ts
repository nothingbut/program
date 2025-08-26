import { browser } from '$app/environment';
import { init, register, locale, waitLocale } from 'svelte-i18n';

const defaultLocale = 'en';

// Register locales
register('en', () => import('./locales/en.json'));
register('zh', () => import('./locales/zh.json'));

// Initialize i18n
init({
  fallbackLocale: defaultLocale,
  initialLocale: browser ? window.localStorage.getItem('locale') || defaultLocale : defaultLocale,
});

// Set up locale persistence
if (browser) {
  locale.subscribe((value) => {
    if (value) {
      window.localStorage.setItem('locale', value);
    }
  });
}

export { locale, waitLocale };

// Helper function to change language
export function setLanguage(lang: string) {
  locale.set(lang);
}

// Helper function to get available languages
export const availableLanguages = [
  { code: 'en', name: 'English' },
  { code: 'zh', name: '中文' }
];