<template>
  <div class="d-flex">
    <SidebarNav />
    <div class="main-content w-100">
      <h4 class="mb-4">Manage Patients</h4>

      <!-- Search -->
      <div class="mb-3">
        <input
          v-model="searchQuery"
          type="text"
          class="form-control"
          placeholder="Search patients by name or phone..."
          @input="handleSearch"
        />
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
      </div>

      <!-- Patients Table -->
      <div class="card" v-else>
        <div class="card-body">
          <div v-if="patients.length === 0" class="text-muted text-center py-3">
            No patients found.
          </div>
          <div class="table-responsive" v-else>
            <table class="table table-hover mb-0">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Name</th>
                  <th>Username</th>
                  <th>Email</th>
                  <th>Age</th>
                  <th>Gender</th>
                  <th>Phone</th>
                  <th>Blood Group</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="pat in patients" :key="pat.id" :class="{ 'table-danger': pat.is_blacklisted }">
                  <td>{{ pat.id }}</td>
                  <td>{{ pat.name || '—' }}</td>
                  <td>{{ pat.username }}</td>
                  <td>{{ pat.email }}</td>
                  <td>{{ pat.age || '—' }}</td>
                  <td>{{ pat.gender || '—' }}</td>
                  <td>{{ pat.phone || '—' }}</td>
                  <td>{{ pat.blood_group || '—' }}</td>
                  <td>
                    <span class="badge" :class="pat.is_blacklisted ? 'bg-danger' : 'bg-success'">
                      {{ pat.is_blacklisted ? 'Blacklisted' : 'Active' }}
                    </span>
                  </td>
                  <td>
                    <div class="btn-group btn-group-sm">
                      <button class="btn btn-outline-primary" @click="openEditModal(pat)" title="Edit">✏️</button>
                      <button
                        class="btn"
                        :class="pat.is_blacklisted ? 'btn-outline-success' : 'btn-outline-warning'"
                        @click="toggleBlacklist(pat)"
                        :title="pat.is_blacklisted ? 'Unblacklist' : 'Blacklist'"
                      >{{ pat.is_blacklisted ? '✅' : '🚫' }}</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Edit Modal -->
      <div class="modal fade" id="patientModal" tabindex="-1" ref="patientModal">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Edit Patient</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
              <div v-if="modalError" class="alert alert-danger">{{ modalError }}</div>
              <div class="mb-3">
                <label class="form-label">Full Name</label>
                <input v-model="form.name" type="text" class="form-control" />
              </div>
              <div class="mb-3">
                <label class="form-label">Age</label>
                <input v-model.number="form.age" type="number" class="form-control" min="0" />
              </div>
              <div class="mb-3">
                <label class="form-label">Gender</label>
                <select v-model="form.gender" class="form-select">
                  <option value="">Select Gender</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label">Phone</label>
                <input v-model="form.phone" type="text" class="form-control" />
              </div>
              <div class="mb-3">
                <label class="form-label">Address</label>
                <textarea v-model="form.address" class="form-control" rows="2"></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Blood Group</label>
                <select v-model="form.blood_group" class="form-select">
                  <option value="">Select Blood Group</option>
                  <option v-for="bg in bloodGroups" :key="bg" :value="bg">{{ bg }}</option>
                </select>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button type="button" class="btn btn-primary" @click="savePatient" :disabled="saving">
                {{ saving ? 'Saving...' : 'Update' }}
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
  name: 'AdminPatients',
  components: { SidebarNav },
  data() {
    return {
      patients: [],
      searchQuery: '',
      loading: true,
      saving: false,
      editingId: null,
      modalError: '',
      form: {
        name: '',
        age: '',
        gender: '',
        phone: '',
        address: '',
        blood_group: ''
      },
      bloodGroups: ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
      bsModal: null
    }
  },
  async created() {
    await this.fetchPatients()
  },
  mounted() {
    this.bsModal = new Modal(this.$refs.patientModal)
  },
  methods: {
    async fetchPatients() {
      this.loading = true
      try {
        const res = await axios.get('/api/admin/patients')
        this.patients = res.data
      } catch (err) {
        console.error('Failed to load patients:', err)
      } finally {
        this.loading = false
      }
    },
    handleSearch() {
      if (this.searchTimer) clearTimeout(this.searchTimer)
      this.searchTimer = setTimeout(async () => {
        if (this.searchQuery.trim()) {
          try {
            const res = await axios.get('/api/admin/search/patients', { params: { q: this.searchQuery } })
            this.patients = res.data
          } catch (err) {
            console.error('Search failed:', err)
          }
        } else {
          await this.fetchPatients()
        }
      }, 300)
    },
    openEditModal(pat) {
      this.editingId = pat.id
      this.modalError = ''
      this.form = {
        name: pat.name || '',
        age: pat.age || '',
        gender: pat.gender || '',
        phone: pat.phone || '',
        address: pat.address || '',
        blood_group: pat.blood_group || ''
      }
      this.bsModal.show()
    },
    async savePatient() {
      this.saving = true
      this.modalError = ''
      try {
        await axios.put(`/api/admin/patients/${this.editingId}`, this.form)
        this.bsModal.hide()
        await this.fetchPatients()
      } catch (err) {
        this.modalError = err.response?.data?.message || 'Update failed'
      } finally {
        this.saving = false
      }
    },
    async toggleBlacklist(pat) {
      try {
        await axios.put(`/api/admin/patients/${pat.id}/blacklist`)
        await this.fetchPatients()
      } catch (err) {
        console.error('Blacklist toggle failed:', err)
      }
    }
  }
}
</script>
