<template>
  <div class="view-container">
    <!-- Back Navigation -->
    <div style="margin-bottom: 1.5rem; text-align: left;">
      <button @click="$router.back()" class="btn btn-secondary back-btn">
        <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="19" y1="12" x2="5" y2="12"></line>
          <polyline points="12 19 5 12 12 5"></polyline>
        </svg>
        {{ $t('common.back') }}
      </button>
    </div>

    <!-- Error/Warning Banner -->
    <div v-if="error" class="info-banner">
      <span>{{ error }}</span>
    </div>

    <div v-if="loading" class="loading-state-full" style="padding: 10rem 0; text-align: center;">
      <div class="spinner"></div>
      <span style="margin-top: 1rem; display: block; color: #64748b;">{{ $t('groupDetail.loading') }}</span>
    </div>

    <div v-if="!loading && teacher" class="detail-grid-layout" style="display: flex; flex-direction: column; gap: 1.5rem;">
      <!-- Teacher Profile Card -->
      <div class="detail-card glass-panel" style="background: white; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); overflow: hidden;">
        <div class="panel-header" style="padding: 1.5rem; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center;">
          <h2 class="panel-title" style="margin: 0; font-size: 1.25rem; font-weight: 700; color: #0f172a;">{{ $t('teacherDetail.title') }}</h2>
          <span :class="['status-badge', teacher.is_active ? 'active' : 'dropped']" style="padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase;">
            {{ teacher.is_active ? $t('teachers.active') : $t('teachers.inactive') }}
          </span>
        </div>
        <div class="panel-body" style="padding: 1.5rem;">
          <div class="profile-header-block" style="display: flex; align-items: center; gap: 1.5rem; margin-bottom: 2rem;">
            <div class="avatar-large" style="width: 70px; height: 70px; border-radius: 50%; background-color: rgba(99, 102, 241, 0.1); color: #6366f1; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; font-weight: 700;">
              {{ getInitials(teacher.first_name, teacher.last_name) }}
            </div>
            <div>
              <h3 class="profile-name" style="margin: 0 0 0.25rem 0; font-size: 1.5rem; font-weight: 700; color: #0f172a;">{{ teacher.first_name }} {{ teacher.last_name }}</h3>
              <p class="profile-username" style="margin: 0; font-size: 0.9rem; color: #64748b;">@{{ teacher.username }}</p>
            </div>
          </div>
          
          <div class="info-fields-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.5rem;">
            <div class="info-field">
              <span class="field-label" style="display: block; font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; font-weight: 600; margin-bottom: 0.25rem;">{{ $t('common.phone') }}</span>
              <span class="field-value" style="font-size: 1rem; color: #1e293b; font-weight: 500;">{{ teacher.phone_number || '-' }}</span>
            </div>
            <div class="info-field">
              <span class="field-label" style="display: block; font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; font-weight: 600; margin-bottom: 0.25rem;">{{ $t('teachers.form_branch') }}</span>
              <span class="field-value" style="font-size: 1rem; color: #1e293b; font-weight: 500;">{{ getBranchName(teacher.branch) }}</span>
            </div>
            <div class="info-field">
              <span class="field-label" style="display: block; font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; font-weight: 600; margin-bottom: 0.25rem;">{{ $t('teachers.col_status') }}</span>
              <span class="field-value" style="font-size: 1rem; color: #1e293b; font-weight: 500; text-transform: capitalize;">{{ teacher.role === 'teacher' ? $t('groupDetail.teacher') : teacher.role }}</span>
            </div>
            <div class="info-field">
              <span class="field-label" style="display: block; font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; font-weight: 600; margin-bottom: 0.25rem;">{{ $t('teacherDetail.monthly_income') }}</span>
              <span class="field-value font-mono font-semibold" style="font-size: 1.1rem; color: #16a34a; font-weight: 700;">{{ formatPrice(currentMonthIncome) }} UZS</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Pending Notifications Alert -->
      <div v-if="pendingNotifications.length" class="detail-card glass-panel" style="background: #fffbeb; border-radius: 16px; border: 1px solid #fde68a; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); overflow: hidden;">
        <div class="panel-header" style="padding: 1.25rem; border-bottom: 1px solid #fde68a; display: flex; align-items: center; gap: 0.5rem; background-color: #fef3c7;">
          <svg style="width: 20px; height: 20px; color: #b45309;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
            <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
          </svg>
          <h3 style="margin: 0; font-size: 1.1rem; font-weight: 700; color: #b45309;">
            {{ $t('teacherDetail.pending_notifications') }} ({{ pendingNotifications.length }})
          </h3>
        </div>
        <div class="panel-body" style="padding: 1.25rem; display: flex; flex-direction: column; gap: 0.75rem;">
          <div v-for="notif in pendingNotifications" :key="notif.id" style="background: white; border: 1px solid #fef3c7; border-radius: 8px; padding: 1rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 2px 0 rgba(0,0,0,0.05); text-align: left;">
            <div>
              <div style="font-weight: 600; color: #1e293b; margin-bottom: 0.25rem;">{{ getLocalizedTitle(notif) }}</div>
              <div style="font-size: 0.875rem; color: #64748b;">{{ notif.message }}</div>
            </div>
            <div style="font-size: 0.8rem; color: #94a3b8; font-family: monospace;">{{ formatDate(notif.created_at) }}</div>
          </div>
        </div>
      </div>

      <!-- Groups Taught Table -->
      <div class="detail-card glass-panel" style="background: white; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); overflow: hidden;">
        <div class="panel-header" style="padding: 1.5rem; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center;">
          <h2 class="panel-title" style="margin: 0; font-size: 1.25rem; font-weight: 700; color: #0f172a;">{{ $t('teacherDetail.groups_taught') }}</h2>
          <div class="badge-count" style="padding: 0.25rem 0.75rem; border-radius: 9999px; background-color: #f1f5f9; color: #475569; font-size: 0.75rem; font-weight: 600;">
            {{ teacherGroups.length }} {{ $t('nav.groups').toLowerCase() }}
          </div>
        </div>
        <div class="panel-body" style="padding: 1.5rem;">
          <div class="table-wrapper" style="overflow-x: auto;">
            <table class="data-table" style="width: 100%; border-collapse: collapse; text-align: left;">
              <thead>
                <tr style="border-bottom: 2px solid #f1f5f9;">
                  <th style="padding: 1rem; color: #64748b; font-weight: 600; font-size: 0.85rem;">ID</th>
                  <th style="padding: 1rem; color: #64748b; font-weight: 600; font-size: 0.85rem;">{{ $t('groups.form_name') }}</th>
                  <th style="padding: 1rem; color: #64748b; font-weight: 600; font-size: 0.85rem;">{{ $t('groupDetail.course') }}</th>
                  <th style="padding: 1rem; color: #64748b; font-weight: 600; font-size: 0.85rem;">{{ $t('groupDetail.branch') }} / {{ $t('groupDetail.room') }}</th>
                  <th style="padding: 1rem; color: #64748b; font-weight: 600; font-size: 0.85rem;">{{ $t('timetable.title') }}</th>
                  <th style="padding: 1rem; color: #64748b; font-weight: 600; font-size: 0.85rem;">{{ $t('groupDetail.price') }}</th>
                  <th style="padding: 1rem; color: #64748b; font-weight: 600; font-size: 0.85rem;">{{ $t('groups.col_students') }}</th>
                  <th style="padding: 1rem; color: #64748b; font-weight: 600; font-size: 0.85rem; text-align: right;">{{ $t('common.status') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="group in teacherGroups" :key="group.id" class="table-row" style="border-bottom: 1px solid #f1f5f9; transition: background-color 0.2s;">
                  <td style="padding: 1rem;" class="font-mono text-muted">#{{ group.id }}</td>
                  <td style="padding: 1rem; font-weight: 600;">
                    <router-link :to="`/groups/${group.id}`" class="group-link" style="color: #6366f1; text-decoration: none; font-weight: 600;">
                      {{ group.name }} &rarr;
                    </router-link>
                  </td>
                  <td style="padding: 1rem;">{{ getCourseName(group.course) }}</td>
                  <td style="padding: 1rem;">{{ getBranchName(group.branch) }} ({{ getRoomName(group.room) }})</td>
                  <td style="padding: 1rem;">
                    <div style="font-weight: 500; color: #334155;">{{ $t('groups.' + (group.group_days_at || 'Mon-Wed-Fri')) }}</div>
                    <div style="font-size: 0.8rem; color: #64748b; font-family: monospace;">{{ formatTime(group.starts_at) }} ({{ group.duration }}m)</div>
                  </td>
                  <td style="padding: 1rem; font-weight: 500; font-family: monospace;">{{ formatPrice(group.price) }} UZS</td>
                  <td style="padding: 1rem;">
                    <span style="font-weight: 600; color: #1e293b;">{{ group.students ? group.students.length : 0 }}</span> {{ $t('groups.col_students').toLowerCase() }}
                  </td>
                  <td style="padding: 1rem; text-align: right;">
                    <span :class="['status-badge', group.status === 'ongoing' ? 'active' : 'dropped']" style="padding: 0.2rem 0.6rem; border-radius: 9999px; font-size: 0.7rem; font-weight: 600;">
                      {{ $t('groups.status_' + (group.status || 'ongoing')) }}
                    </span>
                  </td>
                </tr>
                <tr v-if="!teacherGroups.length">
                  <td colspan="8" style="padding: 3rem; text-align: center; color: #64748b;">{{ $t('teacherDetail.no_groups') }}</td>
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

export default {
  name: 'TeacherDetail',
  data() {
    return {
      teacher: null,
      groups: [],
      courses: [],
      branches: [],
      rooms: [],
      payments: [],
      notifications: [],
      loading: false,
      error: null
    }
  },
  computed: {
    teacherGroups() {
      if (!this.teacher) return []
      return this.groups.filter(g => g.teacher === this.teacher.id)
    },
    currentMonthIncome() {
      if (!this.payments || !this.teacher) return 0
      const now = new Date()
      const currentYear = now.getFullYear()
      const currentMonth = now.getMonth()
      return this.payments
        .filter(p => {
          if (p.status !== 'accepted') return false
          const pDate = new Date(p.payment_date)
          return pDate.getFullYear() === currentYear && pDate.getMonth() === currentMonth
        })
        .reduce((sum, p) => sum + parseFloat(p.amount || 0), 0)
    },
    pendingNotifications() {
      if (!this.notifications) return []
      return this.notifications.filter(
        n => n.notification_type === 'payment_pending' && !this.isPayoutAccepted(n)
      )
    }
  },
  mounted() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      this.loading = true
      this.error = null
      const teacherId = this.$route.params.id

      try {
        const [teacherRes, groupsRes, coursesRes, branchesRes, roomsRes, paymentsRes, notificationsRes] = await Promise.all([
          axios.get(`/api/users/${teacherId}/`),
          axios.get('/api/groups/'),
          axios.get('/api/courses/'),
          axios.get('/api/branches/'),
          axios.get('/api/rooms/'),
          axios.get(`/api/users/${teacherId}/payments/`),
          axios.get(`/api/notifications/?recipient=${teacherId}`)
        ])

        this.teacher = teacherRes.data
        this.groups = groupsRes.data
        this.courses = coursesRes.data
        this.branches = branchesRes.data
        this.rooms = roomsRes.data
        this.payments = paymentsRes.data
        this.notifications = notificationsRes.data
      } catch (err) {
        console.error('Error loading teacher details:', err)
        this.error = this.$t('stats.api_error')
      } finally {
        this.loading = false
      }
    },
    getInitials(firstName, lastName) {
      const f = firstName ? firstName.charAt(0).toUpperCase() : ''
      const l = lastName ? lastName.charAt(0).toUpperCase() : ''
      return f + l || 'T'
    },
    getBranchName(branchId) {
      if (!branchId) return '-'
      const branch = this.branches.find(b => b.id === branchId)
      return branch ? branch.name : `Branch #${branchId}`
    },
    getRoomName(roomId) {
      if (!roomId) return '-'
      const room = this.rooms.find(r => r.id === roomId)
      return room ? room.name : `Room #${roomId}`
    },
    getCourseName(courseId) {
      if (!courseId) return '-'
      const course = this.courses.find(c => c.id === courseId)
      return course ? course.name : `Course #${courseId}`
    },
    formatTime(timeStr) {
      if (!timeStr) return '-'
      const parts = timeStr.split(':')
      return `${parts[0]}:${parts[1]}`
    },
    formatPrice(price) {
      if (!price) return '0'
      const num = parseFloat(price)
      return num.toLocaleString('fr-FR') // Space separated thousands
    },
    isPayoutAccepted(notif) {
      return notif.title && notif.title.includes('Payout Confirmed')
    },
    getLocalizedTitle(notif) {
      const match = notif.title.match(/#(\d+)/)
      const suffix = match ? ` #${match[1]}` : ''
      if (notif.notification_type === 'absence') {
        return this.$t('notifications.absence_title') + suffix
      } else if (notif.notification_type === 'payment_pending') {
        if (this.isPayoutAccepted(notif)) {
          return this.$t('notifications.payment_accepted_title') + suffix
        }
        return this.$t('notifications.payment_pending_title') + suffix
      } else if (notif.notification_type === 'payment_accepted') {
        return this.$t('notifications.payment_accepted_title') + suffix
      }
      return notif.title
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return date.toLocaleString(this.$i18n.locale === 'ru' ? 'ru-RU' : 'uz-UZ', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  }
}
</script>

<style scoped>
@import '../assets/views.css';

.group-link:hover {
  text-decoration: underline !important;
  color: #4f46e5 !important;
}

.table-row:hover {
  background-color: #f8fafc;
}
</style>
