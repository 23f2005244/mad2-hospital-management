<template>
  <div class="d-flex">
    <SidebarNav />
    <div class="main-content w-100">
      <h4 class="mb-4">Book Appointment</h4>

      <div v-if="successMsg" class="alert alert-success alert-dismissible fade show">
        {{ successMsg }}
        <button type="button" class="btn-close" @click="successMsg = ''"></button>
      </div>
      <div v-if="errorMsg" class="alert alert-danger alert-dismissible fade show">
        {{ errorMsg }}
        <button type="button" class="btn-close" @click="errorMsg = ''"></button>
      </div>

      <!-- Step 1: Search / Browse Doctors -->
      <div class="card mb-4">
        <div class="card-header">Step 1: Find a Doctor</div>
        <div class="card-body">
          <div class="row mb-3">
            <div class="col-md-5">
              <input
                v-model="searchQuery"
                type="text"
                class="form-control"
                placeholder="Search by doctor name or specialization..."
                @input="handleSearch"
              />
            </div>
            <div class="col-md-1 text-center pt-2">or</div>
            <div class="col-md-4">
              <select v-model="selectedDeptId" class="form-select" @change="loadDoctorsByDept">
                <option value="">Browse by Department</option>
                <option v-for="dept in departments" :key="dept.id" :value="dept.id">{{ dept.name }}</option>
              </select>
            </div>
          </div>

          <div v-if="doctorsLoading" class="text-center py-3">
            <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
          </div>

          <div v-if="doctors.length > 0" class="table-responsive">
            <table class="table table-hover mb-0">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Specialization</th>
                  <th>Department</th>
                  <th>Experience</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="doc in doctors" :key="doc.id" :class="{ 'table-primary': selectedDoctor && selectedDoctor.id === doc.id }">
                  <td>{{ doc.name }}</td>
                  <td>{{ doc.specialization }}</td>
                  <td>{{ doc.department || '—' }}</td>
                  <td>{{ doc.experience_years ? doc.experience_years + ' yrs' : '—' }}</td>
                  <td>
                    <button class="btn btn-sm btn-outline-primary" @click="selectDoctor(doc)">
                      Select
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Step 2: View Availability & Book -->
      <div class="card" v-if="selectedDoctor">
        <div class="card-header">
          Step 2: Choose a Slot — Dr. {{ selectedDoctor.name }} ({{ selectedDoctor.specialization }})
        </div>
        <div class="card-body">
          <div v-if="slotsLoading" class="text-center py-3">
            <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
          </div>

          <div v-else-if="slots.length === 0" class="text-muted text-center py-3">
            No available slots for this doctor in the next 7 days.
          </div>

          <div class="table-responsive" v-else>
            <table class="table table-bordered mb-0">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Slot</th>
                  <th>Time</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="slot in slots" :key="slot.id">
                  <td>{{ slot.date }}</td>
                  <td><span class="badge" :class="slot.slot_type === 'morning' ? 'bg-warning text-dark' : 'bg-info'">{{ slot.slot_type }}</span></td>
                  <td>{{ slot.start_time }} — {{ slot.end_time }}</td>
                  <td>
                    <span v-if="slot.is_booked" class="badge bg-danger">Booked</span>
                    <span v-else class="badge bg-success">Available</span>
                  </td>
                  <td>
                    <button
                      v-if="!slot.is_booked"
                      class="btn btn-sm btn-primary"
                      @click="bookSlot(slot)"
                      :disabled="booking"
                    >
                      {{ booking ? 'Booking...' : 'Book Now' }}
                    </button>
                    <span v-else class="text-muted small">—</span>
                  </td>
                </tr>
              </tbody>
            </table>
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
  name: 'BookAppointment',
  components: { SidebarNav },
  data() {
    return {
      departments: [],
      doctors: [],
      selectedDeptId: '',
      searchQuery: '',
      doctorsLoading: false,
      selectedDoctor: null,
      slots: [],
      slotsLoading: false,
      booking: false,
      successMsg: '',
      errorMsg: ''
    }
  },
  async created() {
    await this.fetchDepartments()
  },
  methods: {
    async fetchDepartments() {
      try {
        const res = await axios.get('/api/patient/departments')
        this.departments = res.data
      } catch (err) {
        console.error('Failed to load departments:', err)
      }
    },
    handleSearch() {
      if (this.searchTimer) clearTimeout(this.searchTimer)
      this.searchTimer = setTimeout(async () => {
        if (this.searchQuery.trim()) {
          this.selectedDeptId = ''
          this.doctorsLoading = true
          try {
            const res = await axios.get('/api/patient/search/doctors', { params: { q: this.searchQuery } })
            this.doctors = res.data
          } catch (err) {
            console.error('Search failed:', err)
          } finally {
            this.doctorsLoading = false
          }
        } else {
          this.doctors = []
        }
      }, 300)
    },
    async loadDoctorsByDept() {
      if (!this.selectedDeptId) {
        this.doctors = []
        return
      }
      this.searchQuery = ''
      this.doctorsLoading = true
      try {
        const res = await axios.get(`/api/patient/departments/${this.selectedDeptId}/doctors`)
        this.doctors = res.data.doctors
      } catch (err) {
        console.error('Failed to load doctors:', err)
      } finally {
        this.doctorsLoading = false
      }
    },
    async selectDoctor(doc) {
      this.selectedDoctor = doc
      this.slotsLoading = true
      this.slots = []
      try {
        const res = await axios.get(`/api/patient/doctors/${doc.id}/availability`)
        this.slots = res.data.availability
      } catch (err) {
        console.error('Failed to load availability:', err)
      } finally {
        this.slotsLoading = false
      }
    },
    async bookSlot(slot) {
      this.booking = true
      this.successMsg = ''
      this.errorMsg = ''
      try {
        await axios.post('/api/patient/appointments', {
          doctor_id: this.selectedDoctor.id,
          date: slot.date,
          time: slot.start_time
        })
        this.successMsg = `Appointment booked with Dr. ${this.selectedDoctor.name} on ${slot.date} at ${slot.start_time}`
        // Refresh slots to reflect the booking
        await this.selectDoctor(this.selectedDoctor)
      } catch (err) {
        this.errorMsg = err.response?.data?.message || 'Failed to book appointment'
      } finally {
        this.booking = false
      }
    }
  }
}
</script>
