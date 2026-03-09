import { createRouter, createWebHistory } from 'vue-router'
import store from '../store'

// Auth Views
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'

// Admin Views
import AdminDashboard from '../views/admin/AdminDashboard.vue'
import AdminDoctors from '../views/admin/AdminDoctors.vue'
import AdminPatients from '../views/admin/AdminPatients.vue'
import AdminAppointments from '../views/admin/AdminAppointments.vue'

// Doctor Views
import DoctorDashboard from '../views/doctor/DoctorDashboard.vue'
import DoctorAppointments from '../views/doctor/DoctorAppointments.vue'
import DoctorPatients from '../views/doctor/DoctorPatients.vue'
import DoctorAvailability from '../views/doctor/DoctorAvailability.vue'

// Patient Views
import PatientDashboard from '../views/patient/PatientDashboard.vue'
import PatientAppointments from '../views/patient/PatientAppointments.vue'
import PatientHistory from '../views/patient/PatientHistory.vue'
import PatientProfile from '../views/patient/PatientProfile.vue'
import BookAppointment from '../views/patient/BookAppointment.vue'

const routes = [
    { path: '/', redirect: '/login' },
    { path: '/login', component: LoginView, meta: { guest: true } },
    { path: '/register', component: RegisterView, meta: { guest: true } },

    // Admin routes
    {
        path: '/admin',
        meta: { requiresAuth: true, role: 'admin' },
        children: [
            { path: '', redirect: '/admin/dashboard' },
            { path: 'dashboard', component: AdminDashboard },
            { path: 'doctors', component: AdminDoctors },
            { path: 'patients', component: AdminPatients },
            { path: 'appointments', component: AdminAppointments },
        ]
    },

    // Doctor routes
    {
        path: '/doctor',
        meta: { requiresAuth: true, role: 'doctor' },
        children: [
            { path: '', redirect: '/doctor/dashboard' },
            { path: 'dashboard', component: DoctorDashboard },
            { path: 'appointments', component: DoctorAppointments },
            { path: 'patients', component: DoctorPatients },
            { path: 'availability', component: DoctorAvailability },
        ]
    },

    // Patient routes
    {
        path: '/patient',
        meta: { requiresAuth: true, role: 'patient' },
        children: [
            { path: '', redirect: '/patient/dashboard' },
            { path: 'dashboard', component: PatientDashboard },
            { path: 'appointments', component: PatientAppointments },
            { path: 'history', component: PatientHistory },
            { path: 'profile', component: PatientProfile },
            { path: 'book', component: BookAppointment },
        ]
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// Navigation Guard
router.beforeEach((to, from, next) => {
    const isAuthenticated = store.getters.isAuthenticated
    const userRole = store.getters.getRole

    if (to.meta.requiresAuth && !isAuthenticated) {
        next('/login')
    } else if (to.meta.guest && isAuthenticated) {
        next(`/${userRole}/dashboard`)
    } else if (to.meta.role && userRole !== to.meta.role) {
        next(`/${userRole}/dashboard`)
    } else {
        next()
    }
})

export default router