<template>
  <div class="d-flex">
    <SidebarNav />
    <div class="main-content w-100">
      <h4 class="mb-4">All Appointments</h4>

      <!-- Filters -->
      <div class="row mb-3">
        <div class="col-md-3">
          <select v-model="filterStatus" class="form-select" @change="applyFilters">
            <option value="">All Status</option>
            <option value="Booked">Booked</option>
            <option value="Completed">Completed</option>
            <option value="Cancelled">Cancelled</option>
          </select>
        </div>
        <div class="col-md-3">
          <input v-model="filterDate" type="date" class="form-control" @change="applyFilters" />
        </div>
        <div class="col-md-4">
          <input
            v-model="searchText"
            type="text"
            class="form-control"
            placeholder="Search by patient or doctor name..."
            @input="applyFilters"
          />
        </div>
        <div class="col-md-2">
          <button class="btn btn-outline-secondary w-100" @click="clearFilters">Clear Filters</button>
        </div>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
      </div>

      <!-- Appointments Table -->
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
                  <th>Patient</th>
                  <th>Doctor</th>
                  <th>Department</th>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Visit Type</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="appt in filteredAppointments" :key="appt.id">
                  <td>{{ appt.id }}</td>
                  <td>{{ appt.patient_name }}</td>
                  <td>{{ appt.doctor_name }}</td>
                  <td>{{ appt.department || '—' }}</td>
                  <td>{{ appt.date }}</td>
                  <td>{{ appt.time }}</td>
                  <td>{{ appt.visit_type }}</td>
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
          <div class="mt-3 text-muted small" v-if="filteredAppointments.length">
            Showing {{ filteredAppointments.length }} of {{ appointments.length }} appointments
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
  name: 'AdminAppointments',
  components: { SidebarNav },
  data() {
    return {
      appointments: [],
      filterStatus: '',
      filterDate: '',
      searchText: '',
      loading: true
    }
  },
  computed: {
    filteredAppointments() {
      return this.appointments.filter(appt => {
        if (this.filterStatus && appt.status !== this.filterStatus) return false
        if (this.filterDate && appt.date !== this.filterDate) return false
        if (this.searchText) {
          const q = this.searchText.toLowerCase()
          const matchPatient = appt.patient_name && appt.patient_name.toLowerCase().includes(q)
          const matchDoctor = appt.doctor_name && appt.doctor_name.toLowerCase().includes(q)
          if (!matchPatient && !matchDoctor) return false
        }
        return true
      })
    }
  },
  async created() {
    await this.fetchAppointments()
  },
  methods: {
    async fetchAppointments() {
      this.loading = true
      try {
        const res = await axios.get('/api/admin/appointments')
        this.appointments = res.data
      } catch (err) {
        console.error('Failed to load appointments:', err)
      } finally {
        this.loading = false
      }
    },
    applyFilters() {
      // Filters are computed — this is a no-op kept for clarity
    },
    clearFilters() {
      this.filterStatus = ''
      this.filterDate = ''
      this.searchText = ''
    }
  }
}
</script>
