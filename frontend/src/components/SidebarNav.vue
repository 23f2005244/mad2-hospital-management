<template>
  <div class="sidebar">
    <div class="sidebar-brand">
      🏥 HMS
    </div>
    <nav class="sidebar-nav">
      <template v-if="role === 'admin'">
        <router-link to="/admin/dashboard">📊 Dashboard</router-link>
        <router-link to="/admin/doctors">👨‍⚕️ Doctors</router-link>
        <router-link to="/admin/patients">🧑‍🤝‍🧑 Patients</router-link>
        <router-link to="/admin/appointments">📅 Appointments</router-link>
      </template>

      <template v-if="role === 'doctor'">
        <router-link to="/doctor/dashboard">📊 Dashboard</router-link>
        <router-link to="/doctor/appointments">📅 Appointments</router-link>
        <router-link to="/doctor/patients">🧑‍🤝‍🧑 My Patients</router-link>
        <router-link to="/doctor/availability">🗓️ Availability</router-link>
      </template>

      <template v-if="role === 'patient'">
        <router-link to="/patient/dashboard">📊 Dashboard</router-link>
        <router-link to="/patient/appointments">📅 Appointments</router-link>
        <router-link to="/patient/book">➕ Book Appointment</router-link>
        <router-link to="/patient/history">📋 History</router-link>
        <router-link to="/patient/profile">👤 Profile</router-link>
      </template>

      <a href="#" @click.prevent="handleLogout" class="logout-link">🚪 Logout</a>
    </nav>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'SidebarNav',
  computed: {
    ...mapGetters(['getRole']),
    role() { return this.getRole }
  },
  methods: {
    ...mapActions(['logout']),
    handleLogout() {
      this.logout()
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.logout-link {
  position: absolute;
  bottom: 20px;
  width: 100%;
  color: rgba(255,255,255,0.7) !important;
}

.logout-link:hover {
  color: white !important;
  background: rgba(255,0,0,0.2) !important;
}
</style>