<template>
  <div class="view-container">
    <div class="view-header">
      <div>
        <h1 class="view-title">Courses</h1>
        <p class="view-subtitle">Explore curriculum and class prices</p>
      </div>
      <div style="display: flex; gap: 1rem; align-items: center;">
        <div class="badge-count" v-if="courses.length">{{ courses.length }} total</div>
        <button @click="openCreateModal" class="btn btn-primary">
          <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          New Course
        </button>
      </div>
    </div>

    <!-- Error/Warning Banner -->
    <div v-if="error" class="info-banner">
      <span>{{ error }}</span>
    </div>

    <!-- Data Table Container -->
    <div class="table-card">
      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Course Name</th>
              <th>Description</th>
              <th>Price</th>
              <th style="text-align: right;">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="course in courses" :key="course.id" class="table-row">
              <td class="font-mono text-muted">#{{ course.id }}</td>
              <td class="font-semibold">{{ course.name }}</td>
              <td>{{ course.description || '-' }}</td>
              <td class="font-mono font-semibold">{{ formatPrice(course.price) }} UZS</td>
              <td class="actions-cell">
                <button @click="openEditModal(course)" class="btn-icon" title="Edit Course">
                  <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 113 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                  </svg>
                </button>
                <button @click="deleteCourse(course)" class="btn-icon btn-icon-danger" title="Delete Course">
                  <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"></path>
                    <line x1="10" y1="11" x2="10" y2="17"></line>
                    <line x1="14" y1="11" x2="14" y2="17"></line>
                  </svg>
                </button>
              </td>
            </tr>
            <tr v-if="!courses.length && !loading">
              <td colspan="5" class="empty-state">No courses found.</td>
            </tr>
            <tr v-if="loading">
              <td colspan="5" class="loading-state">
                <div class="spinner"></div>
                <span>Loading courses...</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showModal" class="modal-backdrop" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2 class="modal-title">{{ isEdit ? 'Edit Course' : 'Add Course' }}</h2>
          <button @click="closeModal" class="modal-close">
            <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <form @submit.prevent="saveCourse">
          <div class="modal-body">
            <div class="form-group">
              <label for="courseName" class="form-label">Course Name</label>
              <input
                type="text"
                id="courseName"
                v-model="form.name"
                required
                placeholder="e.g. Physics Level I"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label for="price" class="form-label">Price (UZS)</label>
              <input
                type="text"
                inputmode="numeric"
                id="price"
                :value="form.price"
                @input="formatInputPrice"
                required
                placeholder="e.g. 4 500"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label for="description" class="form-label">Description (Optional)</label>
              <textarea
                id="description"
                v-model="form.description"
                placeholder="Course curriculum details, requirements..."
                class="form-input"
                rows="3"
                style="resize: vertical; font-family: inherit;"
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="submitting">
              {{ submitting ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Courses',
  data() {
    return {
      courses: [],
      loading: false,
      error: null,

      // Modal controls
      showModal: false,
      isEdit: false,
      submitting: false,
      form: {
        id: null,
        name: '',
        description: '',
        price: ''
      }
    }
  },
  mounted() {
    this.fetchCourses()
  },
  methods: {
    async fetchCourses() {
      this.loading = true
      this.error = null

      try {
        const response = await axios.get('http://localhost:8000/api/courses/')
        this.courses = response.data
        this.loading = false
      } catch (err) {
        console.error('Error fetching courses:', err)
        this.error = 'Failed to load courses catalogue from backend.'
        this.loading = false
      }
    },
    openCreateModal() {
      this.isEdit = false
      this.form = { id: null, name: '', description: '', price: '' }
      this.showModal = true
    },
    openEditModal(course) {
      this.isEdit = true
      this.form = { ...course }
      if (this.form.price) {
        const digits = Math.round(parseFloat(this.form.price)).toString()
        this.form.price = digits.replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
      }
      this.showModal = true
    },
    closeModal() {
      this.showModal = false
    },
    formatInputPrice(event) {
      const value = event.target.value
      const selectionStart = event.target.selectionStart
      const oldLength = value.length

      // Remove non-digit chars
      const digits = value.replace(/\D/g, '')
      
      // Format with spaces
      const formatted = digits.replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
      
      this.form.price = formatted
      
      this.$nextTick(() => {
        if (event.target) {
          const newLength = formatted.length
          const delta = newLength - oldLength
          const newCursorPos = selectionStart + delta
          event.target.setSelectionRange(newCursorPos, newCursorPos)
        }
      })
    },
    async saveCourse() {
      this.submitting = true
      const rawPrice = this.form.price.replace(/\s/g, '')
      const priceVal = parseFloat(rawPrice || 0).toFixed(2)

      const payload = {
        ...this.form,
        price: priceVal
      }

      try {
        if (this.isEdit) {
          await axios.put(`http://localhost:8000/api/courses/${this.form.id}/`, payload)
        } else {
          await axios.post('http://localhost:8000/api/courses/', payload)
        }
        this.submitting = false
        this.closeModal()
        this.fetchCourses()
      } catch (err) {
        console.error('Error saving course:', err)
        alert('An error occurred while saving the course record.')
        this.submitting = false
      }
    },
    async deleteCourse(course) {
      if (!confirm(`Are you sure you want to delete course "${course.name}"?`)) {
        return
      }

      try {
        await axios.delete(`http://localhost:8000/api/courses/${course.id}/`)
        this.fetchCourses()
      } catch (err) {
        console.error('Error deleting course:', err)
        alert('An error occurred while deleting the course record. If it has dependent groups, deletion is protected.')
      }
    },
    formatPrice(price) {
      if (!price && price !== 0) return '0'
      const val = Math.round(parseFloat(price))
      return val.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
    }
  }
}
</script>

<style scoped>
@import '../assets/views.css';
</style>
