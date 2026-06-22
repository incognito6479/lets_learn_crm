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
      
      <div style="width: 200px;">
        <select v-model="selectedGroup" class="form-input">
          <option value="">All Groups</option>
          <option v-for="group in groups" :key="group.id" :value="group.id">
            {{ group.name }}
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
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="payment in filteredPayments" :key="payment.id" class="table-row">
              <td class="font-mono text-muted">#{{ payment.id }}</td>
              <td class="font-semibold">{{ getStudentName(payment.student) }}</td>
              <td>{{ getGroupName(payment.group) }}</td>
              <td class="font-mono font-semibold text-green">{{ formatPrice(payment.amount) }} UZS</td>
              <td>
                <span :class="['status-badge', payment.payment_method || 'cash']">
                  {{ formatMethod(payment.payment_method) }}
                </span>
              </td>
              <td>{{ formatDate(payment.payment_date) }}</td>
              <td>{{ payment.description || '-' }}</td>
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
      error: null
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
      const sum = this.filteredPayments.reduce((acc, curr) => acc + parseFloat(curr.amount || 0), 0)
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
    formatMethod(method) {
      if (!method) return 'Cash'
      return method.charAt(0).toUpperCase() + method.slice(1)
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
</style>
