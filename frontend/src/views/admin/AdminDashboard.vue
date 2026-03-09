<template>
  <div class="d-flex">
    <SidebarNav />
    <div class="main-content w-100">
      <h4 class="mb-4">Admin Dashboard</h4>

        <!-- Admin Actions -->
        <div class="mb-4">
          <button class="btn btn-outline-primary me-2" @click="triggerDailyReminders" :disabled="actionLoading">
            {{ actionLoading && actionType === 'daily' ? 'Sending...' : 'Send Daily Reminders' }}
          </button>
          <button class="btn btn-outline-success me-2" @click="triggerMonthlyReport" :disabled="actionLoading">
            {{ actionLoading && actionType === 'monthly' ? 'Sending...' : 'Send Monthly Report' }}
          </button>
          <button class="btn btn-outline-info" @click="exportDoctorsCSV" :disabled="actionLoading">
            {{ actionLoading && actionType === 'csv' ? 'Exporting...' : 'Export Doctors CSV' }}
          </button>
          <div v-if="actionMsg" class="alert alert-info mt-3">{{ actionMsg }}</div>
        </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
      </div>

      <template v-else>
        <!-- Stats Cards -->
        <div class="row mb-4">
          <div class="col-md-4 col-lg-2">
            <div class="stat-card" style="background: linear-gradient(135deg, #2c7be5, #6cb2f7)">
              <p>Total Doctors</p>
              <h3>{{ stats.total_doctors }}</h3>
            </div>
          </div>
          <div class="col-md-4 col-lg-2">
            <div class="stat-card" style="background: linear-gradient(135deg, #00d97e, #5cf5b5)">
              <p>Total Patients</p>
              <h3>{{ stats.total_patients }}</h3>
            </div>
          </div>
          <div class="col-md-4 col-lg-2">
            <div class="stat-card" style="background: linear-gradient(135deg, #e63757, #f58ea1)">
              <p>Total Appointments</p>
              <h3>{{ stats.total_appointments }}</h3>
            </div>
          </div>
          <div class="col-md-4 col-lg-2">
            <div class="stat-card" style="background: linear-gradient(135deg, #f6c343, #f9dc8c)">
              <p>Booked</p>
              <h3>{{ stats.booked_appointments }}</h3>
            </div>
          </div>
          <div class="col-md-4 col-lg-2">
            <div class="stat-card" style="background: linear-gradient(135deg, #27bcfd, #7dd8fe)">
              <p>Completed</p>
              <h3>{{ stats.completed_appointments }}</h3>
            </div>
          </div>
          <div class="col-md-4 col-lg-2">
            <div class="stat-card" style="background: linear-gradient(135deg, #6b5eae, #a89bd9)">
              <p>Cancelled</p>
              <h3>{{ stats.cancelled_appointments }}</h3>
            </div>
          </div>
        </div>

        <!-- Recent Appointments -->
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <span>Recent Appointments</span>
            <router-link to="/admin/appointments" class="btn btn-sm btn-outline-primary">View All</router-link>
          </div>
          <div class="card-body">
            <div v-if="appointments.length === 0" class="text-muted text-center py-3">
              No appointments found.
            </div>
            <div class="table-responsive" v-else>
              <table class="table table-hover mb-0">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Patient</th>
                    <th>Doctor</th>
                    <th>Department</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="appt in recentAppointments" :key="appt.id">
                    <td>{{ appt.id }}</td>
                    <td>{{ appt.patient_name }}</td>
                    <td>{{ appt.doctor_name }}</td>
                    <td>{{ appt.department || '—' }}</td>
                    <td>{{ appt.date }}</td>
                    <td>{{ appt.time }}</td>
                    <td>
                      <span
                        class="badge"
                        :class="{
                          'bg-primary': appt.status === 'Booked',
                          'bg-success': appt.status === 'Completed',
                          'bg-danger': appt.status === 'Cancelled'
                        }"
                      >{{ appt.status }}</span>
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
  name: 'AdminDashboard',
  components: { SidebarNav },
  data() {
    return {
      stats: {
        total_doctors: 0,
        total_patients: 0,
        total_appointments: 0,
        booked_appointments: 0,
        completed_appointments: 0,
        cancelled_appointments: 0
      },
      appointments: [],
      loading: true
        ,actionLoading: false
        ,actionType: ''
        ,actionMsg: ''
    }
  },
  computed: {
    recentAppointments() {
      return this.appointments.slice(0, 10)
    }
  },
  async created() {
    await this.fetchData()
  },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const [statsRes, apptsRes] = await Promise.all([
          axios.get('/api/admin/dashboard'),
          axios.get('/api/admin/appointments')
        ])
        this.stats = statsRes.data
        this.appointments = apptsRes.data
      } catch (err) {
        console.error('Failed to load dashboard:', err)
      } finally {
        this.loading = false
      }
    }
      ,async triggerDailyReminders() {
        this.actionLoading = true;
        this.actionType = 'daily';
        this.actionMsg = '';
        try {
          const res = await axios.post('/api/admin/send-daily-reminders');
          this.actionMsg = res.data.message || 'Daily reminders sent.';
        } catch (err) {
          this.actionMsg = 'Failed to send daily reminders.';
        } finally {
          this.actionLoading = false;
          this.actionType = '';
        }
      }
      ,async triggerMonthlyReport() {
        this.actionLoading = true;
        this.actionType = 'monthly';
        this.actionMsg = '';
        try {
          const res = await axios.post('/api/admin/send-monthly-report');
          this.actionMsg = res.data.message || 'Monthly report sent.';
        } catch (err) {
          this.actionMsg = 'Failed to send monthly report.';
        } finally {
          this.actionLoading = false;
          this.actionType = '';
        }
      }
      ,async exportDoctorsCSV() {
        this.actionLoading = true;
        this.actionType = 'csv';
        this.actionMsg = '';
        try {
          const res = await axios.post('/api/admin/export-doctors-csv');
          this.actionMsg = res.data.message || 'Doctors CSV export started.';
        } catch (err) {
          this.actionMsg = 'Failed to export doctors CSV.';
        } finally {
          this.actionLoading = false;
          this.actionType = '';
        }
      }
  }
}
</script>
