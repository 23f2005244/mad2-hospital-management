import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import axios from 'axios'

// Set base URL for all axios requests
axios.defaults.baseURL = 'http://localhost:5001'

// Add JWT token to every request automatically
axios.interceptors.request.use(config => {
    const token = localStorage.getItem('token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

// Handle 401 errors globally
axios.interceptors.response.use(
    response => response,
    error => {
        if (error.response && error.response.status === 401) {
            localStorage.clear()
            router.push('/login')
        }
        return Promise.reject(error)
    }
)

const app = createApp(App)
app.use(router)
app.use(store)
app.mount('#app')