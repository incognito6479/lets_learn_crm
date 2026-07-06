<template>
  <div class="view-container">
    <div class="view-header">
      <div>
        <h1 class="view-title">{{ $t('groups.title') }}</h1>
        <p class="view-subtitle">{{ $t('groups.sub') }}</p>
      </div>
      <div style="display: flex; gap: 1rem; align-items: center;">
        <div class="badge-count" v-if="groups.length">{{ $t('common.total') }}: {{ groups.length }}</div>
        <button v-if="userRole !== 'teacher'" @click="openImportModal" class="btn btn-secondary" style="background-color: #4b5563; border-color: #4b5563; color: white;">
          <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="17 8 12 3 7 8"></polyline>
            <line x1="12" y1="3" x2="12" y2="15"></line>
          </svg>
          {{ $t('groups.import_btn') }}
        </button>
        <button v-if="userRole !== 'teacher'" @click="openCreateModal" class="btn btn-primary">
          <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          {{ $t('groups.new') }}
        </button>
      </div>
    </div>

    <!-- Error/Warning Banner -->
    <div v-if="error" class="info-banner">
      <span>{{ error }}</span>
    </div>

    <!-- Search & Filter Controls -->
    <div class="filter-bar" style="margin-bottom: 1.5rem; display: flex; gap: 1rem; flex-wrap: wrap;">
      <div style="flex: 1; min-width: 260px; max-width: 320px;">
        <input
          type="text"
          v-model="searchQuery"
          :placeholder="$t('groups.search_placeholder')"
          class="form-input"
        />
      </div>
      
      <div style="width: 200px;">
        <select v-model="selectedBranch" class="form-input">
          <option value="">{{ $t('groups.all_branches') }}</option>
          <option v-for="branch in branches" :key="branch.id" :value="branch.id">
            {{ branch.name }}
          </option>
        </select>
      </div>

      <div style="width: 200px;">
        <select v-model="selectedCourse" class="form-input">
          <option value="">{{ $t('groups.all_courses') }}</option>
          <option v-for="course in courses" :key="course.id" :value="course.id">
            {{ course.name }}
          </option>
        </select>
      </div>
    </div>

    <!-- Data Table Container -->
    <div class="table-card">
      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>{{ $t('groups.form_name') }}</th>
              <th>{{ $t('groups.col_course') }}</th>
              <th>{{ $t('groups.col_teacher') }}</th>
              <th>{{ $t('groups.col_room') }}</th>
              <th>{{ $t('groups.col_days') }}</th>
              <th>{{ $t('groups.col_branch') }}</th>
              <th>{{ $t('common.status') }}</th>
              <th>{{ $t('common.price') }}</th>
              <th style="text-align: right;">{{ $t('common.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="group in filteredGroups" :key="group.id" class="table-row clickable-row" @click="navigateToGroup(group.id)">
              <td class="font-mono text-muted">#{{ group.id }}</td>
              <td class="font-semibold">{{ group.name }}</td>
              <td>{{ getCourseName(group.course) }}</td>
              <td>{{ getTeacherName(group.teacher) }}</td>
              <td>{{ getRoomName(group.room) }}</td>
              <td>{{ $t('groups.' + (group.group_days_at || 'Mon-Wed-Fri')) }}</td>
              <td>{{ getBranchName(group.branch) }}</td>
              <td>
                <span :class="['status-badge', group.status || 'enrolled']">
                  {{ $t('groups.status_' + (group.status || 'enrolled')) }}
                </span>
              </td>
              <td class="font-mono font-semibold">{{ formatPrice(group.price) }} UZS</td>
              <td class="actions-cell">
                <button @click.stop="navigateToGroup(group.id)" class="btn-icon" title="View Group Details">
                  <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                  </svg>
                </button>
                <button v-if="userRole !== 'teacher'" @click.stop="openEditModal(group)" class="btn-icon" title="Edit Group">
                  <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 113 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                  </svg>
                </button>
                <button v-if="userRole !== 'teacher'" @click.stop="deleteGroup(group)" class="btn-icon btn-icon-danger" title="Delete Group">
                  <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"></path>
                    <line x1="10" y1="11" x2="10" y2="17"></line>
                    <line x1="14" y1="11" x2="14" y2="17"></line>
                  </svg>
                </button>
              </td>
            </tr>
            <tr v-if="!filteredGroups.length && !loading">
              <td colspan="10" class="empty-state">{{ $t('groups.no_groups') }}</td>
            </tr>
            <tr v-if="loading">
              <td colspan="10" class="loading-state">
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
      <div class="modal-content" style="max-width: 540px; max-height: 90vh; display: flex; flex-direction: column;">
        <div class="modal-header" style="flex-shrink: 0;">
          <h2 class="modal-title">{{ isEdit ? $t('groups.modal_edit') : $t('groups.modal_new') }}</h2>
          <button @click="closeModal" class="modal-close">
            <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <form @submit.prevent="saveGroup" style="display: flex; flex-direction: column; overflow: hidden; flex: 1;">
          <div class="modal-body" style="overflow-y: auto; flex: 1;">
            <div class="form-group">
              <label for="groupName" class="form-label">{{ $t('groups.form_name') }}</label>
              <input
                type="text"
                id="groupName"
                v-model="form.name"
                required
                :placeholder="$t('groups.form_name')"
                class="form-input"
              />
            </div>
            
            <div class="modal-form-grid">
              <div class="form-group">
                <label for="groupBranch" class="form-label">{{ $t('groups.col_branch') }}</label>
                <select id="groupBranch" v-model="form.branch" required class="form-input">
                  <option value="" disabled>{{ $t('groups.form_select_branch') }}</option>
                  <option v-for="branch in branches" :key="branch.id" :value="branch.id">
                    {{ branch.name }}
                  </option>
                </select>
              </div>
 
              <div class="form-group">
                <label for="groupRoom" class="form-label">{{ $t('groups.col_room') }}</label>
                <select id="groupRoom" v-model="form.room" required class="form-input" :disabled="!form.branch">
                  <option value="" disabled>{{ form.branch ? $t('groups.form_select_room') : $t('groups.form_select_branch_first') }}</option>
                  <option v-for="room in filteredRooms" :key="room.id" :value="room.id">
                    {{ room.name }}
                  </option>
                </select>
              </div>
            </div>
 
            <div class="modal-form-grid">
              <div class="form-group">
                <label for="groupCourse" class="form-label">{{ $t('groups.col_course') }}</label>
                <select id="groupCourse" v-model="form.course" required class="form-input" @change="handleCourseChange">
                  <option value="" disabled>{{ $t('groups.form_select_course') }}</option>
                  <option v-for="course in courses" :key="course.id" :value="course.id">
                    {{ course.name }}
                  </option>
                </select>
              </div>
 
              <div class="form-group">
                <label for="groupTeacher" class="form-label">{{ $t('groups.col_teacher') }}</label>
                <select id="groupTeacher" v-model="form.teacher" required class="form-input">
                  <option value="" disabled>{{ $t('groups.form_select_teacher') }}</option>
                  <option v-for="teacher in teachers" :key="teacher.id" :value="teacher.id">
                    {{ teacher.first_name }} {{ teacher.last_name }}
                  </option>
                </select>
              </div>
            </div>
 
            <div class="modal-form-grid">
              <div class="form-group">
                <label for="startedAt" class="form-label">{{ $t('groups.form_start_date') }}</label>
                <input
                  type="date"
                  id="startedAt"
                  v-model="form.started_at"
                  required
                  class="form-input"
                />
              </div>
 
              <div class="form-group">
                <label for="startsAt" class="form-label">{{ $t('groups.form_time') }}</label>
                <input
                  type="time"
                  id="startsAt"
                  v-model="form.starts_at"
                  required
                  class="form-input"
                />
              </div>
            </div>
 
            <div class="modal-form-grid">
              <div class="form-group">
                <label for="duration" class="form-label">{{ $t('groups.form_duration') }}</label>
                <input
                  type="number"
                  id="duration"
                  v-model.number="form.duration"
                  required
                  min="1"
                  placeholder="e.g. 90"
                  class="form-input"
                />
              </div>
 
              <div class="form-group">
                <label for="groupPrice" class="form-label">{{ $t('groups.col_price') }}</label>
                <input
                  type="text"
                  inputmode="numeric"
                  id="groupPrice"
                  :value="form.price"
                  @input="formatInputPrice"
                  required
                  class="form-input"
                />
              </div>
            </div>

            <div class="modal-form-grid">
              <div class="form-group">
                <label for="groupDays" class="form-label">{{ $t('groups.col_days') }}</label>
                <select id="groupDays" v-model="form.group_days_at" required class="form-input">
                  <option value="Mon-Wed-Fri">{{ $t('groups.Mon-Wed-Fri') }}</option>
                  <option value="Tue-Thur-Sat">{{ $t('groups.Tue-Thur-Sat') }}</option>
                  <option value="Everyday">{{ $t('groups.Everyday') }}</option>
                </select>
              </div>

              <div class="form-group">
                <label for="teacherShare" class="form-label">{{ $t('groups.form_teacher_share') }}</label>
                <input
                  type="number"
                  id="teacherShare"
                  v-model.number="form.teacher_share"
                  required
                  min="0"
                  max="100"
                  class="form-input"
                />
              </div>
            </div>
            <div class="modal-form-grid">
              <div class="form-group">
                <label for="groupStatus" class="form-label">{{ $t('common.status') }}</label>
                <select id="groupStatus" v-model="form.status" required class="form-input">
                  <option value="ongoing">{{ $t('groups.status_ongoing') }}</option>
                  <option value="finished">{{ $t('groups.status_finished') }}</option>
                  <option value="enrolled">{{ $t('groups.status_enrolled') }}</option>
                </select>
              </div>
            </div>
 
            <div class="form-group">
              <label for="description" class="form-label">{{ $t('common.description') }}</label>
              <textarea
                id="description"
                v-model="form.description"
                placeholder="..."
                class="form-input"
                rows="3"
                style="resize: vertical; font-family: inherit;"
              ></textarea>
            </div>
          </div>
          <div class="modal-footer" style="flex-shrink: 0;">
            <button type="button" @click="closeModal" class="btn btn-secondary">{{ $t('common.cancel') }}</button>
            <button type="submit" class="btn btn-primary" :disabled="submitting">
              {{ submitting ? $t('common.saving') : $t('common.save') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Import Excel Modal -->
    <div v-if="showImportModal" class="modal-backdrop" @click.self="closeImportModal">
      <div class="modal-content" style="max-width: 500px;">
        <div class="modal-header">
          <h2 class="modal-title">{{ $t('groups.import_modal_title') }}</h2>
          <button @click="closeImportModal" class="modal-close">
            <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <div class="modal-body" style="padding: 1.5rem 0;">
          <p class="modal-instructions" style="margin-bottom: 1.5rem; color: #cbd5e1; font-size: 0.95rem; line-height: 1.5; text-align: left;">
            {{ $t('groups.import_instructions') }}
          </p>

          <!-- Import Options Grid -->
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem; text-align: left;">
            <div class="form-group" style="display: flex; flex-direction: column; gap: 0.4rem;">
              <label class="form-label" style="font-size: 0.85rem; font-weight: 500; color: #cbd5e1;">{{ $t('groups.import_month') }}</label>
              <select v-model="importMonth" class="form-input" style="width: 100%; box-sizing: border-box; background-color: #1e293b; color: white;">
                <option v-for="m in 12" :key="m" :value="m">
                  {{ getLocalizedMonthName(m - 1) }}
                </option>
              </select>
            </div>
            
            <div class="form-group" style="display: flex; flex-direction: column; gap: 0.4rem;">
              <label class="form-label" style="font-size: 0.85rem; font-weight: 500; color: #cbd5e1;">{{ $t('groups.import_year') }}</label>
              <select v-model="importYear" class="form-input" style="width: 100%; box-sizing: border-box; background-color: #1e293b; color: white;">
                <option v-for="y in importYearRange" :key="y" :value="y">
                  {{ y }}
                </option>
              </select>
            </div>
          </div>

          <div class="form-group" style="display: flex; flex-direction: column; gap: 0.4rem; margin-bottom: 1.5rem; text-align: left;">
            <label class="form-label" style="font-size: 0.85rem; font-weight: 500; color: #cbd5e1;">{{ $t('groups.import_price') }}</label>
            <input
              type="text"
              inputmode="numeric"
              v-model="importPriceRaw"
              @input="formatImportPriceInput"
              required
              class="form-input"
              style="width: 100%; box-sizing: border-box; background-color: #1e293b; color: white;"
            />
          </div>
          
          <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; border: 2px dashed #4b5563; border-radius: 8px; padding: 2rem; background-color: #0f172a; transition: all 0.2s;">
            <svg style="width: 3rem; height: 3rem; color: #94a3b8; margin-bottom: 1rem;" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
            <input 
              type="file" 
              ref="excelFileInput" 
              accept=".xlsx, .xls" 
              style="display: none;" 
              @change="handleFileChange"
            />
            <button 
              type="button" 
              @click="$refs.excelFileInput.click()" 
              class="btn btn-secondary" 
              style="background-color: #334155; color: white;"
            >
              {{ selectedFile ? selectedFile.name : $t('groups.import_select_file') }}
            </button>
          </div>
        </div>
        <div class="modal-footer" style="padding-top: 1rem; border-top: 1px solid #334155;">
          <button type="button" @click="closeImportModal" class="btn btn-secondary">{{ $t('groups.import_close') }}</button>
          <button 
            type="button" 
            @click="submitImport" 
            class="btn btn-primary" 
            :disabled="importing || !selectedFile"
          >
            {{ importing ? $t('groups.import_submitting') : $t('groups.import_btn') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Groups',
  data() {
    return {
      groups: [],
      courses: [],
      teachers: [],
      rooms: [],
      branches: [],
      loading: false,
      error: null,

      // Search and Filter controls
      searchQuery: '',
      selectedBranch: '',
      selectedCourse: '',

      // Modal controls
      showModal: false,
      isEdit: false,
      submitting: false,
      userRole: localStorage.getItem('user_role') || '',
      userId: parseInt(localStorage.getItem('user_id')) || null,
      
      // Import controls
      showImportModal: false,
      selectedFile: null,
      importing: false,
      importMonth: new Date().getMonth() + 1,
      importYear: new Date().getFullYear(),
      importPriceRaw: '450 000',
      form: {
        id: null,
        name: '',
        branch: '',
        course: '',
        teacher: '',
        room: '',
        started_at: '',
        starts_at: '',
        duration: 90,
        price: '',
        status: 'ongoing',
        group_days_at: 'Mon-Wed-Fri',
        teacher_share: 50,
        description: ''
      }
    }
  },
  computed: {
    filteredGroups() {
      let list = this.groups
      
      // Filter by search query (group name)
      const query = this.searchQuery.toLowerCase().trim()
      if (query) {
        list = list.filter(g => g.name && g.name.toLowerCase().includes(query))
      }
      
      // Filter by selected branch
      if (this.selectedBranch) {
        list = list.filter(g => g.branch === this.selectedBranch)
      }
      
      // Filter by selected course
      if (this.selectedCourse) {
        list = list.filter(g => g.course === this.selectedCourse)
      }
      
      return list
    },
    filteredRooms() {
      if (!this.form.branch) return []
      return this.rooms.filter(r => r.branch === this.form.branch)
    },
    importYearRange() {
      const cy = new Date().getFullYear()
      return [cy - 2, cy - 1, cy, cy + 1, cy + 2]
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
        const [groupsRes, coursesRes, usersRes, roomsRes, branchesRes] = await Promise.all([
          axios.get('/api/groups/'),
          axios.get('/api/courses/'),
          axios.get('/api/users/'),
          axios.get('/api/rooms/'),
          axios.get('/api/branches/')
        ])
        
        let groupsData = groupsRes.data
        if (this.userRole === 'teacher' && this.userId) {
          groupsData = groupsData.filter(g => g.teacher === this.userId)
        }
        this.groups = groupsData
        this.courses = coursesRes.data
        this.teachers = usersRes.data.filter(u => u.role === 'teacher')
        this.rooms = roomsRes.data
        this.branches = branchesRes.data
      } catch (err) {
        console.error('Error fetching groups data:', err)
        this.error = 'Unable to connect to backend API. Please check server status.'
      } finally {
        this.loading = false
      }
    },
    getCourseName(id) {
      const item = this.courses.find(c => c.id === id)
      return item ? item.name : `Course #${id}`
    },
    getTeacherName(id) {
      const item = this.teachers.find(t => t.id === id)
      return item ? `${item.first_name} ${item.last_name}` : `Teacher #${id}`
    },
    getRoomName(id) {
      const item = this.rooms.find(r => r.id === id)
      return item ? item.name : `Room #${id}`
    },
    getBranchName(id) {
      const item = this.branches.find(b => b.id === id)
      return item ? item.name : `Branch #${id}`
    },
    formatTime(timeStr) {
      if (!timeStr) return '-'
      const parts = timeStr.split(':')
      if (parts.length >= 2) {
        return `${parts[0]}:${parts[1]}`
      }
      return timeStr
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      try {
        const date = new Date(dateStr)
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
      } catch (e) {
        return dateStr
      }
    },
    handleCourseChange() {
      // Do not auto-fill group price with course price
    },
    openCreateModal() {
      this.isEdit = false
      this.form = {
        id: null,
        name: '',
        branch: '',
        course: '',
        teacher: '',
        room: '',
        started_at: '',
        starts_at: '',
        duration: 90,
        price: '',
        status: 'ongoing',
        group_days_at: 'Mon-Wed-Fri',
        teacher_share: 50,
        description: ''
      }
      this.showModal = true
    },
    openEditModal(group) {
      this.isEdit = true
      this.form = {
        id: group.id,
        name: group.name,
        branch: group.branch,
        course: group.course,
        teacher: group.teacher,
        room: group.room,
        started_at: group.started_at,
        starts_at: group.starts_at ? group.starts_at.slice(0, 5) : '',
        duration: group.duration,
        price: group.price,
        status: group.status || 'ongoing',
        group_days_at: group.group_days_at || 'Mon-Wed-Fri',
        teacher_share: group.teacher_share || 50,
        description: group.description || ''
      }
      if (this.form.price) {
        const digits = Math.round(parseFloat(this.form.price)).toString()
        this.form.price = digits.replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
      } else {
        this.form.price = ''
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

      const digits = value.replace(/\D/g, '')
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
    async saveGroup() {
      this.submitting = true
      try {
        const rawPrice = String(this.form.price).replace(/\s/g, '')
        const priceVal = parseFloat(rawPrice || 0).toFixed(2)
        const payload = {
          ...this.form,
          price: priceVal
        }

        if (this.isEdit) {
          await axios.put(`/api/groups/${this.form.id}/`, payload)
          this.closeModal()
          this.fetchData()
        } else {
          const response = await axios.post('/api/groups/', payload)
          this.closeModal()
          const newGroupId = response.data.id
          this.$router.push(`/groups/${newGroupId}`)
        }
      } catch (err) {
        console.error('Error saving group:', err)
        alert(this.$t('groups.error_save'))
      } finally {
        this.submitting = false
      }
    },
    async deleteGroup(group) {
      if (!confirm(this.$t('groups.delete_confirm', { name: group.name }))) {
        return
      }
      try {
        await axios.delete(`/api/groups/${group.id}/`)
        this.fetchData()
      } catch (err) {
        console.error('Error deleting group:', err)
        alert(this.$t('groups.error_delete'))
      }
    },
    navigateToGroup(id) {
      this.$router.push(`/groups/${id}`)
    },
    formatPrice(price) {
      if (!price && price !== 0) return '0'
      const val = Math.round(parseFloat(price))
      return val.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
    },
    openImportModal() {
      this.selectedFile = null
      this.importMonth = new Date().getMonth() + 1
      this.importYear = new Date().getFullYear()
      this.importPriceRaw = '450 000'
      this.showImportModal = true
    },
    closeImportModal() {
      this.showImportModal = false
      this.selectedFile = null
      this.importing = false
    },
    handleFileChange(event) {
      const files = event.target.files
      if (files.length > 0) {
        this.selectedFile = files[0]
      }
    },
    getLocalizedMonthName(monthIdx) {
      const date = new Date(2026, monthIdx, 1)
      const locale = this.$i18n.locale === 'uz' ? 'uz-UZ' : 'ru-RU'
      return date.toLocaleDateString(locale, { month: 'long' })
    },
    formatImportPriceInput(event) {
      const selectionStart = event.target.selectionStart
      const value = event.target.value
      const oldLength = value.length
      
      const digits = value.replace(/\D/g, '')
      const formatted = digits.replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
      
      this.importPriceRaw = formatted
      
      this.$nextTick(() => {
        if (event.target) {
          const newLength = formatted.length
          const delta = newLength - oldLength
          const newCursorPos = selectionStart + delta
          event.target.setSelectionRange(newCursorPos, newCursorPos)
        }
      })
    },
    async submitImport() {
      if (!this.selectedFile) return
      this.importing = true
      const formData = new FormData()
      formData.append('file', this.selectedFile)
      formData.append('month', this.importMonth)
      formData.append('year', this.importYear)
      
      const parsedPrice = parseFloat(this.importPriceRaw.replace(/\s/g, '')) || 450000
      formData.append('price', parsedPrice)
      
      try {
        const response = await axios.post('/api/groups/import-excel/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        alert(this.$t('groups.import_success') + `\n\n- Groups: ${response.data.imported_groups.join(', ')}\n- Students: ${response.data.total_students}\n- Payments: ${response.data.total_payments}\n- Absences: ${response.data.total_absences}`)
        
        this.closeImportModal()
        this.fetchData()
      } catch (err) {
        console.error('Error importing Excel:', err)
        alert(err.response?.data?.detail || err.response?.data?.message || 'Error importing file.')
      } finally {
        this.importing = false
      }
    }
  }
}
</script>

<style scoped>
@import '../assets/views.css';

.schedule-cell {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.starts-time {
  font-weight: 600;
  color: #0f172a;
}

.started-date {
  font-size: 0.8rem;
}

.clickable-row {
  cursor: pointer;
}

.group-link {
  color: #4f46e5;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.15s;
}

.group-link:hover {
  color: #3730a3;
  text-decoration: underline;
}

.status-badge.ongoing {
  background-color: #e0f2fe;
  color: #0369a1;
}

.status-badge.enrolled {
  background-color: #dcfce7;
  color: #15803d;
}

.status-badge.finished {
  background-color: #f1f5f9;
  color: #475569;
}
</style>
