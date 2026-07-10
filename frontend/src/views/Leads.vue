<template>
  <div class="view-container">
    <div class="view-header">
      <div>
        <h1 class="view-title">{{ $t('leads.title') }}</h1>
        <p class="view-subtitle">{{ $t('leads.sub') }}</p>
      </div>
      <div style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
        <div class="badge-count" v-if="filteredLeads.length">
          {{ filteredLeads.length }} {{ $t('common.total') }}
        </div>
        
        <button 
          v-if="selectedLeadIds.length > 0" 
          @click="openCreateGroupModal" 
          class="btn btn-primary"
        >
          🎓 {{ $t('leads.create_group') }} ({{ selectedLeadIds.length }})
        </button>

        <button @click="openCreateModal" class="btn btn-primary">
          <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          {{ $t('leads.new') }}
        </button>
      </div>
    </div>

    <!-- Filters Bar -->
    <div class="filter-bar">
      <div class="filter-group">
        <label class="filter-label">{{ $t('leads.col_course') }}</label>
        <select v-model="filterCourse" class="form-input filter-select">
          <option value="">{{ $t('common.all') }}</option>
          <option v-for="course in courses" :key="course.id" :value="course.id">
            {{ course.name }}
          </option>
        </select>
      </div>
      <div class="filter-group">
        <label class="filter-label">{{ $t('leads.col_status') }}</label>
        <select v-model="filterStatus" class="form-input filter-select">
          <option value="">{{ $t('common.all') }}</option>
          <option value="pending">{{ $t('leads.status_pending') }}</option>
          <option value="coming">{{ $t('leads.status_coming') }}</option>
          <option value="not_coming">{{ $t('leads.status_not_coming') }}</option>
          <option value="converted">{{ $t('leads.status_converted') }}</option>
        </select>
      </div>
      <div v-if="selectedLeadIds.length > 0" class="selection-count">
        {{ selectedLeadIds.length }} selected
      </div>
    </div>

    <!-- Error/Warning Banner -->
    <div v-if="error" class="error-banner">
      <span>{{ error }}</span>
    </div>

    <!-- Data Table Container -->
    <div class="table-card">
      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th style="width: 40px; text-align: center;">
                <input 
                  type="checkbox" 
                  :checked="isAllSelected" 
                  @change="toggleSelectAll"
                />
              </th>
              <th>ID</th>
              <th>{{ $t('leads.col_name') }}</th>
              <th>{{ $t('leads.col_phone') }}</th>
              <th>{{ $t('leads.col_course') }}</th>
              <th v-if="userRole === 'superuser' || userRole === 'CEO'">{{ $t('leads.col_branch') }}</th>
              <th>{{ $t('leads.col_status') }}</th>
              <th>{{ $t('leads.col_notes') }}</th>
              <th style="text-align: right;">{{ $t('common.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="lead in filteredLeads" :key="lead.id" class="table-row">
              <td style="text-align: center;">
                <input 
                  type="checkbox" 
                  :value="lead.id" 
                  v-model="selectedLeadIds"
                  :disabled="lead.status === 'converted'"
                />
              </td>
              <td class="font-mono text-muted">#{{ lead.id }}</td>
              <td class="font-semibold">{{ lead.full_name }}</td>
              <td>
                <a :href="'tel:' + lead.phone" class="phone-link">
                  📞 {{ lead.phone }}
                </a>
              </td>
              <td>
                <span class="course-badge">
                  {{ lead.course_name }}
                </span>
              </td>
              <td v-if="userRole === 'superuser' || userRole === 'CEO'">
                {{ lead.branch_name }}
              </td>
              <td>
                <span :class="['status-badge', 'status-' + lead.status]">
                  {{ $t('leads.status_' + lead.status) }}
                </span>
              </td>
              <td style="max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                {{ lead.notes || '-' }}
              </td>
              <td class="actions-cell">
                <!-- Inline Status Toggles -->
                <select 
                  :value="lead.status" 
                  @change="updateStatus(lead, $event.target.value)"
                  class="status-select-inline"
                >
                  <option value="pending">{{ $t('leads.status_pending') }}</option>
                  <option value="coming">{{ $t('leads.status_coming') }}</option>
                  <option value="not_coming">{{ $t('leads.status_not_coming') }}</option>
                  <option value="converted" disabled>{{ $t('leads.status_converted') }}</option>
                </select>

                <button @click="openEditModal(lead)" class="btn-icon" :title="$t('common.edit')">
                  <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 113 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                  </svg>
                </button>
                <button @click="deleteLead(lead)" class="btn-icon btn-icon-danger" :title="$t('common.delete')">
                  <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"></path>
                  </svg>
                </button>
              </td>
            </tr>
            <tr v-if="!filteredLeads.length && !loading">
              <td :colspan="(userRole === 'superuser' || userRole === 'CEO') ? 9 : 8" class="empty-state">
                {{ $t('leads.no_leads') }}
              </td>
            </tr>
            <tr v-if="loading">
              <td :colspan="(userRole === 'superuser' || userRole === 'CEO') ? 9 : 8" class="loading-state">
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
          <h2 class="modal-title">{{ isEdit ? $t('leads.modal_edit') : $t('leads.modal_new') }}</h2>
          <button @click="closeModal" class="modal-close">
            <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <form @submit.prevent="saveLead">
          <div class="modal-body">
            <div class="form-group">
              <label for="leadName" class="form-label">{{ $t('leads.col_name') }}</label>
              <input
                type="text"
                id="leadName"
                v-model="form.full_name"
                required
                :placeholder="$t('leads.placeholder_name')"
                class="form-input"
              />
            </div>
            
            <div class="form-group">
              <label for="leadPhone" class="form-label">{{ $t('leads.col_phone') }}</label>
              <div class="phone-input-wrapper">
                <span class="phone-prefix">+998</span>
                <input
                  type="text"
                  inputmode="numeric"
                  maxlength="12"
                  id="leadPhone"
                  :value="form.phone"
                  @input="handlePhoneInput($event, 'phone')"
                  @keypress="onlyNumber"
                  required
                  placeholder="90 123 45 67"
                  class="phone-editable-input"
                />
              </div>
            </div>

            <div class="form-group">
              <label for="leadCourse" class="form-label">{{ $t('leads.col_course') }}</label>
              <select id="leadCourse" v-model="form.course" required class="form-input">
                <option value="" disabled>{{ $t('leads.placeholder_course') }}</option>
                <option v-for="course in courses" :key="course.id" :value="course.id">
                  {{ course.name }}
                </option>
              </select>
            </div>

            <!-- Branch dropdown: only visible for Superuser/CEO, otherwise autopopulated -->
            <div class="form-group" v-if="userRole === 'superuser' || userRole === 'CEO'">
              <label for="leadBranch" class="form-label">{{ $t('leads.col_branch') }}</label>
              <select id="leadBranch" v-model="form.branch" required class="form-input">
                <option value="" disabled>{{ $t('leads.placeholder_branch') }}</option>
                <option v-for="b in branches" :key="b.id" :value="b.id">
                  {{ b.name }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label for="leadStatus" class="form-label">{{ $t('leads.col_status') }}</label>
              <select id="leadStatus" v-model="form.status" required class="form-input" :disabled="isEdit && form.status === 'converted'">
                <option value="pending">{{ $t('leads.status_pending') }}</option>
                <option value="coming">{{ $t('leads.status_coming') }}</option>
                <option value="not_coming">{{ $t('leads.status_not_coming') }}</option>
                <option value="converted" disabled v-if="!isEdit">{{ $t('leads.status_converted') }}</option>
                <option value="converted" v-if="isEdit && form.status === 'converted'">{{ $t('leads.status_converted') }}</option>
              </select>
            </div>

            <div class="form-group">
              <label for="leadNotes" class="form-label">{{ $t('leads.col_notes') }}</label>
              <textarea
                id="leadNotes"
                v-model="form.notes"
                :placeholder="$t('leads.placeholder_notes')"
                class="form-input"
                rows="3"
                style="resize: vertical; font-family: inherit;"
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

    <!-- Create Group Modal -->
    <div v-if="showCreateGroupModal" class="modal-backdrop" @click.self="closeCreateGroupModal">
      <div class="modal-content" style="max-width: 600px;">
        <div class="modal-header">
          <h2 class="modal-title">{{ $t('leads.modal_create_group') }}</h2>
          <button @click="closeCreateGroupModal" class="modal-close">
            <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <form @submit.prevent="submitCreateGroup">
          <div class="modal-body">
            
            <div v-if="groupModalWarning" class="warning-banner">
              ⚠️ {{ groupModalWarning }}
            </div>

            <div class="form-group">
              <label for="groupName" class="form-label">{{ $t('leads.group_name') }}</label>
              <input
                type="text"
                id="groupName"
                v-model="groupForm.name"
                required
                placeholder="e.g. Upper Intermediate Group A"
                class="form-input"
              />
            </div>

            <div class="modal-form-grid">
              <div class="form-group">
                <label for="groupCourse" class="form-label">{{ $t('leads.col_course') }}</label>
                <select id="groupCourse" v-model="groupForm.course" required class="form-input" disabled>
                  <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.name }}</option>
                </select>
              </div>
              <div class="form-group">
                <label for="groupTeacher" class="form-label">{{ $t('leads.teacher') }}</label>
                <select id="groupTeacher" v-model="groupForm.teacher" required class="form-input">
                  <option value="" disabled>{{ $t('groups.form_select_teacher') }}</option>
                  <option v-for="t in teachers" :key="t.id" :value="t.id">{{ t.first_name }} {{ t.last_name }}</option>
                </select>
              </div>
            </div>

            <div class="modal-form-grid">
              <div class="form-group">
                <label for="groupRoom" class="form-label">{{ $t('leads.room') }}</label>
                <select id="groupRoom" v-model="groupForm.room" required class="form-input">
                  <option value="" disabled>{{ $t('groups.form_select_room') }}</option>
                  <option v-for="r in filteredRooms" :key="r.id" :value="r.id">{{ r.name }}</option>
                </select>
              </div>
              <div class="form-group">
                <label for="groupDays" class="form-label">{{ $t('leads.group_days') }}</label>
                <select id="groupDays" v-model="groupForm.group_days_at" required class="form-input">
                  <option value="Mon-Wed-Fri">Mon-Wed-Fri</option>
                  <option value="Tue-Thur-Sat">Tue-Thur-Sat</option>
                  <option value="Everyday">Everyday</option>
                </select>
              </div>
            </div>

            <div class="modal-form-grid">
              <div class="form-group">
                <label for="startedAt" class="form-label">{{ $t('leads.started_at') }}</label>
                <input
                  type="date"
                  id="startedAt"
                  v-model="groupForm.started_at"
                  required
                  class="form-input"
                />
              </div>
              <div class="form-group">
                <label for="startsAt" class="form-label">{{ $t('leads.starts_at') }}</label>
                <input
                  type="time"
                  id="startsAt"
                  v-model="groupForm.starts_at"
                  required
                  class="form-input"
                />
              </div>
            </div>

            <div class="modal-form-grid">
              <div class="form-group">
                <label for="duration" class="form-label">{{ $t('leads.duration') }}</label>
                <input
                  type="number"
                  id="duration"
                  v-model.number="groupForm.duration"
                  required
                  min="1"
                  class="form-input"
                />
              </div>
              <div class="form-group">
                <label for="groupPrice" class="form-label">{{ $t('leads.price') }}</label>
                <input
                  type="text"
                  id="groupPrice"
                  v-model="groupForm.price_formatted"
                  @input="formatGroupFormPrice"
                  required
                  class="form-input"
                />
              </div>
            </div>

            <div class="form-group">
              <label for="teacherShare" class="form-label">{{ $t('leads.teacher_share') }}</label>
              <input
                type="number"
                id="teacherShare"
                v-model.number="groupForm.teacher_share"
                required
                min="0"
                max="100"
                class="form-input"
              />
            </div>

          </div>
          <div class="modal-footer">
            <button type="button" @click="closeCreateGroupModal" class="btn btn-secondary">{{ $t('common.cancel') }}</button>
            <button type="submit" class="btn btn-primary" :disabled="submittingGroup || !!groupModalWarning">
              {{ submittingGroup ? $t('common.loading') : $t('leads.submit_create_group') }}
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
  name: 'Leads',
  data() {
    return {
      leads: [],
      courses: [],
      branches: [],
      teachers: [],
      rooms: [],
      loading: false,
      error: null,

      // Search & Filters
      filterCourse: '',
      filterStatus: '',
      selectedLeadIds: [],

      // Add/Edit Lead Modal
      showModal: false,
      isEdit: false,
      submitting: false,
      userRole: localStorage.getItem('user_role') || '',
      userId: parseInt(localStorage.getItem('user_id')) || null,
      userBranchId: null,
      
      form: {
        id: null,
        full_name: '',
        phone: '',
        course: '',
        branch: '',
        status: 'pending',
        notes: ''
      },

      // Create Group Modal
      showCreateGroupModal: false,
      submittingGroup: false,
      groupForm: {
        name: '',
        course: '',
        teacher: '',
        room: '',
        started_at: new Date().toISOString().split('T')[0],
        starts_at: '09:00',
        duration: 90,
        price_formatted: '',
        teacher_share: 50,
        group_days_at: 'Mon-Wed-Fri'
      }
    }
  },
  computed: {
    filteredLeads() {
      let list = this.leads
      if (this.filterCourse) {
        list = list.filter(l => l.course === parseInt(this.filterCourse))
      }
      if (this.filterStatus) {
        list = list.filter(l => l.status === this.filterStatus)
      }
      return list
    },
    isAllSelected() {
      const activeLeads = this.filteredLeads.filter(l => l.status !== 'converted')
      if (activeLeads.length === 0) return false
      return activeLeads.every(l => this.selectedLeadIds.includes(l.id))
    },
    filteredRooms() {
      if (this.userBranchId) {
        return this.rooms.filter(r => r.branch === this.userBranchId)
      }
      return this.rooms
    },
    groupModalWarning() {
      if (this.selectedLeadIds.length === 0) return null
      
      // Verify all selected leads share the exact same course
      const selectedLeads = this.leads.filter(l => this.selectedLeadIds.includes(l.id))
      const firstCourseId = selectedLeads[0].course
      const differentCourse = selectedLeads.some(l => l.course !== firstCourseId)
      if (differentCourse) {
        return this.$t('leads.error_select_leads') + " (Leads have different course preferences)"
      }
      
      // Verify all selected leads belong to the same branch
      const firstBranchId = selectedLeads[0].branch
      const differentBranch = selectedLeads.some(l => l.branch !== firstBranchId)
      if (differentBranch) {
        return "Selected leads belong to different branches. Please select leads from the same branch."
      }

      return null
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
        const [leadsRes, coursesRes, branchesRes, usersRes, roomsRes] = await Promise.all([
          axios.get('/api/leads/'),
          axios.get('/api/courses/'),
          axios.get('/api/branches/'),
          axios.get('/api/users/'),
          axios.get('/api/rooms/')
        ])

        this.leads = leadsRes.data
        this.courses = coursesRes.data
        this.branches = branchesRes.data
        this.teachers = usersRes.data.filter(u => u.role === 'teacher' && u.is_active)
        this.rooms = roomsRes.data
        // console.log(this.rooms)

        if (this.userId) {
          try {
            const userProfileRes = await axios.get(`/api/users/${this.userId}/`)
            this.userBranchId = userProfileRes.data.branch
          } catch (profileErr) {
            console.error('Error fetching user profile branch:', profileErr)
          }
        }
      } catch (err) {
        console.error('Error loading leads page data:', err)
        this.error = this.$t('stats.api_error')
      } finally {
        this.loading = false
      }
    },
    toggleSelectAll() {
      const activeLeads = this.filteredLeads.filter(l => l.status !== 'converted')
      if (this.isAllSelected) {
        this.selectedLeadIds = this.selectedLeadIds.filter(
          id => !activeLeads.some(l => l.id === id)
        )
      } else {
        const idsToAdd = activeLeads.map(l => l.id).filter(id => !this.selectedLeadIds.includes(id))
        this.selectedLeadIds = [...this.selectedLeadIds, ...idsToAdd]
      }
    },
    openCreateModal() {
      this.isEdit = false
      this.form = {
        id: null,
        full_name: '',
        phone: '',
        course: '',
        branch: this.userBranchId || '',
        status: 'pending',
        notes: ''
      }
      this.showModal = true
    },
    openEditModal(lead) {
      this.isEdit = true
      this.form = {
        id: lead.id,
        full_name: lead.full_name,
        phone: this.parsePhoneForInput(lead.phone),
        course: lead.course,
        branch: lead.branch,
        status: lead.status,
        notes: lead.notes || ''
      }
      this.showModal = true
    },
    closeModal() {
      this.showModal = false
    },
    async saveLead() {
      this.submitting = true
      
      const rawPhone = this.form.phone.replace(/\D/g, '')
      if (rawPhone.length !== 9) {
        alert(this.$t('students.phone_length_error'))
        this.submitting = false
        return
      }

      const payload = {
        ...this.form,
        phone: '+998' + rawPhone
      }

      try {
        if (this.isEdit) {
          await axios.put(`/api/leads/${this.form.id}/`, payload)
        } else {
          await axios.post('/api/leads/', payload)
        }
        this.closeModal()
        this.fetchData()
      } catch (err) {
        console.error('Error saving lead:', err)
        alert(this.$t('common.error_save'))
      } finally {
        this.submitting = false
      }
    },
    async updateStatus(lead, newStatus) {
      try {
        const payload = {
          full_name: lead.full_name,
          phone: lead.phone,
          course: lead.course,
          branch: lead.branch,
          status: newStatus,
          notes: lead.notes
        }
        await axios.put(`/api/leads/${lead.id}/`, payload)
        this.fetchData()
      } catch (err) {
        console.error('Error updating status:', err)
        alert(this.$t('common.error_save'))
      }
    },
    async deleteLead(lead) {
      if (confirm(this.$t('leads.delete_confirm'))) {
        try {
          await axios.delete(`/api/leads/${lead.id}/`)
          this.fetchData()
        } catch (err) {
          console.error('Error deleting lead:', err)
          alert(this.$t('common.error_delete'))
        }
      }
    },
    openCreateGroupModal() {
      if (this.selectedLeadIds.length === 0) return
      
      const selectedLeads = this.leads.filter(l => this.selectedLeadIds.includes(l.id))
      const firstCourseId = selectedLeads[0].course
      const course = this.courses.find(c => c.id === firstCourseId)
      
      let priceFormatted = ''
      if (course && course.price) {
        const digits = Math.round(parseFloat(course.price)).toString()
        priceFormatted = digits.replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
      }

      this.groupForm = {
        name: `${course ? course.name : ''} Group`,
        course: firstCourseId,
        teacher: '',
        room: '',
        started_at: new Date().toISOString().split('T')[0],
        starts_at: '09:00',
        duration: 90,
        price_formatted: priceFormatted,
        teacher_share: 50,
        group_days_at: 'Mon-Wed-Fri'
      }
      
      this.showCreateGroupModal = true
    },
    closeCreateGroupModal() {
      this.showCreateGroupModal = false
    },
    formatGroupFormPrice(event) {
      const value = event.target.value
      const digits = value.replace(/\D/g, '')
      this.groupForm.price_formatted = digits.replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
    },
    async submitCreateGroup() {
      this.submittingGroup = true
      try {
        const rawPrice = String(this.groupForm.price_formatted).replace(/\s/g, '')
        const priceVal = parseFloat(rawPrice || 0).toFixed(2)
        const payload = {
          name: this.groupForm.name,
          course: this.groupForm.course,
          teacher: this.groupForm.teacher,
          room: this.groupForm.room,
          started_at: this.groupForm.started_at,
          starts_at: this.groupForm.starts_at,
          duration: this.groupForm.duration,
          price: priceVal,
          teacher_share: this.groupForm.teacher_share,
          group_days_at: this.groupForm.group_days_at,
          lead_ids: this.selectedLeadIds
        }

        const response = await axios.post('/api/leads/create-group/', payload)
        this.closeCreateGroupModal()
        this.selectedLeadIds = []
        
        // Redirect to new group page!
        const newGroupId = response.data.id
        this.$router.push(`/groups/${newGroupId}`)
      } catch (err) {
        console.error('Error creating group from leads:', err)
        alert(err.response?.data?.detail || err.response?.data?.[0] || 'Error creating group')
      } finally {
        this.submittingGroup = false
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
    }
  }
}
</script>

<style scoped>
@import '../assets/views.css';

/* Scoped styles for Leads view */
.course-badge {
  background-color: #f1f5f9;
  color: #475569;
  padding: 0.25rem 0.625rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 500;
  display: inline-block;
}

.phone-link {
  color: #4f46e5;
  text-decoration: none;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  transition: opacity 0.15s ease;
}

.phone-link:hover {
  text-decoration: underline !important;
  opacity: 0.95;
}

/* Inline Lead Badge Status Overrides */
.status-badge.status-pending {
  background-color: #ffedd5;
  color: #c2410c;
}
.status-badge.status-coming {
  background-color: #dcfce7;
  color: #15803d;
}
.status-badge.status-not_coming {
  background-color: #fee2e2;
  color: #b91c1c;
}
.status-badge.status-converted {
  background-color: #e0e7ff;
  color: #4338ca;
}

.status-select-inline {
  padding: 0.35rem 0.5rem;
  border-radius: 8px;
  border: 1px solid #cbd5e1;
  font-size: 0.8rem;
  font-weight: 500;
  margin-right: 0.5rem;
  background-color: #fff;
  cursor: pointer;
  outline: none;
  transition: all 0.2s ease;
}
.status-select-inline:hover {
  border-color: #94a3b8;
}
.status-select-inline:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1);
}

/* Warning and Error Banners */
.warning-banner {
  background-color: #fffbeb;
  border: 1px solid #fef3c7;
  color: #b45309;
  padding: 0.875rem 1.25rem;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  font-size: 0.875rem;
  line-height: 1.4;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.error-banner {
  background-color: #fef2f2;
  border: 1px solid #fca5a5;
  color: #b91c1c;
  padding: 0.875rem 1.25rem;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  font-size: 0.875rem;
  line-height: 1.4;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Filter bar styling overrides */
.filter-bar {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1rem 1.25rem;
  margin-bottom: 1.5rem;
  display: flex;
  gap: 1.25rem;
  flex-wrap: wrap;
  align-items: center;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  min-width: 200px;
}

.filter-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.filter-select {
  padding: 0.5rem 2.5rem 0.5rem 0.75rem !important;
  margin-bottom: 0;
}

.selection-count {
  margin-left: auto;
  color: #6366f1;
  font-weight: 600;
  font-size: 0.9rem;
  background-color: rgba(99, 102, 241, 0.08);
  padding: 0.35rem 0.75rem;
  border-radius: 8px;
}

input[type="checkbox"] {
  cursor: pointer;
  width: 16px;
  height: 16px;
  accent-color: #6366f1;
}
</style>
