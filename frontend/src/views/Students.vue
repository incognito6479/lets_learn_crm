<template>
  <div class="view-container">
    <div class="view-header">
      <div>
        <h1 class="view-title">{{ $t('students.title') }}</h1>
        <p class="view-subtitle">{{ $t('students.sub') }}</p>
      </div>
      <div style="display: flex; gap: 1rem; align-items: center;">
        <div class="badge-count" v-if="students.length">{{ students.length }} {{ $t('common.total') }}</div>
        <button @click="openCreateModal" class="btn btn-primary">
          <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          {{ $t('students.new') }}
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
        :placeholder="$t('students.search_placeholder')"
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
              <th>{{ $t('students.col_fullname') }}</th>
              <th>{{ $t('students.col_phone1') }}</th>
              <th>{{ $t('students.col_phone2') }}</th>
              <th>{{ $t('common.description') }}</th>
              <th style="text-align: right;">{{ $t('common.actions') }}</th>
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
                <button @click="openEditModal(student)" class="btn-icon" :title="$t('students.modal_edit')">
                  <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 113 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                  </svg>
                </button>
                <button @click="deleteStudent(student)" class="btn-icon btn-icon-danger" :title="$t('common.delete')">
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
              <td colspan="6" class="empty-state">{{ $t('students.no_students') }}</td>
            </tr>
            <tr v-if="loading">
              <td colspan="6" class="loading-state">
                <div class="spinner"></div>
                <span>{{ $t('common.loading') }}</span>
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
          <h2 class="modal-title">{{ isEdit ? $t('students.modal_edit') : $t('students.modal_new') }}</h2>
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
              <label for="fullName" class="form-label">{{ $t('students.col_fullname') }}</label>
              <input
                type="text"
                id="fullName"
                v-model="form.full_name"
                required
                :placeholder="$t('groupDetail.student_fullname_placeholder')"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label for="phone1" class="form-label">{{ $t('students.col_phone1') }}</label>
              <div class="phone-input-wrapper">
                <span class="phone-prefix">+998</span>
                <input
                  type="text"
                  inputmode="numeric"
                  maxlength="12"
                  id="phone1"
                  :value="form.phone1"
                  @input="handlePhoneInput($event, 'phone1')"
                  @keypress="onlyNumber"
                  required
                  placeholder="90 123 45 67"
                  class="phone-editable-input"
                />
              </div>
            </div>
            <div class="form-group">
              <label for="phone2" class="form-label">{{ $t('students.col_phone2') }}</label>
              <div class="phone-input-wrapper">
                <span class="phone-prefix">+998</span>
                <input
                  type="text"
                  inputmode="numeric"
                  maxlength="12"
                  id="phone2"
                  :value="form.phone2"
                  @input="handlePhoneInput($event, 'phone2')"
                  @keypress="onlyNumber"
                  placeholder="90 123 45 67"
                  class="phone-editable-input"
                />
              </div>
            </div>
            <div class="form-group">
              <label for="description" class="form-label">{{ $t('common.description') }}</label>
              <textarea
                id="description"
                v-model="form.description"
                :placeholder="$t('groupDetail.student_desc_placeholder')"
                class="form-input"
                rows="3"
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" @click="closeModal" class="btn btn-secondary">{{ $t('common.cancel') }}</button>
            <button type="submit" class="btn btn-primary" :disabled="submitting">
              {{ submitting ? $t('common.loading') : $t('common.save') }}
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
      let list = [...this.students]
      
      // Sort newly added (highest ID) first
      list.sort((a, b) => b.id - a.id)
      
      const query = this.searchQuery.toLowerCase().trim()
      if (query) {
        list = list.filter(s => {
          const nameMatch = s.full_name && s.full_name.toLowerCase().includes(query)
          const phone1Match = s.phone1 && s.phone1.toLowerCase().includes(query)
          const phone2Match = s.phone2 && s.phone2.toLowerCase().includes(query)
          return nameMatch || phone1Match || phone2Match
        })
      }
      
      return list.slice(0, 20)
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
        const response = await axios.get('/api/students/')
        this.students = response.data
        this.loading = false
      } catch (err) {
        console.error('Error fetching students:', err)
        this.error = this.$t('stats.api_error')
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
        phone1: this.parsePhoneForInput(student.phone1),
        phone2: this.parsePhoneForInput(student.phone2 || ''),
        description: student.description || ''
      }
      this.showModal = true
    },
    closeModal() {
      this.showModal = false
    },
    async saveStudent() {
      this.submitting = true
      
      const rawPhone1 = this.form.phone1.replace(/\D/g, '')
      if (rawPhone1.length !== 9) {
        alert(this.$t('students.phone_length_error'))
        this.submitting = false
        return
      }
      if (this.form.phone2) {
        const rawPhone2 = this.form.phone2.replace(/\D/g, '')
        if (rawPhone2.length !== 9) {
          alert(this.$t('students.phone_length_error'))
          this.submitting = false
          return
        }
      }

      const payload = {
        ...this.form,
        phone1: '+998' + rawPhone1,
        phone2: this.form.phone2 ? ('+998' + this.form.phone2.replace(/\D/g, '')) : null
      }
      try {
        if (this.isEdit) {
          await axios.put(`/api/students/${this.form.id}/`, payload)
        } else {
          await axios.post('/api/students/', payload)
        }
        this.submitting = false
        this.closeModal()
        this.fetchStudents()
      } catch (err) {
        console.error('Error saving student:', err)
        alert(this.$t('common.error_save'))
        this.submitting = false
      }
    },
    async deleteStudent(student) {
      if (!confirm(this.$t('students.delete_confirm', { name: student.full_name }))) {
        return
      }

      try {
        // Delete request in backend sets is_active = False (soft delete)
        await axios.delete(`/api/students/${student.id}/`)
        this.fetchStudents()
      } catch (err) {
        console.error('Error deleting student:', err)
        alert(this.$t('common.error_delete'))
      }
    },
    formatPhoneInput(val) {
      if (!val) return ''
      const digits = val.replace(/\D/g, '').slice(0, 9)
      let formatted = ''
      if (digits.length > 0) {
        formatted += digits.substring(0, 2)
      }
      if (digits.length > 2) {
        formatted += ' ' + digits.substring(2, 5)
      }
      if (digits.length > 5) {
        formatted += ' ' + digits.substring(5, 7)
      }
      if (digits.length > 7) {
        formatted += ' ' + digits.substring(7, 9)
      }
      return formatted
    },
    handlePhoneInput(e, field) {
      const input = e.target
      const rawValue = input.value
      
      const selectionStart = input.selectionStart
      const digitsBefore = rawValue.substring(0, selectionStart).replace(/\D/g, '').length
      
      const formatted = this.formatPhoneInput(rawValue)
      this.form[field] = formatted
      
      this.$nextTick(() => {
        let newCursorPos = 0
        let digitCount = 0
        for (let i = 0; i < formatted.length; i++) {
          if (/\d/.test(formatted[i])) {
            digitCount++
          }
          newCursorPos = i + 1
          if (digitCount === digitsBefore) {
            break
          }
        }
        input.setSelectionRange(newCursorPos, newCursorPos)
      })
    },
    parsePhoneForInput(phoneStr) {
      if (!phoneStr) return ''
      let localPart = phoneStr
      if (phoneStr.startsWith('+998')) {
        localPart = phoneStr.substring(4)
      } else if (phoneStr.startsWith('998')) {
        localPart = phoneStr.substring(3)
      }
      return this.formatPhoneInput(localPart)
    },
    onlyNumber(event) {
      const charCode = event.which ? event.which : event.keyCode
      if (charCode > 31 && (charCode < 48 || charCode > 57)) {
        event.preventDefault()
      }
      return true
    }
  }
}
</script>

<style scoped>
@import '../assets/views.css';
</style>
