<template>
  <div class="d-flex">
    <SidebarNav />
    <div class="main-content w-100">
      <h4 class="mb-4">My Appointments</h4>

      <!-- Filters -->
      <div class="row mb-3">
        <div class="col-md-3">
          <input v-model="filterDate" type="date" class="form-control" @change="fetchAppointments" />
        </div>
        <div class="col-md-3">
          <select v-model="filterStatus" class="form-select">
            <option value="">All Status</option>
            <option value="Booked">Booked</option>
            <option value="Completed">Completed</option>
            <option value="Cancelled">Cancelled</option>
          </select>
        </div>
        <div class="col-md-2">
          <button class="btn btn-outline-secondary w-100" @click="clearFilters">Clear</button>
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
                  <th>Patient</th>
                  <th>Age</th>
                  <th>Gender</th>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="appt in filteredAppointments" :key="appt.id">
                  <td>{{ appt.id }}</td>
                  <td>{{ appt.patient_name }}</td>
                  <td>{{ appt.patient_age || '—' }}</td>
                  <td>{{ appt.patient_gender || '—' }}</td>
                  <td>{{ appt.date }}</td>
                  <td>{{ appt.time }}</td>
                  <td>
                    <span class="badge" :class="{
                      'bg-primary': appt.status === 'Booked',
                      'bg-success': appt.status === 'Completed',
                      'bg-danger': appt.status === 'Cancelled'
                    }">{{ appt.status }}</span>
                  </td>
                  <td>
                    <div class="btn-group btn-group-sm" v-if="appt.status === 'Booked'">
                      <button class="btn btn-outline-success" @click="openTreatmentModal(appt)" title="Complete & Add Treatment">✅ Complete</button>
                      <button class="btn btn-outline-danger" @click="cancelAppointment(appt)" title="Cancel">❌ Cancel</button>
                    </div>
                    <span v-else-if="appt.has_treatment" class="text-muted small">Treatment added</span>
                    <span v-else class="text-muted small">—</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Treatment Modal -->
      <div class="modal fade" id="treatmentModal" tabindex="-1" ref="treatmentModal">
        <div class="modal-dialog modal-lg">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Add Treatment — {{ selectedAppt ? selectedAppt.patient_name : '' }}</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
              <div v-if="treatmentError" class="alert alert-danger">{{ treatmentError }}</div>
              <div class="mb-3">
                <label class="form-label">Diagnosis</label>
                <textarea v-model="treatmentForm.diagnosis" class="form-control" rows="2"></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Prescription</label>
                <textarea v-model="treatmentForm.prescription" class="form-control" rows="2"></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Medicines</label>
                <textarea v-model="treatmentForm.medicines" class="form-control" rows="2"></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Tests Done</label>
                <input v-model="treatmentForm.tests_done" type="text" class="form-control" />
              </div>
              <div class="mb-3">
                <label class="form-label">Notes</label>
                <textarea v-model="treatmentForm.notes" class="form-control" rows="2"></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Next Visit Date</label>
                <input v-model="treatmentForm.next_visit" type="date" class="form-control" />
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button type="button" class="btn btn-primary" @click="saveTreatment" :disabled="saving">
                {{ saving ? 'Saving...' : 'Save Treatment' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import SidebarNav from '@/components/SidebarNav.vue'
import { Modal } from 'bootstrap'

export default {
  name: 'DoctorAppointments',
  components: { SidebarNav },
  data() {
    return {
      appointments: [],
      filterDate: '',
      filterStatus: '',
      loading: true,
      saving: false,
      selectedAppt: null,
      treatmentError: '',
      treatmentForm: this.emptyTreatment(),
      bsModal: null
    }
  },
  computed: {
    filteredAppointments() {
      return this.appointments.filter(a => {
        if (this.filterStatus && a.status !== this.filterStatus) return false
        return true
      })
    }
  },
  async created() {
    await this.fetchAppointments()
  },
  mounted() {
    this.bsModal = new Modal(this.$refs.treatmentModal)
  },
  methods: {
    emptyTreatment() {
      return {
        diagnosis: '',
        prescription: '',
        medicines: '',
        tests_done: '',
        notes: '',
        next_visit: ''
      }
    },
    async fetchAppointments() {
      this.loading = true
      try {
        const params = {}
        if (this.filterDate) params.date = this.filterDate
        const res = await axios.get('/api/doctor/appointments', { params })
        this.appointments = res.data
      } catch (err) {
        console.error('Failed to load appointments:', err)
      } finally {
        this.loading = false
      }
    },
    clearFilters() {
      this.filterDate = ''
      this.filterStatus = ''
      this.fetchAppointments()
    },
    openTreatmentModal(appt) {
      this.selectedAppt = appt
      this.treatmentError = ''
      this.treatmentForm = this.emptyTreatment()
      this.bsModal.show()
    },
    async saveTreatment() {
      this.saving = true
      this.treatmentError = ''
      try {
        await axios.post(`/api/doctor/appointments/${this.selectedAppt.id}/treatment`, this.treatmentForm)
        this.bsModal.hide()
        await this.fetchAppointments()
      } catch (err) {
        this.treatmentError = err.response?.data?.message || 'Failed to save treatment'
      } finally {
        this.saving = false
      }
    },
    async cancelAppointment(appt) {
      if (!confirm(`Cancel appointment #${appt.id} with ${appt.patient_name}?`)) return
      try {
        await axios.put(`/api/doctor/appointments/${appt.id}/status`, { status: 'Cancelled' })
        await this.fetchAppointments()
      } catch (err) {
        console.error('Failed to cancel:', err)
      }
    }
  }
}
</script>
