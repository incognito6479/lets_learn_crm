import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import i18n from './i18n'
import axios from 'axios'

// Centralized API Base URL configuration
axios.defaults.baseURL = import.meta.env.VITE_API_URL || ''

const app = createApp(App)
app.use(router)
app.use(i18n)
app.mount('#app')
