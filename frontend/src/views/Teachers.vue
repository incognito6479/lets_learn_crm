<template>
  <div class="view-container">
    <div class="view-header">
      <div>
        <h1 class="view-title">{{ $t('teachers.title') }}</h1>
        <p class="view-subtitle">{{ $t('teachers.sub') }}</p>
      </div>
      <div style="display: flex; gap: 1rem; align-items: center;">
        <div class="badge-count" v-if="teachers.length">{{ teachers.length }} {{ $t('stats.active_teachers') }}</div>
        <button @click="openCreateModal" class="btn btn-primary">
          <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          {{ $t('teachers.new') }}
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
        :placeholder="$t('teachers.search_placeholder')"
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
              <th>{{ $t('common.name') }}</th>
              <th>{{ $t('teachers.col_username') }}</th>
              <th>{{ $t('common.phone') }}</th>
              <th>{{ $t('teachers.col_status') }}</th>
              <th>{{ $t('teachers.col_branch') }}</th>
              <th>{{ $t('teachers.col_status') }}</th>
              <th style="text-align: right;">{{ $t('common.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="teacher in filteredTeachers" :key="teacher.id" class="table-row">
              <td class="font-mono text-muted">#{{ teacher.id }}</td>
              <td class="font-semibold">
                <router-link :to="`/teachers/${teacher.id}`" class="teacher-link">
                  {{ teacher.first_name }} {{ teacher.last_name }}
                </router-link>
              </td>
              <td>{{ teacher.username }}</td>
              <td>{{ teacher.phone_number || '-' }}</td>
              <td>
                <span class="status-badge teacher">{{ teacher.role === 'teacher' ? $t('groupDetail.teacher') : teacher.role }}</span>
              </td>
              <td>{{ getBranchName(teacher.branch) }}</td>
              <td>
                <span class="status-badge" :class="teacher.is_active ? 'active' : 'dropped'">
                  {{ teacher.is_active ? $t('teachers.active') : $t('teachers.inactive') }}
                </span>
              </td>
              <td class="actions-cell">
                <button @click="openEditModal(teacher)" class="btn-icon" :title="$t('teachers.modal_edit')">
                  <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 113 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                  </svg>
                </button>
                <button @click="deleteTeacher(teacher)" class="btn-icon btn-icon-danger" :title="$t('common.delete')">
                  <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"></path>
                    <line x1="10" y1="11" x2="10" y2="17"></line>
                    <line x1="14" y1="11" x2="14" y2="17"></line>
                  </svg>
                </button>
              </td>
            </tr>
            <tr v-if="!teachers.length && !loading">
              <td colspan="8" class="empty-state">{{ $t('teachers.no_teachers') }}</td>
            </tr>
            <tr v-if="loading">
              <td colspan="8" class="loading-state">
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
          <h2 class="modal-title">{{ isEdit ? $t('teachers.modal_edit') : $t('teachers.modal_new') }}</h2>
          <button @click="closeModal" class="modal-close">
            <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <form @submit.prevent="saveTeacher">
          <div class="modal-body">
            <div style="display: flex; gap: 1rem;">
              <div class="form-group" style="flex: 1;">
                <label for="firstName" class="form-label">{{ $t('teachers.form_firstname') }}</label>
                <input
                  type="text"
                  id="firstName"
                  v-model="form.first_name"
                  required
                  class="form-input"
                />
              </div>
              <div class="form-group" style="flex: 1;">
                <label for="lastName" class="form-label">{{ $t('teachers.form_lastname') }}</label>
                <input
                  type="text"
                  id="lastName"
                  v-model="form.last_name"
                  required
                  class="form-input"
                />
              </div>
            </div>
            <div class="form-group">
              <label for="username" class="form-label">{{ $t('teachers.form_username') }}</label>
              <input
                type="text"
                id="username"
                v-model="form.username"
                required
                class="form-input"
                :disabled="isEdit"
              />
            </div>
            <div class="form-group">
              <label for="password" class="form-label">{{ $t('login.password') }} {{ isEdit ? $t('teachers.form_password_hint') : '' }}</label>
              <input
                type="password"
                id="password"
                v-model="form.password"
                :required="!isEdit"
                :placeholder="$t('login.password') + '...'"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label for="phoneNumber" class="form-label">{{ $t('common.phone') }}</label>
              <input
                type="text"
                id="phoneNumber"
                v-model="form.phone_number"
                :placeholder="$t('groupDetail.student_phone1_placeholder')"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label for="teacherBranch" class="form-label">{{ $t('teachers.form_branch') }}</label>
              <select id="teacherBranch" v-model="form.branch" class="form-input">
                <option value="">{{ $t('teachers.form_branch') }}</option>
                <option v-for="branch in branches" :key="branch.id" :value="branch.id">
                  {{ branch.name }}
                </option>
              </select>
            </div>
            <!-- Status Checkbox -->
            <div class="remember-me" style="margin-top: 0.5rem;">
              <label class="checkbox-container">
                <input type="checkbox" v-model="form.is_active" />
                <span class="checkmark"></span>
                <span class="checkbox-label" style="color: #475569; font-weight: 600;">{{ $t('teachers.form_status') }}</span>
              </label>
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
  name: 'Teachers',
  data() {
    return {
      teachers: [],
      branches: [],
      searchQuery: '',
      loading: false,
      error: null,

      // Modal controls
      showModal: false,
      isEdit: false,
      submitting: false,
      form: {
        id: null,
        first_name: '',
        last_name: '',
        username: '',
        password: '',
        phone_number: '',
        branch: '',
        role: 'teacher',
        is_active: true
      }
    }
  },
  computed: {
    filteredTeachers() {
      const query = this.searchQuery.toLowerCase().trim()
      if (!query) return this.teachers
      return this.teachers.filter(t => {
        const fullName = `${t.first_name || ''} ${t.last_name || ''}`.toLowerCase()
        return fullName.includes(query)
      })
    }
  },
  mounted() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      this.loading = true
      this.error = null

      try {
        const [usersRes, branchesRes] = await Promise.all([
          axios.get(`/api/users/`, { params: { role: 'teacher' } }),
          axios.get(`/api/branches/`)
        ])
        this.branches = branchesRes.data
        this.teachers = usersRes.data
        this.loading = false
      } catch (err) {
        console.error('Error fetching data:', err)
        this.error = this.$t('stats.api_error')
        this.loading = false
      }
    },
    openCreateModal() {
      this.isEdit = false
      this.form = {
        id: null,
        first_name: '',
        last_name: '',
        username: '',
        password: '',
        phone_number: '',
        branch: '',
        role: 'teacher',
        is_active: true
      }
      this.showModal = true
    },
    openEditModal(teacher) {
      this.isEdit = true
      this.form = { ...teacher, password: '' }
      this.showModal = true
    },
    closeModal() {
      this.showModal = false
    },
    async saveTeacher() {
      this.submitting = true
      // Set branch to null if empty
      if (this.form.branch === '') this.form.branch = null

      try {
        if (this.isEdit) {
          const editPayload = { ...this.form }
          // Only send password if user entered a new one
          if (!editPayload.password) {
            delete editPayload.password
          }
          await axios.put(`/api/users/${this.form.id}/`, editPayload)
        } else {
          await axios.post('/api/users/', this.form)
        }
        this.submitting = false
        this.closeModal()
        this.fetchData()
      } catch (err) {
        console.error('Error saving teacher:', err)
        alert(this.$t('common.error_save'))
        this.submitting = false
      }
    },
    async deleteTeacher(teacher) {
      if (!confirm(this.$t('teachers.delete_confirm', { name: teacher.first_name + ' ' + teacher.last_name }))) {
        return
      }

      try {
        await axios.delete(`/api/users/${teacher.id}/`)
        this.fetchData()
      } catch (err) {
        console.error('Error deleting teacher:', err)
        alert(this.$t('teachers.error_delete'))
      }
    },
    getBranchName(branchId) {
      if (!branchId) return '-'
      const branch = this.branches.find(b => b.id === branchId)
      return branch ? branch.name : `Branch #${branchId}`
    }
  }
}
</script>

<style scoped>
@import '../assets/views.css';

.teacher-link {
  color: #6366f1;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s;
}

.teacher-link:hover {
  color: #4f46e5;
  text-decoration: underline;
}
</style>
