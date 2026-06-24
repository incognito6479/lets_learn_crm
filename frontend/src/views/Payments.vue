<template>
  <div class="view-container">
    <div class="view-header">
      <div>
        <h1 class="view-title">{{ $t('payments.title') }}</h1>
        <p class="view-subtitle">{{ $t('payments.sub') }}</p>
      </div>
      <div class="badge-count" v-if="filteredPayments.length">{{ $t('payments.total_collected') }}: {{ totalPayments }} UZS</div>
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
      
      <div style="min-width: 250px;">
        <select v-model="selectedGroup" class="form-input">
          <option value="">{{ $t('payments.filter_group') }}</option>
          <option v-for="group in groups" :key="group.id" :value="group.id">
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
              <th>{{ $t('stats.student') }}</th>
              <th>{{ $t('stats.group') }}</th>
              <th>{{ $t('payments.col_amount') }}</th>
              <th>{{ $t('payments.col_method') }}</th>
              <th>{{ $t('payments.col_date') }}</th>
              <th>{{ $t('payments.col_status') }}</th>
              <th>{{ $t('common.description') }}</th>
              <th style="text-align: right;">{{ $t('common.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="payment in filteredPayments" :key="payment.id" class="table-row" :style="!payment.is_active || payment.status === 'canceled' ? 'opacity: 0.65; background-color: #f8fafc;' : ''">
              <td class="font-mono text-muted">#{{ payment.id }}</td>
              <td class="font-semibold">{{ getStudentName(payment.student) }}</td>
              <td>{{ getGroupName(payment.group) }}</td>
              <td class="font-mono font-semibold text-green" :style="!payment.is_active || payment.status === 'canceled' ? 'text-decoration: line-through; color: #94a3b8 !important;' : ''">{{ formatPrice(payment.amount) }} UZS</td>
              <td>
                <span :class="['status-badge', payment.payment_method || 'cash']">
                  {{ $t('groupDetail.' + (payment.payment_method || 'cash')) }}
                </span>
              </td>
              <td>{{ formatDate(payment.payment_date) }}</td>
              <td>
                <span :class="['status-badge', payment.status || 'accepted']">
                  {{ $t('payments.status_' + (payment.status || 'accepted')) }}
                </span>
              </td>
              <td>{{ payment.description || '-' }}</td>
              <td class="actions-cell">
                <button
                  v-if="payment.is_active && payment.status !== 'canceled'"
                  @click="openCancelModal(payment)"
                  class="btn-icon btn-icon-danger"
                  :title="$t('payments.cancel_modal_title')"
                  style="width: auto; padding: 0 0.5rem; font-size: 0.8rem; font-weight: 600; gap: 0.25rem;"
                >
                  <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="15" y1="9" x2="9" y2="15"></line>
                    <line x1="9" y1="9" x2="15" y2="15"></line>
                  </svg>
                  {{ $t('payments.cancel_btn') }}
                </button>
                <span v-else class="text-muted" style="font-size: 0.8rem; font-style: italic;">{{ $t('payments.status_canceled') }}</span>
              </td>
            </tr>
            <tr v-if="!filteredPayments.length && !loading">
              <td colspan="9" class="empty-state">{{ $t('stats.no_payments') }}</td>
            </tr>
            <tr v-if="loading">
              <td colspan="9" class="loading-state">
                <div class="spinner"></div>
                <span>{{ $t('common.loading') }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Cancel Payment Modal -->
    <div v-if="showCancelModal" class="modal-backdrop" @click.self="closeCancelModal">
      <div class="modal-content" style="max-width: 480px;">
        <div class="modal-header">
          <h2 class="modal-title">{{ $t('payments.cancel_modal_title') }}</h2>
          <button @click="closeCancelModal" class="modal-close">
            <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <form @submit.prevent="confirmCancelPayment">
          <div class="modal-body">
            <p class="modal-instructions" style="color: #ef4444; font-weight: 600; margin-bottom: 1.25rem;">
              {{ $t('payments.cancel_modal_instructions') }}
            </p>

            <div class="form-group" style="margin-bottom: 1rem;">
              <label class="form-label">{{ $t('stats.student') }}</label>
              <input
                type="text"
                :value="getStudentName(selectedPaymentForCancel.student)"
                disabled
                class="form-input"
                style="background-color: #f1f5f9; cursor: not-allowed;"
              />
            </div>

            <div class="form-group" style="margin-bottom: 1rem;">
              <label class="form-label">{{ $t('stats.group') }}</label>
              <input
                type="text"
                :value="getGroupName(selectedPaymentForCancel.group)"
                disabled
                class="form-input"
                style="background-color: #f1f5f9; cursor: not-allowed;"
              />
            </div>

            <div class="form-group" style="margin-bottom: 1rem;">
              <label class="form-label">{{ $t('groupDetail.payment_amount') }}</label>
              <input
                type="text"
                :value="formatPrice(selectedPaymentForCancel.amount) + ' UZS'"
                disabled
                class="form-input"
                style="background-color: #f1f5f9; cursor: not-allowed;"
              />
            </div>

            <div class="form-group" style="margin-bottom: 1rem;">
              <label class="form-label">{{ $t('groupDetail.payment_method') }}</label>
              <input
                type="text"
                :value="$t('groupDetail.' + (selectedPaymentForCancel.payment_method || 'cash'))"
                disabled
                class="form-input"
                style="background-color: #f1f5f9; cursor: not-allowed;"
              />
            </div>

            <div class="form-group">
              <label class="form-label">{{ $t('common.description') }}</label>
              <textarea
                :value="selectedPaymentForCancel.description || '-'"
                disabled
                class="form-input"
                rows="2"
                style="background-color: #f1f5f9; cursor: not-allowed; resize: none;"
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" @click="closeCancelModal" class="btn btn-secondary">{{ $t('common.back') }}</button>
            <button
              type="submit"
              class="btn btn-danger"
              :disabled="submittingCancel"
            >
              {{ submittingCancel ? $t('common.loading') : $t('payments.void_payment_btn') }}
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
  name: 'Payments',
  data() {
    return {
      payments: [],
      students: [],
      groups: [],
      searchQuery: '',
      selectedGroup: '',
      loading: false,
      error: null,
      showCancelModal: false,
      selectedPaymentForCancel: null,
      submittingCancel: false
    }
  },
  computed: {
    filteredPayments() {
      let list = this.payments
      
      if (this.selectedGroup) {
        list = list.filter(p => p.group === this.selectedGroup)
      }
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase().trim()
        list = list.filter(p => {
          const name = this.getStudentName(p.student).toLowerCase()
          return name.includes(query)
        })
      }
      
      return list
    },
    totalPayments() {
      const sum = this.filteredPayments
        .filter(p => p.is_active && p.status === 'accepted')
        .reduce((acc, curr) => acc + parseFloat(curr.amount || 0), 0)
      return this.formatPrice(sum)
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
        const [paymentsRes, studentsRes, groupsRes] = await Promise.all([
          axios.get('http://localhost:8000/api/payments/'),
          axios.get('http://localhost:8000/api/students/'),
          axios.get('http://localhost:8000/api/groups/')
        ])
        this.payments = paymentsRes.data
        this.students = studentsRes.data
        this.groups = groupsRes.data
        this.loading = false
      } catch (err) {
        console.error('Error fetching payments:', err)
        this.error = this.$t('stats.api_error')
        this.loading = false
      }
    },
    getStudentName(studentId) {
      const student = this.students.find(s => s.id === studentId)
      return student ? student.full_name : `Student #${studentId}`
    },
    getGroupName(groupId) {
      const group = this.groups.find(g => g.id === groupId)
      return group ? group.name : `Group #${groupId}`
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
    formatTime(timeStr) {
      if (!timeStr) return '-'
      const parts = timeStr.split(':')
      if (parts.length >= 2) {
        return `${parts[0]}:${parts[1]}`
      }
      return timeStr
    },
    formatMethod(method) {
      if (!method) return 'Cash'
      return method.charAt(0).toUpperCase() + method.slice(1)
    },
    openCancelModal(payment) {
      this.selectedPaymentForCancel = payment
      this.showCancelModal = true
    },
    closeCancelModal() {
      this.showCancelModal = false
      this.selectedPaymentForCancel = null
    },
    async confirmCancelPayment() {
      this.submittingCancel = true
      try {
        await axios.patch(`http://localhost:8000/api/payments/${this.selectedPaymentForCancel.id}/`, {
          is_active: false,
          status: 'canceled'
        })
        this.closeCancelModal()
        await this.fetchData()
      } catch (err) {
        console.error('Error cancelling payment:', err)
        alert(this.$t('payments.error_cancel'))
      } finally {
        this.submittingCancel = false
      }
    }
  }
}
</script>

<style scoped>
@import '../assets/views.css';

.text-green {
  color: #16a34a !important;
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
</style>
