<template>
  <div class="d-flex">
    <SidebarNav />
    <div class="main-content w-100">
      <h4 class="mb-4">Welcome, Dr. {{ dashboard.doctor_name || '...' }}</h4>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
      </div>

      <template v-else>
        <!-- Stats Cards -->
        <div class="row mb-4">
          <div class="col-md-4">
            <div class="stat-card" style="background: linear-gradient(135deg, #2c7be5, #6cb2f7)">
              <p>Today's Appointments</p>
              <h3>{{ dashboard.today_appointments }}</h3>
            </div>
          </div>
          <div class="col-md-4">
            <div class="stat-card" style="background: linear-gradient(135deg, #00d97e, #5cf5b5)">
              <p>This Week</p>
              <h3>{{ dashboard.week_appointments }}</h3>
            </div>
          </div>
          <div class="col-md-4">
            <div class="stat-card" style="background: linear-gradient(135deg, #e63757, #f58ea1)">
              <p>Total Patients</p>
              <h3>{{ dashboard.total_patients }}</h3>
            </div>
          </div>
        </div>

        <!-- Today's Appointments Table -->
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <span>Today's Appointments</span>
            <router-link to="/doctor/appointments" class="btn btn-sm btn-outline-primary">View All</router-link>
          </div>
          <div class="card-body">
            <div v-if="todayAppointments.length === 0" class="text-muted text-center py-3">
              No appointments for today.
            </div>
            <div class="table-responsive" v-else>
              <table class="table table-hover mb-0">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Patient</th>
                    <th>Time</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="appt in todayAppointments" :key="appt.id">
                    <td>{{ appt.id }}</td>
                    <td>{{ appt.patient_name }}</td>
                    <td>{{ appt.time }}</td>
                    <td>
                      <span class="badge" :class="{
                        'bg-primary': appt.status === 'Booked',
                        'bg-success': appt.status === 'Completed',
                        'bg-danger': appt.status === 'Cancelled'
                      }">{{ appt.status }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import SidebarNav from '@/components/SidebarNav.vue'

export default {
  name: 'DoctorDashboard',
  components: { SidebarNav },
  data() {
    return {
      dashboard: {
        doctor_name: '',
        today_appointments: 0,
        week_appointments: 0,
        total_patients: 0
      },
      todayAppointments: [],
      loading: true
    }
  },
  async created() {
    await this.fetchData()
  },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const today = new Date().toISOString().split('T')[0]
        const [dashRes, apptsRes] = await Promise.all([
          axios.get('/api/doctor/dashboard'),
          axios.get('/api/doctor/appointments', { params: { date: today } })
        ])
        this.dashboard = dashRes.data
        this.todayAppointments = apptsRes.data
      } catch (err) {
        console.error('Failed to load dashboard:', err)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
