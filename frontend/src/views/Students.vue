<template>
  <div class="view-container">
    <div class="view-header">
      <div>
        <h1 class="view-title">Students</h1>
        <p class="view-subtitle">Manage registered students and their details</p>
      </div>
      <div style="display: flex; gap: 1rem; align-items: center;">
        <div class="badge-count" v-if="students.length">{{ students.length }} total</div>
        <button @click="openCreateModal" class="btn btn-primary">
          <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          New Student
        </button>
      </div>
    </div>

    <!-- Error/Warning Banner -->
    <div v-if="error" class="info-banner">
      <span>{{ error }}</span>
    </div>

    <!-- Search Input Control -->
    <div class="search-bar-container" style="margin-bottom: 1.5rem; display: flex; gap: 0.5rem; max-width: 320px;">
      <input
        type="text"
        v-model="searchQuery"
        placeholder="Search students by name or phone..."
        class="form-input"
      />
    </div>

    <!-- Data Table Container -->
    <div class="table-card">
      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Full Name</th>
              <th>Primary Phone</th>
              <th>Secondary Phone</th>
              <th>Description</th>
              <th style="text-align: right;">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="student in filteredStudents" :key="student.id" class="table-row">
              <td class="font-mono text-muted">#{{ student.id }}</td>
              <td class="font-semibold">{{ student.full_name }}</td>
              <td>{{ student.phone1 }}</td>
              <td>{{ student.phone2 || '-' }}</td>
              <td>{{ student.description || '-' }}</td>
              <td class="actions-cell">
                <button @click="openEditModal(student)" class="btn-icon" title="Edit Student">
                  <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 113 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                  </svg>
                </button>
                <button @click="deleteStudent(student)" class="btn-icon btn-icon-danger" title="Delete Student">
                  <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"></path>
                    <line x1="10" y1="11" x2="10" y2="17"></line>
                    <line x1="14" y1="11" x2="14" y2="17"></line>
                  </svg>
                </button>
              </td>
            </tr>
            <tr v-if="!students.length && !loading">
              <td colspan="6" class="empty-state">No students found.</td>
            </tr>
            <tr v-if="loading">
              <td colspan="6" class="loading-state">
                <div class="spinner"></div>
                <span>Loading students...</span>
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
          <h2 class="modal-title">{{ isEdit ? 'Edit Student' : 'Add Student' }}</h2>
          <button @click="closeModal" class="modal-close">
            <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <form @submit.prevent="saveStudent">
          <div class="modal-body">
            <div class="form-group">
              <label for="fullName" class="form-label">Full Name</label>
              <input
                type="text"
                id="fullName"
                v-model="form.full_name"
                required
                placeholder="e.g. John Doe"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label for="phone1" class="form-label">Primary Phone</label>
              <input
                type="text"
                id="phone1"
                v-model="form.phone1"
                required
                placeholder="e.g. +1 555-0199"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label for="phone2" class="form-label">Secondary Phone (Optional)</label>
              <input
                type="text"
                id="phone2"
                v-model="form.phone2"
                placeholder="e.g. +1 555-0198"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label for="description" class="form-label">Description (Optional)</label>
              <textarea
                id="description"
                v-model="form.description"
                placeholder="e.g. Preparing for IELTS, schedules on weekends"
                class="form-input"
                rows="3"
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
  name: 'Students',
  data() {
    return {
      students: [],
      searchQuery: '',
      loading: false,
      error: null,
      
      // Modal controls
      showModal: false,
      isEdit: false,
      submitting: false,
      form: {
        id: null,
        full_name: '',
        phone1: '',
        phone2: '',
        description: ''
      }
    }
  },
  computed: {
    filteredStudents() {
      const query = this.searchQuery.toLowerCase().trim()
      if (!query) return this.students
      return this.students.filter(s => {
        const nameMatch = s.full_name && s.full_name.toLowerCase().includes(query)
        const phone1Match = s.phone1 && s.phone1.toLowerCase().includes(query)
        const phone2Match = s.phone2 && s.phone2.toLowerCase().includes(query)
        return nameMatch || phone1Match || phone2Match
      })
    }
  },
  mounted() {
    this.fetchStudents()
  },
  methods: {
    async fetchStudents() {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.get('http://localhost:8000/api/students/')
        this.students = response.data
        this.loading = false
      } catch (err) {
        console.error('Error fetching students:', err)
        this.error = 'Failed to load students roster.'
        this.loading = false
      }
    },
    openCreateModal() {
      this.isEdit = false
      this.form = { id: null, full_name: '', phone1: '', phone2: '', description: '' }
      this.showModal = true
    },
    openEditModal(student) {
      this.isEdit = true
      this.form = {
        id: student.id,
        full_name: student.full_name,
        phone1: student.phone1,
        phone2: student.phone2 || '',
        description: student.description || ''
      }
      this.showModal = true
    },
    closeModal() {
      this.showModal = false
    },
    async saveStudent() {
      this.submitting = true
      try {
        if (this.isEdit) {
          await axios.put(`http://localhost:8000/api/students/${this.form.id}/`, this.form)
        } else {
          await axios.post('http://localhost:8000/api/students/', this.form)
        }
        this.submitting = false
        this.closeModal()
        this.fetchStudents()
      } catch (err) {
        console.error('Error saving student:', err)
        alert('An error occurred while saving the student record.')
        this.submitting = false
      }
    },
    async deleteStudent(student) {
      if (!confirm(`Are you sure you want to delete student "${student.full_name}"?`)) {
        return
      }

      try {
        // Delete request in backend sets is_active = False (soft delete)
        await axios.delete(`http://localhost:8000/api/students/${student.id}/`)
        this.fetchStudents()
      } catch (err) {
        console.error('Error deleting student:', err)
        alert('An error occurred while deleting the student record.')
      }
    }
  }
}
</script>

<style scoped>
@import '../assets/views.css';
</style>
