<template>
  <div class="d-flex">
    <SidebarNav />
    <div class="main-content w-100">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h4 class="mb-0">Treatment History</h4>
        <button class="btn btn-outline-primary" @click="exportCSV" :disabled="exporting">
          {{ exporting ? 'Exporting...' : '📤 Export CSV' }}
        </button>
      </div>

      <div v-if="exportMsg" class="alert alert-info alert-dismissible fade show">
        {{ exportMsg }}
        <button type="button" class="btn-close" @click="exportMsg = ''"></button>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
      </div>

      <template v-else>
        <div v-if="history.length === 0" class="text-muted text-center py-5">
          No completed visits yet.
        </div>

        <div class="accordion" id="historyAccordion" v-else>
          <div class="accordion-item" v-for="visit in history" :key="visit.appointment_id">
            <h2 class="accordion-header">
              <button
                class="accordion-button collapsed"
                type="button"
                data-bs-toggle="collapse"
                :data-bs-target="'#hist-' + visit.appointment_id"
              >
                <div class="d-flex w-100 justify-content-between me-3">
                  <span><strong>{{ visit.date }}</strong> — Dr. {{ visit.doctor_name }} ({{ visit.department || 'N/A' }})</span>
                  <span class="text-muted small">{{ visit.time }}</span>
                </div>
              </button>
            </h2>
            <div :id="'hist-' + visit.appointment_id" class="accordion-collapse collapse" data-bs-parent="#historyAccordion">
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
      </template>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import SidebarNav from '@/components/SidebarNav.vue'

export default {
  name: 'PatientHistory',
  components: { SidebarNav },
  data() {
    return {
      history: [],
      loading: true,
      exporting: false,
      exportMsg: ''
    }
  },
  async created() {
    await this.fetchHistory()
  },
  methods: {
    async fetchHistory() {
      this.loading = true
      try {
        const res = await axios.get('/api/patient/history')
        this.history = res.data
      } catch (err) {
        console.error('Failed to load history:', err)
      } finally {
        this.loading = false
      }
    },
    async exportCSV() {
      this.exporting = true
      this.exportMsg = ''
      try {
        const res = await axios.post('/api/patient/export-csv')
        this.exportMsg = res.data.message || 'CSV export started. Check your email shortly.'
      } catch (err) {
        this.exportMsg = err.response?.data?.message || 'Export failed'
      } finally {
        this.exporting = false
      }
    }
  }
}
</script>
