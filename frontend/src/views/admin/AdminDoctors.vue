<template>
  <div class="d-flex">
    <SidebarNav />
    <div class="main-content w-100">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h4 class="mb-0">Manage Doctors</h4>
        <button class="btn btn-primary" @click="openAddModal">+ Add Doctor</button>
      </div>

      <!-- Search -->
      <div class="mb-3">
        <input
          v-model="searchQuery"
          type="text"
          class="form-control"
          placeholder="Search doctors by name or specialization..."
          @input="handleSearch"
        />
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
      </div>

      <!-- Doctors Table -->
      <div class="card" v-else>
        <div class="card-body">
          <div v-if="doctors.length === 0" class="text-muted text-center py-3">
            No doctors found.
          </div>
          <div class="table-responsive" v-else>
            <table class="table table-hover mb-0">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Name</th>
                  <th>Username</th>
                  <th>Email</th>
                  <th>Specialization</th>
                  <th>Department</th>
                  <th>Experience</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="doc in doctors" :key="doc.id" :class="{ 'table-danger': doc.is_blacklisted }">
                  <td>{{ doc.id }}</td>
                  <td>{{ doc.name }}</td>
                  <td>{{ doc.username }}</td>
                  <td>{{ doc.email }}</td>
                  <td>{{ doc.specialization }}</td>
                  <td>{{ doc.department || '—' }}</td>
                  <td>{{ doc.experience_years ? doc.experience_years + ' yrs' : '—' }}</td>
                  <td>
                    <span class="badge" :class="doc.is_blacklisted ? 'bg-danger' : 'bg-success'">
                      {{ doc.is_blacklisted ? 'Blacklisted' : 'Active' }}
                    </span>
                  </td>
                  <td>
                    <div class="btn-group btn-group-sm">
                      <button class="btn btn-outline-primary" @click="openEditModal(doc)" title="Edit">✏️</button>
                      <button
                        class="btn"
                        :class="doc.is_blacklisted ? 'btn-outline-success' : 'btn-outline-warning'"
                        @click="toggleBlacklist(doc)"
                        :title="doc.is_blacklisted ? 'Unblacklist' : 'Blacklist'"
                      >{{ doc.is_blacklisted ? '✅' : '🚫' }}</button>
                      <button class="btn btn-outline-danger" @click="deleteDoctor(doc)" title="Delete">🗑️</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Add / Edit Modal -->
      <div class="modal fade" id="doctorModal" tabindex="-1" ref="doctorModal">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">{{ isEditing ? 'Edit Doctor' : 'Add Doctor' }}</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
              <div v-if="modalError" class="alert alert-danger">{{ modalError }}</div>

              <!-- Only show login fields when adding -->
              <template v-if="!isEditing">
                <div class="mb-3">
                  <label class="form-label">Username</label>
                  <input v-model="form.username" type="text" class="form-control" required />
                </div>
                <div class="mb-3">
                  <label class="form-label">Email</label>
                  <input v-model="form.email" type="email" class="form-control" required />
                </div>
                <div class="mb-3">
                  <label class="form-label">Password</label>
                  <input v-model="form.password" type="password" class="form-control" required />
                </div>
              </template>

              <div class="mb-3">
                <label class="form-label">Full Name</label>
                <input v-model="form.name" type="text" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Specialization</label>
                <input v-model="form.specialization" type="text" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Department</label>
                <select v-model="form.department_id" class="form-select">
                  <option value="">Select Department</option>
                  <option v-for="dept in departments" :key="dept.id" :value="dept.id">{{ dept.name }}</option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label">Experience (years)</label>
                <input v-model.number="form.experience_years" type="number" class="form-control" min="0" />
              </div>
              <div class="mb-3">
                <label class="form-label">Qualification</label>
                <input v-model="form.qualification" type="text" class="form-control" />
              </div>

              <!-- Email & password change when editing -->
              <template v-if="isEditing">
                <div class="mb-3">
                  <label class="form-label">Email</label>
                  <input v-model="form.email" type="email" class="form-control" />
                </div>
                <div class="mb-3">
                  <label class="form-label">New Password (leave blank to keep)</label>
                  <input v-model="form.password" type="password" class="form-control" />
                </div>
              </template>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button type="button" class="btn btn-primary" @click="saveDoctor" :disabled="saving">
                {{ saving ? 'Saving...' : (isEditing ? 'Update' : 'Add Doctor') }}
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
  name: 'AdminDoctors',
  components: { SidebarNav },
  data() {
    return {
      doctors: [],
      departments: [],
      searchQuery: '',
      loading: true,
      saving: false,
      isEditing: false,
      editingId: null,
      modalError: '',
      form: this.emptyForm(),
      bsModal: null
    }
  },
  async created() {
    await this.fetchData()
  },
  mounted() {
    this.bsModal = new Modal(this.$refs.doctorModal)
  },
  methods: {
    emptyForm() {
      return {
        username: '',
        email: '',
        password: '',
        name: '',
        specialization: '',
        department_id: '',
        experience_years: '',
        qualification: ''
      }
    },
    async fetchData() {
      this.loading = true
      try {
        const [docRes, deptRes] = await Promise.all([
          axios.get('/api/admin/doctors'),
          axios.get('/api/admin/departments')
        ])
        this.doctors = docRes.data
        this.departments = deptRes.data
      } catch (err) {
        console.error('Failed to load doctors:', err)
      } finally {
        this.loading = false
      }
    },
    handleSearch() {
      if (this.searchTimer) clearTimeout(this.searchTimer)
      this.searchTimer = setTimeout(async () => {
        if (this.searchQuery.trim()) {
          try {
            const res = await axios.get('/api/admin/search/doctors', { params: { q: this.searchQuery } })
            this.doctors = res.data
          } catch (err) {
            console.error('Search failed:', err)
          }
        } else {
          await this.fetchData()
        }
      }, 300)
    },
    openAddModal() {
      this.isEditing = false
      this.editingId = null
      this.modalError = ''
      this.form = this.emptyForm()
      this.bsModal.show()
    },
    openEditModal(doc) {
      this.isEditing = true
      this.editingId = doc.id
      this.modalError = ''
      this.form = {
        username: doc.username,
        email: doc.email,
        password: '',
        name: doc.name,
        specialization: doc.specialization,
        department_id: doc.department_id || '',
        experience_years: doc.experience_years || '',
        qualification: doc.qualification || ''
      }
      this.bsModal.show()
    },
    async saveDoctor() {
      this.saving = true
      this.modalError = ''
      try {
        if (this.isEditing) {
          const payload = {
            name: this.form.name,
            specialization: this.form.specialization,
            department_id: this.form.department_id || null,
            experience_years: this.form.experience_years || null,
            qualification: this.form.qualification || null,
            email: this.form.email
          }
          if (this.form.password) payload.password = this.form.password
          await axios.put(`/api/admin/doctors/${this.editingId}`, payload)
        } else {
          await axios.post('/api/admin/doctors', this.form)
        }
        this.bsModal.hide()
        await this.fetchData()
      } catch (err) {
        this.modalError = err.response?.data?.message || 'Operation failed'
      } finally {
        this.saving = false
      }
    },
    async toggleBlacklist(doc) {
      try {
        await axios.put(`/api/admin/doctors/${doc.id}/blacklist`)
        await this.fetchData()
      } catch (err) {
        console.error('Blacklist toggle failed:', err)
      }
    },
    async deleteDoctor(doc) {
      if (!confirm(`Are you sure you want to delete Dr. ${doc.name}?`)) return
      try {
        await axios.delete(`/api/admin/doctors/${doc.id}`)
        await this.fetchData()
      } catch (err) {
        console.error('Delete failed:', err)
      }
    }
  }
}
</script>
