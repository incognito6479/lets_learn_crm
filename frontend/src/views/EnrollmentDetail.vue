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

    <div v-if="loading" class="loading-state-full">
      <div class="spinner"></div>
      <span>{{ $t('common.loading') }}</span>
    </div>

    <div v-if="!loading && enrollment" class="detail-grid-layout">
      <!-- Left Column: Student & Group details -->
      <div class="main-info-col">
        <!-- Student Info Card -->
        <div class="detail-card glass-panel">
          <div class="panel-header" style="display: flex; align-items: center; gap: 1rem;">
            <button @click="openEditStudentModal" class="btn btn-secondary btn-sm" style="padding: 0.35rem 0.75rem; font-size: 0.8rem; display: inline-flex; align-items: center; gap: 0.25rem;">
              <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width: 14px; height: 14px;">
                <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 113 3L12 15l-4 1 1-4 9.5-9.5z"></path>
              </svg>
              {{ $t('common.edit') }}
            </button>
            <h2 class="panel-title">{{ $t('enrollmentDetail.profile_card') }}</h2>
          </div>
          <div class="panel-body">
            <div class="profile-header-block">
              <div class="avatar-large">{{ getInitials(student.full_name) }}</div>
              <div>
                <h3 class="profile-name">{{ student.full_name }}</h3>
                <span :class="['status-badge', enrollment.status || 'enrolled']">
                  {{ $t('groupDetail.status_' + (enrollment.status || 'enrolled')) }}
                </span>
              </div>
            </div>
            
            <div class="info-fields-grid">
              <div class="info-field">
                <span class="field-label">{{ $t('groupDetail.student_phone1') }}</span>
                <span class="field-value">{{ student.phone1 || '-' }}</span>
              </div>
              <div class="info-field" v-if="student.phone2">
                <span class="field-label">{{ $t('groupDetail.student_phone2') }}</span>
                <span class="field-value">{{ student.phone2 }}</span>
              </div>
              <div class="info-field">
                <span class="field-label">{{ $t('enrollmentDetail.enroll_date') }}</span>
                <span class="field-value">{{ formatDate(enrollment.date) }}</span>
              </div>
              <div class="info-field" style="grid-column: span 2;" v-if="student.description">
                <span class="field-label">{{ $t('common.description') }}</span>
                <span class="field-value description-text">{{ student.description }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Group & Class Details Card -->
        <div class="detail-card glass-panel" style="margin-top: 1.5rem;">
          <div class="panel-header">
            <h2 class="panel-title">{{ $t('groupDetail.details_title') }}</h2>
          </div>
          <div class="panel-body">
            <div class="info-fields-grid">
              <div class="info-field">
                <span class="field-label">{{ $t('stats.group') }}</span>
                <span class="field-value highlight-text" @click="$router.push(`/groups/${group.id}`)" style="cursor: pointer;">
                  {{ group.name }} &rarr;
                </span>
              </div>
              <div class="info-field">
                <span class="field-label">{{ $t('groupDetail.course') }}</span>
                <span class="field-value">{{ getCourseName(group.course) }}</span>
              </div>
              <div class="info-field">
                <span class="field-label">{{ $t('groupDetail.teacher') }}</span>
                <span class="field-value">{{ getTeacherName(group.teacher) }}</span>
              </div>
              <div class="info-field">
                <span class="field-label">{{ $t('groupDetail.branch') }} &amp; {{ $t('groupDetail.room') }}</span>
                <span class="field-value">{{ getBranchName(group.branch) }} ({{ getRoomName(group.room) }})</span>
              </div>
              <div class="info-field">
                <span class="field-label">{{ $t('groupDetail.time') }}</span>
                <span class="field-value">{{ formatTime(group.starts_at) }}</span>
              </div>
              <div class="info-field">
                <span class="field-label">{{ $t('groupDetail.days') }}</span>
                <span class="field-value">{{ $t('groups.' + (group.group_days_at || 'Mon-Wed-Fri')) }}</span>
              </div>
              <div class="info-field">
                <span class="field-label">{{ $t('groupDetail.duration') }}</span>
                <span class="field-value">{{ $t('groupDetail.duration_value', { val: group.duration }) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Student's Enrolled Groups & Debt Status Card -->
        <div class="detail-card glass-panel" style="margin-top: 1.5rem;">
          <div class="panel-header">
            <h2 class="panel-title">{{ $t('enrollmentDetail.all_groups') }}</h2>
          </div>
          <div class="panel-body">
            <div class="table-wrapper" style="box-shadow: none; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>{{ $t('stats.group') }}</th>
                    <th>{{ $t('groupDetail.branch') }}</th>
                    <th>{{ $t('groupDetail.enrollment_status') }}</th>
                    <th>{{ $t('groupDetail.payment_status_label') }}</th>
                    <th style="text-align: right;">{{ $t('common.actions') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in studentEnrollments" :key="item.id" :class="['table-row', { 'current-group-row': item.id === enrollment.id }]">
                    <td class="font-semibold">
                      {{ item.groupName }}
                      <span v-if="item.id === enrollment.id" class="current-label-badge">{{ $t('enrollmentDetail.current_badge') }}</span>
                    </td>
                    <td>{{ item.branchName }}</td>
                    <td>
                      <span :class="['status-badge', item.status || 'enrolled']">
                        {{ $t('groupDetail.status_' + (item.status || 'enrolled')) }}
                      </span>
                    </td>
                    <td>
                      <div style="display: flex; flex-direction: column; align-items: flex-start; gap: 0.25rem;">
                        <span :class="['status-badge', item.payment_status || 'debt']">
                          {{ $t('groupDetail.status_' + (item.payment_status || 'debt')) }}
                        </span>
                        <span v-if="(item.payment_status || 'debt') === 'debt'" class="table-debt-amount">
                          {{ formatPrice(item.debt_amount) }} UZS
                        </span>
                      </div>
                    </td>
                    <td style="text-align: right;">
                      <button @click="$router.push(`/enrollments/${item.id}`)" class="btn-icon" :title="$t('debts.action_view')" :disabled="item.id === enrollment.id">
                        <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                          <circle cx="12" cy="12" r="3"></circle>
                        </svg>
                      </button>
                    </td>
                  </tr>
                  <tr v-if="!studentEnrollments.length">
                    <td colspan="5" class="empty-state">{{ $t('enrollmentDetail.no_enrollments') }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Payments & Outstanding Debt -->
      <div class="payment-col">
        <!-- Balance Overview Card -->
        <div class="detail-card glass-panel balance-summary-card">
          <div class="panel-header">
            <h2 class="panel-title">{{ $t('enrollmentDetail.title') }}</h2>
          </div>
          <div class="panel-body">
            <div class="balance-display-block">
              <span class="balance-label">{{ $t('enrollmentDetail.outstanding_balance') }}</span>
              <h1 :class="['balance-amount', enrollment.payment_status === 'debt' ? 'text-red' : 'text-green']">
                {{ formatPrice(enrollment.debt_amount) }} UZS
              </h1>
              <div class="badge-status-row" style="display: flex; flex-direction: column; align-items: center; gap: 0.75rem;">
                <span :class="['status-badge', enrollment.payment_status || 'debt']">
                  {{ $t('groupDetail.payment_status_label') }}: {{ $t('groupDetail.status_' + (enrollment.payment_status || 'debt')) }}
                </span>
                <button
                  v-if="(enrollment.payment_status || 'debt') === 'debt' && enrollment.status !== 'dropped'"
                  @click="openPaymentModal"
                  class="btn btn-primary"
                  style="font-size: 0.85rem; padding: 0.45rem 1.25rem; font-weight: 600; width: 100%; justify-content: center;"
                >
                  {{ $t('debts.action_pay') }}
                </button>
              </div>
            </div>

            <div class="group-pricing-info">
              <div class="price-row">
                <span>{{ $t('groups.col_price') }}:</span>
                <strong>{{ formatPrice(group.price) }} UZS</strong>
              </div>
              <div class="price-row">
                <span>{{ $t('enrollmentDetail.paid') }}:</span>
                <strong>{{ formatPrice(totalPaymentsForGroup) }} UZS</strong>
              </div>
            </div>
          </div>
        </div>

        <!-- Payments Log Card -->
        <div class="detail-card glass-panel" style="margin-top: 1.5rem;">
          <div class="panel-header">
            <h2 class="panel-title">{{ $t('enrollmentDetail.payments_history') }}</h2>
          </div>
          <div class="panel-body">
            <div class="timeline-wrapper">
              <div v-for="payment in paymentsForGroup" :key="payment.id" class="timeline-item">
                <div class="timeline-marker"></div>
                <div class="timeline-content">
                  <div class="timeline-header">
                    <span class="timeline-amount" :style="!payment.is_active || payment.status === 'canceled' ? 'text-decoration: line-through; color: #94a3b8;' : ''">{{ formatPrice(payment.amount) }} UZS</span>
                    <div style="display: flex; gap: 0.5rem; align-items: center;">
                      <span :class="['status-badge', payment.payment_method || 'cash']">
                        {{ $t('groupDetail.' + (payment.payment_method || 'cash')) }}
                      </span>
                      <span :class="['status-badge', payment.status || 'accepted']">
                        {{ $t('payments.status_' + (payment.status || 'accepted')) }}
                      </span>
                    </div>
                  </div>
                  <span class="timeline-date">{{ formatDateTime(payment.payment_date) }}</span>
                  <p class="timeline-desc">{{ payment.description || '-' }}</p>
                </div>
              </div>
              <div v-if="!paymentsForGroup.length" class="empty-state" style="padding: 1.5rem 0;">
                {{ $t('enrollmentDetail.no_payments') }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Record Payment Modal -->
    <div v-if="showPaymentModal" class="modal-backdrop" @click.self="closePaymentModal">
      <div class="modal-content" style="max-width: 480px;">
        <div class="modal-header">
          <h2 class="modal-title">{{ $t('groupDetail.record_payment_title') }}</h2>
          <button @click="closePaymentModal" class="modal-close">
            <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <form @submit.prevent="confirmPayment">
          <div class="modal-body">
            <p class="modal-instructions" style="margin-bottom: 1.25rem; text-align: left;">
              <span v-html="$t('groupDetail.confirm_payment_instructions', { student: '<strong>' + student.full_name + '</strong>', group: '<strong>' + group.name + '</strong>' })"></span>
            </p>

            <div class="form-group" style="margin-bottom: 1.25rem; display: flex; flex-direction: column; gap: 0.5rem; text-align: left;">
              <label for="paymentAmount" class="form-label" style="font-size: 0.875rem; font-weight: 500; color: #cbd5e1;">{{ $t('groupDetail.payment_amount') }}</label>
              <input
                type="text"
                inputmode="numeric"
                id="paymentAmount"
                :value="paymentForm.amount"
                @input="formatPaymentInputPrice"
                required
                class="form-input"
                style="width: 100%; box-sizing: border-box;"
              />
            </div>

            <div class="form-group" style="margin-bottom: 1.25rem; display: flex; flex-direction: column; gap: 0.5rem; text-align: left;">
              <label for="paymentMethod" class="form-label" style="font-size: 0.875rem; font-weight: 500; color: #cbd5e1;">{{ $t('groupDetail.payment_method') }}</label>
              <select id="paymentMethod" v-model="paymentForm.payment_method" required class="form-input" style="width: 100%; box-sizing: border-box;">
                <option value="cash">{{ $t('groupDetail.cash') }}</option>
                <option value="card">{{ $t('groupDetail.card') }}</option>
              </select>
            </div>

            <div class="form-group" style="display: flex; flex-direction: column; gap: 0.5rem; text-align: left;">
              <label for="paymentDescription" class="form-label" style="font-size: 0.875rem; font-weight: 500; color: #cbd5e1;">{{ $t('groupDetail.payment_desc') }}</label>
              <textarea
                id="paymentDescription"
                v-model="paymentForm.description"
                class="form-input"
                rows="3"
                :placeholder="$t('groupDetail.payment_desc_placeholder')"
                style="width: 100%; box-sizing: border-box; resize: vertical;"
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" @click="closePaymentModal" class="btn btn-secondary">{{ $t('common.cancel') }}</button>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="submittingPayment || !paymentForm.amount"
            >
              {{ submittingPayment ? $t('groupDetail.processing') : $t('groupDetail.confirm_payment_btn') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Edit Student Modal -->
    <div v-if="showEditStudentModal" class="modal-backdrop" @click.self="closeEditStudentModal">
      <div class="modal-content" style="max-width: 480px;">
        <div class="modal-header">
          <h2 class="modal-title">{{ $t('students.modal_edit') }}</h2>
          <button @click="closeEditStudentModal" class="modal-close">
            <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <form @submit.prevent="updateStudent">
          <div class="modal-body">
            <!-- Full Name -->
            <div class="form-group" style="margin-bottom: 1.25rem; display: flex; flex-direction: column; gap: 0.5rem; text-align: left;">
              <label for="studentName" class="form-label" style="font-size: 0.875rem; font-weight: 500; color: #cbd5e1;">{{ $t('groupDetail.student_fullname') }}</label>
              <input
                type="text"
                id="studentName"
                v-model="studentForm.full_name"
                required
                class="form-input"
                style="width: 100%; box-sizing: border-box;"
              />
            </div>

            <!-- Phone 1 -->
            <div class="form-group" style="margin-bottom: 1.25rem; display: flex; flex-direction: column; gap: 0.5rem; text-align: left;">
              <label for="studentPhone1" class="form-label" style="font-size: 0.875rem; font-weight: 500; color: #cbd5e1;">{{ $t('groupDetail.student_phone1') }}</label>
              <div class="phone-input-wrapper">
                <span class="phone-prefix">+998</span>
                <input
                  type="text"
                  inputmode="numeric"
                  maxlength="12"
                  id="studentPhone1"
                  :value="studentForm.phone1"
                  @input="handleStudentPhoneInput($event, 'phone1')"
                  @keypress="onlyNumber"
                  required
                  placeholder="90 123 45 67"
                  class="phone-editable-input"
                  style="width: 100%; box-sizing: border-box;"
                />
              </div>
            </div>

            <!-- Phone 2 -->
            <div class="form-group" style="display: flex; flex-direction: column; gap: 0.5rem; text-align: left;">
              <label for="studentPhone2" class="form-label" style="font-size: 0.875rem; font-weight: 500; color: #cbd5e1;">{{ $t('groupDetail.student_phone2') }}</label>
              <div class="phone-input-wrapper">
                <span class="phone-prefix">+998</span>
                <input
                  type="text"
                  inputmode="numeric"
                  maxlength="12"
                  id="studentPhone2"
                  :value="studentForm.phone2"
                  @input="handleStudentPhoneInput($event, 'phone2')"
                  @keypress="onlyNumber"
                  placeholder="90 123 45 67"
                  class="phone-editable-input"
                  style="width: 100%; box-sizing: border-box;"
                />
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" @click="closeEditStudentModal" class="btn btn-secondary">{{ $t('common.cancel') }}</button>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="submittingStudentUpdate || !studentForm.full_name || !studentForm.phone1"
            >
              {{ submittingStudentUpdate ? $t('groupDetail.processing') : $t('common.save') }}
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
  name: 'EnrollmentDetail',
  data() {
    return {
      enrollment: null,
      student: {},
      group: {},
      payments: [],
      courses: [],
      teachers: [],
      rooms: [],
      branches: [],
      allEnrollments: [],
      loading: false,
      error: null,
      showPaymentModal: false,
      submittingPayment: false,
      paymentForm: {
        amount: '',
        payment_method: 'cash',
        description: ''
      },
      showEditStudentModal: false,
      submittingStudentUpdate: false,
      studentForm: {
        id: null,
        full_name: '',
        phone1: '',
        phone2: ''
      }
    }
  },
  computed: {
    paymentsForGroup() {
      if (!this.payments.length || !this.enrollment) return []
      return this.payments.filter(
        p => p.student === this.enrollment.student && p.group === this.enrollment.group
      ).sort((a, b) => new Date(b.payment_date) - new Date(a.payment_date))
    },
    totalPaymentsForGroup() {
      return this.paymentsForGroup
        .filter(p => p.is_active && p.status === 'accepted')
        .reduce((sum, p) => sum + parseFloat(p.amount || 0), 0)
    },
    studentEnrollments() {
      if (!this.allEnrollments.length || !this.enrollment) return []
      // Find all enrollments belonging to the same student (including current)
      return this.allEnrollments
        .filter(e => e.student === this.enrollment.student)
        .map(e => {
          const grp = e.groupInfo || {}
          const grpName = grp.name || `Group #${e.group}`
          
          let branchName = 'Branch'
          if (this.branches.length && grp.branch) {
            const b = this.branches.find(br => br.id === grp.branch)
            if (b) branchName = b.name
          }

          return {
            ...e,
            groupName: grpName,
            branchName: branchName
          }
        })
    }
  },
  watch: {
    // Re-fetch data if route id parameter changes (e.g. user navigates between other groups)
    '$route.params.id': {
      handler: 'fetchData',
      immediate: true
    }
  },
  methods: {
    async fetchData() {
      const id = this.$route.params.id
      this.loading = true
      this.error = null
      try {
        const [enrollmentRes, paymentsRes, coursesRes, usersRes, roomsRes, branchesRes, allEnrollmentsRes] = await Promise.all([
          axios.get(`/api/enrollments/${id}/`),
          axios.get('/api/payments/'),
          axios.get('/api/courses/'),
          axios.get('/api/users/'),
          axios.get('/api/rooms/'),
          axios.get('/api/branches/'),
          axios.get('/api/enrollments/')
        ])

        this.enrollment = enrollmentRes.data
        this.payments = paymentsRes.data
        this.courses = coursesRes.data
        this.teachers = usersRes.data.filter(u => u.role === 'teacher')
        this.rooms = roomsRes.data
        this.branches = branchesRes.data
        
        // Populate groups list locally for calculations
        const groupsRes = await axios.get('/api/groups/')
        this.allEnrollments = allEnrollmentsRes.data.map(e => {
          const g = groupsRes.data.find(grp => grp.id === e.group)
          return {
            ...e,
            groupInfo: g
          }
        })
        
        // Fetch student detail and current group detail using foreign keys
        const [studentRes, groupRes] = await Promise.all([
          axios.get(`/api/students/${this.enrollment.student}/`),
          axios.get(`/api/groups/${this.enrollment.group}/`)
        ])
        
        this.student = studentRes.data
        this.group = groupRes.data
        this.loading = false
      } catch (err) {
        console.error('Error fetching enrollment details:', err)
        this.error = this.$t('stats.api_error')
        this.loading = false
      }
    },
    getInitials(name) {
      if (!name) return 'S'
      return name.split(' ').map(p => p.charAt(0)).join('').toUpperCase().slice(0, 2)
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
    formatPrice(price) {
      if (!price && price !== 0) return '0'
      const val = Math.round(parseFloat(price))
      return val.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
    },
    formatTime(timeStr) {
      if (!timeStr) return '-'
      const parts = timeStr.split(':')
      if (parts.length >= 2) return `${parts[0]}:${parts[1]}`
      return timeStr
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      try {
        const date = new Date(dateStr)
        const locale = this.$i18n.locale === 'uz' ? 'uz-UZ' : 'ru-RU'
        return date.toLocaleDateString(locale, { month: 'short', day: 'numeric', year: 'numeric' })
      } catch (e) {
        return dateStr
      }
    },
    formatDateTime(dateStr) {
      if (!dateStr) return '-'
      try {
        const date = new Date(dateStr)
        const locale = this.$i18n.locale === 'uz' ? 'uz-UZ' : 'ru-RU'
        return date.toLocaleDateString(locale, {
          month: 'short',
          day: 'numeric',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        })
      } catch (e) {
        return dateStr
      }
    },
    formatMethod(method) {
      if (!method) return 'Cash'
      return method.charAt(0).toUpperCase() + method.slice(1)
    },
    openPaymentModal() {
      // Auto-populate the amount input with the group's price or outstanding debt
      const defaultAmount = this.formatPrice(this.enrollment.debt_amount || this.group.price)
      this.paymentForm = {
        amount: defaultAmount,
        payment_method: 'cash',
        description: ''
      }
      this.showPaymentModal = true
    },
    closePaymentModal() {
      this.showPaymentModal = false
    },
    formatPaymentInputPrice(event) {
      const input = event.target
      const originalValue = input.value
      const selectionStart = input.selectionStart
      
      const numericVal = originalValue.replace(/[^\d]/g, '')
      if (!numericVal) {
        this.paymentForm.amount = ''
        return
      }
      
      const formatted = this.formatPrice(numericVal)
      this.paymentForm.amount = formatted
      
      this.$nextTick(() => {
        const delta = formatted.length - originalValue.length
        const newCursorPos = selectionStart + delta
        input.setSelectionRange(newCursorPos, newCursorPos)
      })
    },
    async confirmPayment() {
      this.submittingPayment = true
      try {
        const rawAmount = String(this.paymentForm.amount).replace(/\s/g, '')
        const amountVal = parseFloat(rawAmount || 0)
        
        await axios.post('/api/payments/', {
          group: this.group.id,
          student: this.student.id,
          amount: amountVal,
          payment_method: this.paymentForm.payment_method,
          description: this.paymentForm.description || `Payment for group: ${this.group.name}`
        })
        
        this.closePaymentModal()
        await this.fetchData()
      } catch (err) {
        console.error('Error confirming payment:', err)
        alert(this.$t('groupDetail.error_payment'))
      } finally {
        this.submittingPayment = false
      }
    },
    openEditStudentModal() {
      this.studentForm = {
        id: this.student.id,
        full_name: this.student.full_name,
        phone1: this.parsePhoneForInput(this.student.phone1),
        phone2: this.parsePhoneForInput(this.student.phone2 || '')
      }
      this.showEditStudentModal = true
    },
    closeEditStudentModal() {
      this.showEditStudentModal = false
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
    handleStudentPhoneInput(e, field) {
      const input = e.target
      const rawValue = input.value
      
      const selectionStart = input.selectionStart
      const digitsBefore = rawValue.substring(0, selectionStart).replace(/\D/g, '').length
      
      const formatted = this.formatPhoneInput(rawValue)
      this.studentForm[field] = formatted
      
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
    },
    async updateStudent() {
      this.submittingStudentUpdate = true
      
      const rawPhone1 = this.studentForm.phone1.replace(/\D/g, '')
      if (rawPhone1.length !== 9) {
        alert(this.$t('students.phone_length_error'))
        this.submittingStudentUpdate = false
        return
      }
      
      let rawPhone2 = null
      if (this.studentForm.phone2) {
        const parsed2 = this.studentForm.phone2.replace(/\D/g, '')
        if (parsed2) {
          if (parsed2.length !== 9) {
            alert(this.$t('students.phone_length_error'))
            this.submittingStudentUpdate = false
            return
          }
          rawPhone2 = '+998' + parsed2
        }
      }
      
      const payload = {
        full_name: this.studentForm.full_name,
        phone1: '+998' + rawPhone1,
        phone2: rawPhone2,
        description: this.student.description || ''
      }
      
      try {
        await axios.put(`/api/students/${this.student.id}/`, payload)
        this.closeEditStudentModal()
        await this.fetchData()
      } catch (err) {
        console.error('Error updating student:', err)
        alert(this.$t('common.error_save'))
      } finally {
        this.submittingStudentUpdate = false
      }
    }
  }
}
</script>

<style scoped>
@import '../assets/views.css';

.back-btn {
  font-size: 0.85rem;
  padding: 0.45rem 0.85rem;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.detail-grid-layout {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 1.75rem;
  text-align: left;
}

@media (max-width: 1024px) {
  .detail-grid-layout {
    grid-template-columns: 1fr;
  }
}

.glass-panel {
  background: white;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.01), 0 2px 4px -2px rgba(0, 0, 0, 0.01);
  overflow: hidden;
}

.panel-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #f1f5f9;
}

.panel-title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: #0f172a;
}

.panel-body {
  padding: 1.5rem;
}

/* Profile Header Section */
.profile-header-block {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  margin-bottom: 1.75rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px dashed #e2e8f0;
}

.avatar-large {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #6366f1, #3b82f6);
  color: white;
  font-size: 1.5rem;
  font-weight: 700;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
}

.profile-name {
  margin: 0 0 0.4rem 0;
  font-size: 1.4rem;
  font-weight: 700;
  color: #0f172a;
}

/* Info Grid Layout */
.info-fields-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem 1.5rem;
}

.info-field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.field-label {
  font-size: 0.775rem;
  font-weight: 600;
  text-transform: uppercase;
  color: #64748b;
  letter-spacing: 0.5px;
}

.field-value {
  font-size: 0.95rem;
  font-weight: 500;
  color: #1e293b;
}

.highlight-text {
  color: #4f46e5;
  font-weight: 600;
}

.highlight-text:hover {
  text-decoration: underline;
}

.description-text {
  font-size: 0.9rem;
  color: #4b5563;
  line-height: 1.5;
  background-color: #f8fafc;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  border-left: 3px solid #cbd5e1;
}

/* Balance Display */
.balance-summary-card {
  background: linear-gradient(to bottom, #ffffff, #fafafa);
}

.balance-display-block {
  text-align: center;
  padding: 1.5rem 1rem;
  background-color: #f8fafc;
  border-radius: 12px;
  border: 1px solid #f1f5f9;
  margin-bottom: 1.5rem;
}

.balance-label {
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  color: #64748b;
  letter-spacing: 0.5px;
}

.balance-amount {
  font-size: 2rem;
  font-weight: 700;
  margin: 0.5rem 0;
  line-height: 1;
}

.badge-status-row {
  margin-top: 0.75rem;
  display: inline-block;
}

.text-red {
  color: #dc2626 !important;
}

.text-green {
  color: #16a34a !important;
}

.group-pricing-info {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0.5rem 0.25rem;
}

.price-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  color: #475569;
}

.price-row strong {
  color: #1e293b;
}

/* Timeline/Payments logs */
.timeline-wrapper {
  display: flex;
  flex-direction: column;
  position: relative;
  padding-left: 1.25rem;
}

.timeline-wrapper::before {
  content: '';
  position: absolute;
  left: 3.5px;
  top: 8px;
  bottom: 8px;
  width: 2px;
  background-color: #e2e8f0;
}

.timeline-item {
  position: relative;
  padding-bottom: 1.5rem;
}

.timeline-item:last-child {
  padding-bottom: 0;
}

.timeline-marker {
  position: absolute;
  left: -1.25rem;
  top: 6px;
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background-color: #6366f1;
  border: 2px solid white;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
}

.timeline-content {
  background-color: #f8fafc;
  padding: 0.85rem 1rem;
  border-radius: 10px;
  border: 1px solid #f1f5f9;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
}

.timeline-amount {
  font-weight: 700;
  color: #1e293b;
  font-size: 0.95rem;
}

.timeline-date {
  font-size: 0.75rem;
  color: #94a3b8;
  display: block;
  margin-bottom: 0.5rem;
}

.timeline-desc {
  margin: 0;
  font-size: 0.825rem;
  color: #64748b;
  line-height: 1.4;
}

.status-badge.cash {
  background-color: #e0f2fe;
  color: #0369a1;
}

.status-badge.card {
  background-color: #f3e8ff;
  color: #6b21a8;
}

.status-badge.accepted {
  background-color: #dcfce7;
  color: #15803d;
}

.status-badge.canceled {
  background-color: #fee2e2;
  color: #991b1b;
}

.loading-state-full {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 5rem 0;
  color: #64748b;
  gap: 1rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(99, 102, 241, 0.1);
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.current-group-row {
  background-color: rgba(99, 102, 241, 0.04) !important;
}

.current-label-badge {
  font-size: 0.7rem;
  background-color: #6366f1;
  color: white;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  margin-left: 0.5rem;
  font-weight: 500;
  display: inline-block;
  vertical-align: middle;
}

.table-debt-amount {
  color: #dc2626;
  font-weight: 600;
  font-size: 0.775rem;
}
</style>
