<template>
  <div class="view-container">
    <div class="view-header">
      <div>
        <h1 class="view-title">{{ $t('debts.title') }}</h1>
        <p class="view-subtitle">{{ $t('debts.sub') }}</p>
      </div>
      <div style="display: flex; gap: 1rem; align-items: center;" v-if="filteredDebts.length">
        <div class="badge-count">{{ filteredDebts.length }} {{ $t('debts.unique_count') }}</div>
        <div class="badge-count text-danger-badge">{{ $t('debts.total_debts') }}: {{ formatPrice(totalFilteredDebt) }} UZS</div>
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
          :placeholder="$t('payments.search_student')"
          class="form-input"
        />
      </div>
      
      <div style="width: 200px;">
        <select v-model="selectedBranch" class="form-input" @change="selectedGroup = ''">
          <option value="">{{ $t('timetable.filter_branch') }}</option>
          <option v-for="branch in branches" :key="branch.id" :value="branch.id">
            {{ branch.name }}
          </option>
        </select>
      </div>

      <div style="min-width: 250px;">
        <select v-model="selectedGroup" class="form-input">
          <option value="">{{ $t('payments.filter_group') }}</option>
          <option v-for="group in filteredGroupsForSelect" :key="group.id" :value="group.id">
            {{ group.name }} ({{ formatTime(group.starts_at) }}, {{ $t('groups.' + (group.group_days_at || 'Mon-Wed-Fri')) }})
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
              <th>{{ $t('groupDetail.student_fullname') }}</th>
              <th>{{ $t('stats.group') }}</th>
              <th>{{ $t('groups.col_branch') }}</th>
              <th>{{ $t('common.phone') }}</th>
              <th>{{ $t('groupDetail.enrollment_date') }}</th>
              <th>{{ $t('debts.col_debt') }}</th>
              <th style="text-align: right;">{{ $t('common.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="debt in filteredDebts" :key="debt.enrollmentId" class="table-row clickable-row" @click="navigateToEnrollment(debt.enrollmentId)">
              <td class="font-mono text-muted">#{{ debt.enrollmentId }}</td>
              <td class="font-semibold">{{ debt.studentName }}</td>
              <td>{{ debt.groupName }}</td>
              <td>{{ debt.branchName }}</td>
              <td>{{ debt.studentPhone }}</td>
              <td>{{ formatDate(debt.date) }}</td>
              <td class="font-mono font-bold text-red">{{ formatPrice(debt.debt_amount) }} UZS</td>
              <td class="actions-cell">
                <button @click.stop="openPaymentModal(debt)" class="btn-pay" :title="$t('groupDetail.record_payment_title')">
                  {{ $t('debts.action_pay') }}
                </button>
                <button @click.stop="navigateToEnrollment(debt.enrollmentId)" class="btn-icon" :title="$t('debts.action_view')">
                  <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                  </svg>
                </button>
                <button @click.stop="navigateToGroup(debt.groupId)" class="btn-icon" :title="$t('groupDetail.details_title')">
                  <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"></path>
                    <circle cx="9" cy="7" r="4"></circle>
                    <path d="M23 21v-2a4 4 0 00-3-3.87"></path>
                    <path d="M16 3.13a4 4 0 010 7.75"></path>
                  </svg>
                </button>
              </td>
            </tr>
            <tr v-if="!filteredDebts.length && !loading">
              <td colspan="8" class="empty-state">{{ $t('debts.no_debts') }}</td>
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
            <p class="modal-instructions" style="margin-bottom: 1.25rem; text-align: left;" v-if="paymentEnrollment">
              <span v-html="$t('groupDetail.confirm_payment_instructions', { student: '<strong>' + paymentEnrollment.studentName + '</strong>', group: '<strong>' + paymentEnrollment.groupName + '</strong>' })"></span>
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
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'DebtList',
  data() {
    return {
      enrollments: [],
      students: [],
      groups: [],
      branches: [],
      searchQuery: '',
      selectedBranch: '',
      selectedGroup: '',
      loading: false,
      error: null,
      showPaymentModal: false,
      submittingPayment: false,
      paymentForm: {
        amount: '',
        payment_method: 'cash',
        description: ''
      },
      paymentEnrollment: null
    }
  },
  computed: {
    debtEnrollments() {
      if (!this.enrollments.length || !this.students.length || !this.groups.length || !this.branches.length) return []
      
      return this.enrollments
        .filter(e => e.status === 'enrolled' && e.payment_status === 'debt')
        .map(e => {
          const student = this.students.find(s => s.id === e.student) || {}
          const group = this.groups.find(g => g.id === e.group) || {}
          const branch = this.branches.find(b => b.id === group.branch) || {}
          
          return {
            enrollmentId: e.id,
            date: e.date,
            debt_amount: parseFloat(e.debt_amount || 0),
            studentId: e.student,
            studentName: student.full_name || `Student #${e.student}`,
            studentPhone: student.phone1 || '-',
            groupId: e.group,
            groupName: group.name || `Group #${e.group}`,
            branchId: group.branch,
            branchName: branch.name || `Branch #${group.branch}`
          }
        })
    },
    filteredGroupsForSelect() {
      if (!this.selectedBranch) return this.groups
      return this.groups.filter(g => g.branch === this.selectedBranch)
    },
    filteredDebts() {
      let list = this.debtEnrollments
      
      if (this.selectedBranch) {
        list = list.filter(d => d.branchId === this.selectedBranch)
      }
      if (this.selectedGroup) {
        list = list.filter(d => d.groupId === this.selectedGroup)
      }
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase().trim()
        list = list.filter(d => d.studentName.toLowerCase().includes(query))
      }
      
      return list
    },
    totalFilteredDebt() {
      return this.filteredDebts.reduce((sum, d) => sum + d.debt_amount, 0)
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
        const [enrollmentsRes, studentsRes, groupsRes, branchesRes] = await Promise.all([
          axios.get('http://localhost:8000/api/enrollments/'),
          axios.get('http://localhost:8000/api/students/'),
          axios.get('http://localhost:8000/api/groups/'),
          axios.get('http://localhost:8000/api/branches/')
        ])
        
        this.enrollments = enrollmentsRes.data
        this.students = studentsRes.data
        this.groups = groupsRes.data
        this.branches = branchesRes.data
        this.loading = false
      } catch (err) {
        console.error('Error fetching debts data:', err)
        this.error = this.$t('stats.api_error')
        this.loading = false
      }
    },
    formatPrice(price) {
      if (!price && price !== 0) return '0'
      const val = Math.round(parseFloat(price))
      return val.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
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
    formatTime(timeStr) {
      if (!timeStr) return '-'
      const parts = timeStr.split(':')
      if (parts.length >= 2) {
        return `${parts[0]}:${parts[1]}`
      }
      return timeStr
    },
    navigateToEnrollment(id) {
      this.$router.push(`/enrollments/${id}`)
    },
    navigateToGroup(id) {
      this.$router.push(`/groups/${id}`)
    },
    openPaymentModal(debt) {
      this.paymentEnrollment = debt
      const val = Math.round(parseFloat(debt.debt_amount || 0))
      this.paymentForm.amount = val.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
      this.paymentForm.payment_method = 'cash'
      this.paymentForm.description = ''
      this.showPaymentModal = true
    },
    closePaymentModal() {
      this.showPaymentModal = false
      this.paymentEnrollment = null
      this.paymentForm.amount = ''
      this.paymentForm.payment_method = 'cash'
      this.paymentForm.description = ''
    },
    formatPaymentInputPrice(event) {
      const value = event.target.value
      const selectionStart = event.target.selectionStart
      const oldLength = value.length

      const digits = value.replace(/\D/g, '')
      const formatted = digits.replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
      
      this.paymentForm.amount = formatted
      
      this.$nextTick(() => {
        if (event.target) {
          const newLength = formatted.length
          const delta = newLength - oldLength
          const newCursorPos = selectionStart + delta
          event.target.setSelectionRange(newCursorPos, newCursorPos)
        }
      })
    },
    async confirmPayment() {
      this.submittingPayment = true
      try {
        const rawAmount = String(this.paymentForm.amount).replace(/\s/g, '')
        const amountVal = parseFloat(rawAmount || 0)
        
        await axios.post('http://localhost:8000/api/payments/', {
          group: this.paymentEnrollment.groupId,
          student: this.paymentEnrollment.studentId,
          amount: amountVal,
          payment_method: this.paymentForm.payment_method,
          description: this.paymentForm.description || `Payment for group: ${this.paymentEnrollment.groupName}`
        })
        
        this.closePaymentModal()
        await this.fetchData()
      } catch (err) {
        console.error('Error confirming payment:', err)
        alert(this.$t('groupDetail.error_payment'))
      } finally {
        this.submittingPayment = false
      }
    }
  }
}
</script>

<style scoped>
@import '../assets/views.css';

.text-red {
  color: #dc2626 !important;
}

.text-danger-badge {
  background-color: #fee2e2;
  color: #991b1b;
}

.clickable-row {
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.clickable-row:hover {
  background-color: #f1f5f9;
}

.btn-pay {
  background-color: #4f46e5;
  color: white;
  border: none;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  font-size: 0.775rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  display: inline-flex;
  align-items: center;
  margin-right: 0.5rem;
}

.btn-pay:hover {
  background-color: #4338ca;
  transform: translateY(-1px);
  box-shadow: 0 2px 5px rgba(79, 70, 229, 0.2);
}

.btn-pay:active {
  transform: translateY(0);
}
</style>
