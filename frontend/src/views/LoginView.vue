<template>
  <div class="auth-wrapper">
    <div class="auth-card">
      <div class="auth-header">
        <h2>🏥 Hospital Management</h2>
        <p>Sign in to your account</p>
      </div>

      <div v-if="error" class="alert alert-danger">{{ error }}</div>

      <form @submit.prevent="handleLogin">
        <div class="mb-3">
          <label class="form-label">Username</label>
          <input
            v-model="form.username"
            type="text"
            class="form-control"
            placeholder="Enter username"
            required
          />
        </div>

        <div class="mb-3">
          <label class="form-label">Password</label>
          <input
            v-model="form.password"
            type="password"
            class="form-control"
            placeholder="Enter password"
            required
          />
        </div>

        <button
          type="submit"
          class="btn btn-primary w-100"
          :disabled="loading"
        >
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </button>
      </form>

      <div class="auth-footer">
        <p>Don't have an account? <router-link to="/register">Register here</router-link></p>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: 'LoginView',
  data() {
    return {
      form: { username: '', password: '' },
      error: '',
      loading: false
    }
  },
  methods: {
    ...mapActions(['login']),
    async handleLogin() {
      this.loading = true
      this.error = ''
      try {
        const user = await this.login(this.form)
        if (user.role === 'admin') this.$router.push('/admin/dashboard')
        else if (user.role === 'doctor') this.$router.push('/doctor/dashboard')
        else this.$router.push('/patient/dashboard')
      } catch (err) {
        this.error = err.response?.data?.message || 'Login failed'
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
}

.auth-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
}

.auth-header {
  text-align: center;
  margin-bottom: 30px;
}

.auth-header h2 {
  color: #1a3c5e;
  font-weight: 700;
  margin-bottom: 5px;
}

.auth-header p {
  color: #666;
}

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