<template>
  <div class="d-flex">
    <SidebarNav />
    <div class="main-content w-100">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h4 class="mb-0">My Appointments</h4>
        <router-link to="/patient/book" class="btn btn-primary">+ Book Appointment</router-link>
      </div>

      <!-- Filters -->
      <div class="row mb-3">
        <div class="col-md-3">
          <select v-model="filterStatus" class="form-select">
            <option value="">All Statuses</option>
            <option value="Booked">Booked</option>
            <option value="Completed">Completed</option>
            <option value="Cancelled">Cancelled</option>
          </select>
        </div>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
      </div>

      <div class="card" v-else>
        <div class="card-body">
          <div v-if="filteredAppointments.length === 0" class="text-muted text-center py-3">
            No appointments found.
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
                  <th>Visit Type</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="appt in filteredAppointments" :key="appt.id">
                  <td>{{ appt.id }}</td>
                  <td>{{ appt.doctor_name }}</td>
                  <td>{{ appt.department || '—' }}</td>
                  <td>{{ appt.date }}</td>
                  <td>{{ appt.time }}</td>
                  <td>{{ appt.visit_type }}</td>
                  <td>
                    <span class="badge" :class="{
                      'bg-primary': appt.status === 'Booked',
                      'bg-success': appt.status === 'Completed',
                      'bg-danger': appt.status === 'Cancelled'
                    }">{{ appt.status }}</span>
                  </td>
                  <td>
                    <button
                      v-if="appt.status === 'Booked'"
                      class="btn btn-sm btn-outline-danger"
                      @click="cancelAppointment(appt)"
                    >Cancel</button>
                    <span v-else class="text-muted small">—</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import SidebarNav from '@/components/SidebarNav.vue'

export default {
  name: 'PatientAppointments',
  components: { SidebarNav },
  data() {
    return {
      appointments: [],
      filterStatus: '',
      loading: true
    }
  },
  computed: {
    filteredAppointments() {
      if (!this.filterStatus) return this.appointments
      return this.appointments.filter(a => a.status === this.filterStatus)
    }
  },
  async created() {
    await this.fetchAppointments()
  },
  methods: {
    async fetchAppointments() {
      this.loading = true
      try {
        const res = await axios.get('/api/patient/appointments')
        this.appointments = res.data
      } catch (err) {
        console.error('Failed to load appointments:', err)
      } finally {
        this.loading = false
      }
    },
    async cancelAppointment(appt) {
      if (!confirm(`Cancel appointment #${appt.id} with Dr. ${appt.doctor_name}?`)) return
      try {
        await axios.put(`/api/patient/appointments/${appt.id}/cancel`)
        await this.fetchAppointments()
      } catch (err) {
        alert(err.response?.data?.message || 'Failed to cancel appointment')
      }
    }
  }
}
</script>
