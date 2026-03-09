import { createStore } from 'vuex'
import axios from 'axios'

export default createStore({
    state: {
        token: localStorage.getItem('token') || null,
        user: JSON.parse(localStorage.getItem('user')) || null,
    },

    getters: {
        isAuthenticated: state => !!state.token,
        getUser: state => state.user,
        getRole: state => state.user ? state.user.role : null,
        isAdmin: state => state.user && state.user.role === 'admin',
        isDoctor: state => state.user && state.user.role === 'doctor',
        isPatient: state => state.user && state.user.role === 'patient',
    },

    mutations: {
        SET_TOKEN(state, token) {
            state.token = token
            localStorage.setItem('token', token)
        },
        SET_USER(state, user) {
            state.user = user
            localStorage.setItem('user', JSON.stringify(user))
        },
        LOGOUT(state) {
            state.token = null
            state.user = null
            localStorage.removeItem('token')
            localStorage.removeItem('user')
        }
    },

    actions: {
        async login({ commit }, credentials) {
            const response = await axios.post('/api/auth/login', credentials)
            const { access_token, user } = response.data
            commit('SET_TOKEN', access_token)
            commit('SET_USER', user)
            return user
        },

        async register({ commit }, userData) {
            const response = await axios.post('/api/auth/register', userData)
            return response.data
        },

        logout({ commit }) {
            commit('LOGOUT')
        }
    }
})