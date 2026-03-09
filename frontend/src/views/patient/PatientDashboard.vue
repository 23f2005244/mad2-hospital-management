<template>
  <div class="d-flex">
    <SidebarNav />
    <div class="main-content w-100">
      <h4 class="mb-4">Welcome, {{ dashboard.patient_name || '...' }}</h4>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
      </div>

      <template v-else>
        <!-- Export CSV Alert -->
        <div v-if="exportMsg" class="alert alert-info alert-dismissible fade show">
          {{ exportMsg }}
          <button type="button" class="btn-close" @click="exportMsg = ''"></button>
        </div>

        <!-- Stats -->
        <div class="row mb-4">
          <div class="col-md-3">
            <div class="stat-card" style="background: linear-gradient(135deg, #2c7be5, #6cb2f7)">
              <p>Upcoming Appointments</p>
              <h3>{{ dashboard.total_upcoming }}</h3>
            </div>
          </div>
          <div class="col-md-3">
            <div class="stat-card" style="background: linear-gradient(135deg, #00d97e, #5cf5b5)">
              <p>Past Appointments</p>
              <h3>{{ dashboard.total_past }}</h3>
            </div>
          </div>
          <div class="col-md-3">
            <div class="stat-card" style="background: linear-gradient(135deg, #e63757, #f58ea1)">
              <p>Departments</p>
              <h3>{{ dashboard.departments ? dashboard.departments.length : 0 }}</h3>
            </div>
          </div>
          <div class="col-md-3">
            <div class="stat-card clickable" style="background: linear-gradient(135deg, #6b5eae, #a89bd9); cursor: pointer;" @click="exportCSV">
              <p>{{ exporting ? 'Exporting...' : '📤 Export CSV' }}</p>
              <h3><small style="font-size: 14px;">Treatment History</small></h3>
            </div>
          </div>
        </div>

        <!-- Upcoming Appointments -->
        <div class="card mb-4">
          <div class="card-header d-flex justify-content-between align-items-center">
            <span>Upcoming Appointments</span>
            <router-link to="/patient/book" class="btn btn-sm btn-primary">+ Book Appointment</router-link>
          </div>
          <div class="card-body">
            <div v-if="dashboard.upcoming_appointments.length === 0" class="text-muted text-center py-3">
              No upcoming appointments.
            </div>
            <div class="table-responsive" v-else>
              <table class="table table-hover mb-0">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Doctor</th>
                    <th>Department</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="appt in dashboard.upcoming_appointments" :key="appt.id">
                    <td>{{ appt.id }}</td>
                    <td>{{ appt.doctor_name }}</td>
                    <td>{{ appt.department || '—' }}</td>
                    <td>{{ appt.date }}</td>
                    <td>{{ appt.time }}</td>
                    <td><span class="badge bg-primary">{{ appt.status }}</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Departments -->
        <div class="card">
          <div class="card-header">Departments</div>
          <div class="card-body">
            <div v-if="!dashboard.departments || dashboard.departments.length === 0" class="text-muted text-center py-3">
              No departments found.
            </div>
            <div class="row" v-else>
              <div class="col-md-4 mb-3" v-for="dept in dashboard.departments" :key="dept.id">
                <div class="card h-100">
                  <div class="card-body">
                    <h6 class="card-title">{{ dept.name }}</h6>
                    <p class="card-text text-muted small">{{ dept.description || 'No description' }}</p>
                  </div>
                </div>
              </div>
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
  name: 'PatientDashboard',
  components: { SidebarNav },
  data() {
    return {
      dashboard: {
        patient_name: '',
        upcoming_appointments: [],
        total_upcoming: 0,
        total_past: 0,
        departments: []
      },
      loading: true,
      exporting: false,
      exportMsg: ''
    }
  },
  async created() {
    await this.fetchDashboard()
  },
  methods: {
    async fetchDashboard() {
      this.loading = true
      try {
        const res = await axios.get('/api/patient/dashboard')
        this.dashboard = res.data
      } catch (err) {
        console.error('Failed to load dashboard:', err)
      } finally {
        this.loading = false
      }
    },
    async exportCSV() {
      if (this.exporting) return
      this.exporting = true
      this.exportMsg = ''
      try {
        const res = await axios.post('/api/patient/export-csv')
        this.exportMsg = res.data.message || 'CSV export started. You will receive an email shortly.'
      } catch (err) {
        this.exportMsg = err.response?.data?.message || 'Export failed. Please try again.'
      } finally {
        this.exporting = false
      }
    }
  }
}
</script>
