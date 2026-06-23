<template>
  <div class="view-container">
    <div class="view-header">
      <div>
        <h1 class="view-title">Payments</h1>
        <p class="view-subtitle">Review incoming transactions and student bills</p>
      </div>
      <div class="badge-count" v-if="filteredPayments.length">{{ totalPayments }} UZS total</div>
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
          placeholder="Search by student name..."
          class="form-input"
        />
      </div>
      
      <div style="min-width: 250px;">
        <select v-model="selectedGroup" class="form-input">
          <option value="">All Groups</option>
          <option v-for="group in groups" :key="group.id" :value="group.id">
            {{ group.name }} ({{ formatTime(group.starts_at) }}, {{ group.group_days_at || 'Mon-Wed-Fri' }})
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
              <th>Student</th>
              <th>Group</th>
              <th>Amount</th>
              <th>Method</th>
              <th>Date</th>
              <th>Status</th>
              <th>Description</th>
              <th style="text-align: right;">Actions</th>
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
                  {{ formatMethod(payment.payment_method) }}
                </span>
              </td>
              <td>{{ formatDate(payment.payment_date) }}</td>
              <td>
                <span :class="['status-badge', payment.status || 'accepted']">
                  {{ payment.status || 'accepted' }}
                </span>
              </td>
              <td>{{ payment.description || '-' }}</td>
              <td class="actions-cell">
                <button
                  v-if="payment.is_active && payment.status !== 'canceled'"
                  @click="openCancelModal(payment)"
                  class="btn-icon btn-icon-danger"
                  title="Cancel Payment"
                  style="width: auto; padding: 0 0.5rem; font-size: 0.8rem; font-weight: 600; gap: 0.25rem;"
                >
                  <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="15" y1="9" x2="9" y2="15"></line>
                    <line x1="9" y1="9" x2="15" y2="15"></line>
                  </svg>
                  Cancel
                </button>
                <span v-else class="text-muted" style="font-size: 0.8rem; font-style: italic;">Canceled</span>
              </td>
            </tr>
            <tr v-if="!filteredPayments.length && !loading">
              <td colspan="7" class="empty-state">No payments found.</td>
            </tr>
            <tr v-if="loading">
              <td colspan="7" class="loading-state">
                <div class="spinner"></div>
                <span>Loading payments...</span>
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
          <h2 class="modal-title">Cancel Payment</h2>
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
              Are you sure you want to cancel this payment? This action is irreversible and will restore student debt.
            </p>

            <div class="form-group" style="margin-bottom: 1rem;">
              <label class="form-label">Student Name</label>
              <input
                type="text"
                :value="getStudentName(selectedPaymentForCancel.student)"
                disabled
                class="form-input"
                style="background-color: #f1f5f9; cursor: not-allowed;"
              />
            </div>

            <div class="form-group" style="margin-bottom: 1rem;">
              <label class="form-label">Group Name</label>
              <input
                type="text"
                :value="getGroupName(selectedPaymentForCancel.group)"
                disabled
                class="form-input"
                style="background-color: #f1f5f9; cursor: not-allowed;"
              />
            </div>

            <div class="form-group" style="margin-bottom: 1rem;">
              <label class="form-label">Amount (UZS)</label>
              <input
                type="text"
                :value="formatPrice(selectedPaymentForCancel.amount) + ' UZS'"
                disabled
                class="form-input"
                style="background-color: #f1f5f9; cursor: not-allowed;"
              />
            </div>

            <div class="form-group" style="margin-bottom: 1rem;">
              <label class="form-label">Payment Method</label>
              <input
                type="text"
                :value="formatMethod(selectedPaymentForCancel.payment_method)"
                disabled
                class="form-input"
                style="background-color: #f1f5f9; cursor: not-allowed;"
              />
            </div>

            <div class="form-group">
              <label class="form-label">Description</label>
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
            <button type="button" @click="closeCancelModal" class="btn btn-secondary">Go Back</button>
            <button
              type="submit"
              class="btn btn-danger"
              :disabled="submittingCancel"
            >
              {{ submittingCancel ? 'Cancelling...' : 'Yes, Cancel Payment' }}
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
        this.error = 'Failed to load payments details from backend.'
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
        return date.toLocaleDateString('en-US', {
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
        alert('An error occurred while cancelling the payment.')
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
