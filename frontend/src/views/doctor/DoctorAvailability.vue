<template>
  <div class="d-flex">
    <SidebarNav />
    <div class="main-content w-100">
      <h4 class="mb-4">Set Availability (Next 7 Days)</h4>

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
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-bordered mb-0">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Day</th>
                    <th>Morning Slot</th>
                    <th>Evening Slot</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="day in days" :key="day.date">
                    <td>{{ day.date }}</td>
                    <td>{{ day.dayName }}</td>
                    <td>
                      <div class="form-check">
                        <input
                          class="form-check-input"
                          type="checkbox"
                          v-model="day.morning"
                          :id="'morning-' + day.date"
                        />
                        <label class="form-check-label" :for="'morning-' + day.date">
                          09:00 — 12:00
                        </label>
                      </div>
                    </td>
                    <td>
                      <div class="form-check">
                        <input
                          class="form-check-input"
                          type="checkbox"
                          v-model="day.evening"
                          :id="'evening-' + day.date"
                        />
                        <label class="form-check-label" :for="'evening-' + day.date">
                          14:00 — 17:00
                        </label>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="mt-3 text-end">
              <button class="btn btn-primary" @click="saveAvailability" :disabled="saving">
                {{ saving ? 'Saving...' : 'Save Availability' }}
              </button>
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
  name: 'DoctorAvailability',
  components: { SidebarNav },
  data() {
    return {
      days: [],
      loading: true,
      saving: false,
      successMsg: '',
      errorMsg: ''
    }
  },
  async created() {
    this.buildDays()
    await this.fetchAvailability()
  },
  methods: {
    buildDays() {
      const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
      const today = new Date()
      this.days = []
      for (let i = 0; i < 7; i++) {
        const d = new Date(today)
        d.setDate(today.getDate() + i)
        const dateStr = d.toISOString().split('T')[0]
        this.days.push({
          date: dateStr,
          dayName: dayNames[d.getDay()],
          morning: false,
          evening: false
        })
      }
    },
    async fetchAvailability() {
      this.loading = true
      try {
        const res = await axios.get('/api/doctor/availability')
        const existing = res.data
        for (const slot of existing) {
          const day = this.days.find(d => d.date === slot.date)
          if (day) {
            if (slot.slot_type === 'morning') day.morning = true
            if (slot.slot_type === 'evening') day.evening = true
          }
        }
      } catch (err) {
        console.error('Failed to load availability:', err)
      } finally {
        this.loading = false
      }
    },
    async saveAvailability() {
      this.saving = true
      this.successMsg = ''
      this.errorMsg = ''
      try {
        const availabilities = []
        for (const day of this.days) {
          if (day.morning) {
            availabilities.push({
              date: day.date,
              start_time: '09:00',
              end_time: '12:00',
              slot_type: 'morning'
            })
          }
          if (day.evening) {
            availabilities.push({
              date: day.date,
              start_time: '14:00',
              end_time: '17:00',
              slot_type: 'evening'
            })
          }
        }
        await axios.post('/api/doctor/availability', { availabilities })
        this.successMsg = 'Availability saved successfully!'
      } catch (err) {
        this.errorMsg = err.response?.data?.message || 'Failed to save availability'
      } finally {
        this.saving = false
      }
    }
  }
}
</script>
