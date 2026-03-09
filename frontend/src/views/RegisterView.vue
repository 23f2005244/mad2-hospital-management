<template>
  <div class="auth-wrapper">
    <div class="auth-card">
      <div class="auth-header">
        <h2>🏥 Hospital Management</h2>
        <p>Create your patient account</p>
      </div>

      <div v-if="error" class="alert alert-danger">{{ error }}</div>
      <div v-if="success" class="alert alert-success">{{ success }}</div>

      <form @submit.prevent="handleRegister">
        <div class="row">
          <div class="col-md-6 mb-3">
            <label class="form-label">Full Name *</label>
            <input v-model="form.name" type="text" class="form-control" required />
          </div>
          <div class="col-md-6 mb-3">
            <label class="form-label">Username *</label>
            <input v-model="form.username" type="text" class="form-control" required />
          </div>
        </div>

        <div class="mb-3">
          <label class="form-label">Email *</label>
          <input v-model="form.email" type="email" class="form-control" required />
        </div>

        <div class="mb-3">
          <label class="form-label">Password *</label>
          <input v-model="form.password" type="password" class="form-control" required />
        </div>

        <div class="row">
          <div class="col-md-6 mb-3">
            <label class="form-label">Age</label>
            <input v-model="form.age" type="number" class="form-control" />
          </div>
          <div class="col-md-6 mb-3">
            <label class="form-label">Gender</label>
            <select v-model="form.gender" class="form-select">
              <option value="">Select</option>
              <option>Male</option>
              <option>Female</option>
              <option>Other</option>
            </select>
          </div>
        </div>

        <div class="row">
          <div class="col-md-6 mb-3">
            <label class="form-label">Phone</label>
            <input v-model="form.phone" type="text" class="form-control" />
          </div>
          <div class="col-md-6 mb-3">
            <label class="form-label">Blood Group</label>
            <select v-model="form.blood_group" class="form-select">
              <option value="">Select</option>
              <option>A+</option><option>A-</option>
              <option>B+</option><option>B-</option>
              <option>O+</option><option>O-</option>
              <option>AB+</option><option>AB-</option>
            </select>
          </div>
        </div>

        <div class="mb-3">
          <label class="form-label">Address</label>
          <textarea v-model="form.address" class="form-control" rows="2"></textarea>
        </div>

        <button type="submit" class="btn btn-primary w-100" :disabled="loading">
          {{ loading ? 'Registering...' : 'Register' }}
        </button>
      </form>

      <div class="auth-footer">
        <p>Already have an account? <router-link to="/login">Login here</router-link></p>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: 'RegisterView',
  data() {
    return {
      form: {
        name: '', username: '', email: '', password: '',
        age: '', gender: '', phone: '', blood_group: '', address: ''
      },
      error: '', success: '', loading: false
    }
  },
  methods: {
    ...mapActions(['register']),
    async handleRegister() {
      this.loading = true
      this.error = ''
      this.success = ''
      try {
        await this.register(this.form)
        this.success = 'Registration successful! Redirecting to login...'
        setTimeout(() => this.$router.push('/login'), 2000)
      } catch (err) {
        this.error = err.response?.data?.message || 'Registration failed'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.auth-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a3c5e 0%, #2c7be5 100%);
  padding: 20px;
}

.auth-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  width: 100%;
  max-width: 600px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
}

.auth-header {
  text-align: center;
  margin-bottom: 30px;
}

.auth-header h2 { color: #1a3c5e; font-weight: 700; }
.auth-header p { color: #666; }

.auth-footer {
  text-align: center;
  margin-top: 20px;
  color: #666;
}

.auth-footer a {
  color: #2c7be5;
  text-decoration: none;
  font-weight: 500;
}
</style>