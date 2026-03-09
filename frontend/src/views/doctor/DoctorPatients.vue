<template>
  <div class="d-flex">
    <SidebarNav />
    <div class="main-content w-100">
      <h4 class="mb-4">My Patients</h4>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
      </div>

      <template v-else>
        <!-- Patients Table -->
        <div class="card mb-4">
          <div class="card-body">
            <div v-if="patients.length === 0" class="text-muted text-center py-3">
              No patients assigned yet.
            </div>
            <div class="table-responsive" v-else>
              <table class="table table-hover mb-0">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Name</th>
                    <th>Age</th>
                    <th>Gender</th>
                    <th>Phone</th>
                    <th>Blood Group</th>
                    <th>Last Visit</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="pat in patients" :key="pat.id" :class="{ 'table-info': selectedPatientId === pat.id }">
                    <td>{{ pat.id }}</td>
                    <td>{{ pat.name || '—' }}</td>
                    <td>{{ pat.age || '—' }}</td>
                    <td>{{ pat.gender || '—' }}</td>
                    <td>{{ pat.phone || '—' }}</td>
                    <td>{{ pat.blood_group || '—' }}</td>
                    <td>{{ pat.last_appointment || '—' }}</td>
                    <td>
                      <button class="btn btn-sm btn-outline-primary" @click="viewHistory(pat)">
                        📋 View History
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Patient History Section -->
        <div class="card" v-if="selectedPatient">
          <div class="card-header d-flex justify-content-between align-items-center">
            <span>History — {{ selectedPatient.name }} ({{ selectedPatient.age || '?' }} yrs, {{ selectedPatient.gender || '?' }})</span>
            <button class="btn btn-sm btn-outline-secondary" @click="closeHistory">Close</button>
          </div>
          <div class="card-body">
            <div v-if="historyLoading" class="text-center py-3">
              <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
            </div>
            <div v-else-if="history.length === 0" class="text-muted text-center py-3">
              No visit history found.
            </div>
            <div v-else>
              <div class="accordion" id="historyAccordion">
                <div class="accordion-item" v-for="(visit, idx) in history" :key="visit.appointment_id">
                  <h2 class="accordion-header">
                    <button
                      class="accordion-button collapsed"
                      type="button"
                      data-bs-toggle="collapse"
                      :data-bs-target="'#visit-' + visit.appointment_id"
                    >
                      {{ visit.date }} — {{ visit.time }} —
                      <span class="badge ms-2" :class="{
                        'bg-primary': visit.status === 'Booked',
                        'bg-success': visit.status === 'Completed',
                        'bg-danger': visit.status === 'Cancelled'
                      }">{{ visit.status }}</span>
                    </button>
                  </h2>
                  <div :id="'visit-' + visit.appointment_id" class="accordion-collapse collapse" data-bs-parent="#historyAccordion">
                    <div class="accordion-body">
                      <div v-if="visit.treatment">
                        <div class="row">
                          <div class="col-md-6 mb-2"><strong>Diagnosis:</strong> {{ visit.treatment.diagnosis || '—' }}</div>
                          <div class="col-md-6 mb-2"><strong>Prescription:</strong> {{ visit.treatment.prescription || '—' }}</div>
                          <div class="col-md-6 mb-2"><strong>Medicines:</strong> {{ visit.treatment.medicines || '—' }}</div>
                          <div class="col-md-6 mb-2"><strong>Tests Done:</strong> {{ visit.treatment.tests_done || '—' }}</div>
                          <div class="col-md-6 mb-2"><strong>Notes:</strong> {{ visit.treatment.notes || '—' }}</div>
                          <div class="col-md-6 mb-2"><strong>Next Visit:</strong> {{ visit.treatment.next_visit || '—' }}</div>
                        </div>
                      </div>
                      <div v-else class="text-muted">No treatment record for this visit.</div>
                    </div>
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
  name: 'DoctorPatients',
  components: { SidebarNav },
  data() {
    return {
      patients: [],
      loading: true,
      selectedPatientId: null,
      selectedPatient: null,
      history: [],
      historyLoading: false
    }
  },
  async created() {
    await this.fetchPatients()
  },
  methods: {
    async fetchPatients() {
      this.loading = true
      try {
        const res = await axios.get('/api/doctor/patients')
        this.patients = res.data
      } catch (err) {
        console.error('Failed to load patients:', err)
      } finally {
        this.loading = false
      }
    },
    async viewHistory(pat) {
      this.selectedPatientId = pat.id
      this.historyLoading = true
      this.history = []
      try {
        const res = await axios.get(`/api/doctor/patients/${pat.id}/history`)
        this.selectedPatient = res.data.patient
        this.history = res.data.history
      } catch (err) {
        console.error('Failed to load history:', err)
      } finally {
        this.historyLoading = false
      }
    },
    closeHistory() {
      this.selectedPatientId = null
      this.selectedPatient = null
      this.history = []
    }
  }
}
</script>
