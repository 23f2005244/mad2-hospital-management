<template>
  <div class="d-flex">
    <SidebarNav />
    <div class="main-content w-100">
      <h4 class="mb-4">My Profile</h4>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
      </div>

      <template v-else>
        <div v-if="successMsg" class="alert alert-success alert-dismissible fade show">
          {{ successMsg }}
          <button type="button" class="btn-close" @click="successMsg = ''"></button>
        </div>
        <div v-if="errorMsg" class="alert alert-danger alert-dismissible fade show">
          {{ errorMsg }}
          <button type="button" class="btn-close" @click="errorMsg = ''"></button>
        </div>

        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <span>Profile Details</span>
            <button v-if="!editing" class="btn btn-sm btn-outline-primary" @click="editing = true">Edit</button>
            <button v-else class="btn btn-sm btn-outline-secondary" @click="cancelEdit">Cancel</button>
          </div>
          <div class="card-body">
            <!-- View Mode -->
            <div v-if="!editing">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label text-muted small">Username</label>
                  <p class="mb-0">{{ profile.username }}</p>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label text-muted small">Email</label>
                  <p class="mb-0">{{ profile.email }}</p>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label text-muted small">Full Name</label>
                  <p class="mb-0">{{ profile.name || '—' }}</p>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label text-muted small">Age</label>
                  <p class="mb-0">{{ profile.age || '—' }}</p>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label text-muted small">Gender</label>
                  <p class="mb-0">{{ profile.gender || '—' }}</p>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label text-muted small">Phone</label>
                  <p class="mb-0">{{ profile.phone || '—' }}</p>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label text-muted small">Blood Group</label>
                  <p class="mb-0">{{ profile.blood_group || '—' }}</p>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label text-muted small">Address</label>
                  <p class="mb-0">{{ profile.address || '—' }}</p>
                </div>
              </div>
            </div>

            <!-- Edit Mode -->
            <div v-else>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Full Name</label>
                  <input v-model="form.name" type="text" class="form-control" />
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Age</label>
                  <input v-model.number="form.age" type="number" class="form-control" min="0" />
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Gender</label>
                  <select v-model="form.gender" class="form-select">
                    <option value="">Select Gender</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Phone</label>
                  <input v-model="form.phone" type="text" class="form-control" />
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Blood Group</label>
                  <select v-model="form.blood_group" class="form-select">
                    <option value="">Select Blood Group</option>
                    <option v-for="bg in bloodGroups" :key="bg" :value="bg">{{ bg }}</option>
                  </select>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Address</label>
                  <textarea v-model="form.address" class="form-control" rows="2"></textarea>
                </div>
              </div>
              <div class="text-end">
                <button class="btn btn-primary" @click="saveProfile" :disabled="saving">
                  {{ saving ? 'Saving...' : 'Save Changes' }}
                </button>
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
  name: 'PatientProfile',
  components: { SidebarNav },
  data() {
    return {
      profile: {},
      form: {},
      editing: false,
      loading: true,
      saving: false,
      successMsg: '',
      errorMsg: '',
      bloodGroups: ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    }
  },
  async created() {
    await this.fetchProfile()
  },
  methods: {
    async fetchProfile() {
      this.loading = true
      try {
        const res = await axios.get('/api/patient/profile')
        this.profile = res.data
      } catch (err) {
        console.error('Failed to load profile:', err)
      } finally {
        this.loading = false
      }
    },
    cancelEdit() {
      this.editing = false
      this.form = {}
    },
    async saveProfile() {
      this.saving = true
      this.successMsg = ''
      this.errorMsg = ''
      try {
        await axios.put('/api/patient/profile', {
          name: this.form.name,
          age: this.form.age,
          gender: this.form.gender,
          phone: this.form.phone,
          address: this.form.address,
          blood_group: this.form.blood_group
        })
        this.successMsg = 'Profile updated successfully!'
        this.editing = false
        await this.fetchProfile()
      } catch (err) {
        this.errorMsg = err.response?.data?.message || 'Failed to update profile'
      } finally {
        this.saving = false
      }
    }
  },
  watch: {
    editing(val) {
      if (val) {
        this.form = {
          name: this.profile.name || '',
          age: this.profile.age || '',
          gender: this.profile.gender || '',
          phone: this.profile.phone || '',
          address: this.profile.address || '',
          blood_group: this.profile.blood_group || ''
        }
      }
    }
  }
}
</script>
