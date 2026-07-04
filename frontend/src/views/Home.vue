<template>
  <div class="dashboard-home">
    <!-- Header Section -->
    <div class="home-header">
      <h1 class="welcome-title">{{ $t('stats.dashboard') }}</h1>
      <p class="welcome-subtitle">{{ $t('stats.welcome', { name: username }) }}</p>
    </div>

    <!-- Error/Warning Banner -->
    <div v-if="error" class="info-banner">
      <span>{{ error }}</span>
    </div>

    <!-- Statistics Grid -->
    <div class="stats-grid">
      <!-- Students Stat Card -->
      <div class="stat-card card-purple" @click="$router.push('/students')">
        <div class="card-content">
          <div class="card-info">
            <span class="card-label">{{ $t('stats.registered_students') }}</span>
            <h2 class="card-value" v-if="!loading">{{ studentCount }}</h2>
            <div class="spinner-small" v-else></div>
          </div>
          <div class="card-icon-wrapper">
            <svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 10v6M2 10l10-5 10 5-10 5z"></path>
              <path d="M6 12v5c0 2 2 3 6 3s6-1 6-3v-5"></path>
            </svg>
          </div>
        </div>
        <div class="card-footer">
          <span>{{ $t('stats.view_students') }}</span>
        </div>
      </div>

      <!-- Teachers Stat Card -->
      <div class="stat-card card-blue" @click="$router.push('/teachers')">
        <div class="card-content">
          <div class="card-info">
            <span class="card-label">{{ $t('stats.active_teachers') }}</span>
            <h2 class="card-value" v-if="!loading">{{ teacherCount }}</h2>
            <div class="spinner-small" v-else></div>
          </div>
          <div class="card-icon-wrapper">
            <svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"></path>
              <circle cx="9" cy="7" r="4"></circle>
              <path d="M23 21v-2a4 4 0 00-3-3.87"></path>
              <path d="M16 3.13a4 4 0 010 7.75"></path>
            </svg>
          </div>
        </div>
        <div class="card-footer">
          <span>{{ $t('stats.view_teachers') }}</span>
        </div>
      </div>

      <!-- Outstanding Debt Stat Card -->
      <div class="stat-card card-red" @click="$router.push('/debts')">
        <div class="card-content">
          <div class="card-info">
            <span class="card-label">{{ $t('stats.outstanding_debt') }}</span>
            <h2 class="card-value" v-if="!loading">{{ formatPrice(totalDebtAmount) }} UZS</h2>
            <div class="spinner-small" v-else></div>
          </div>
          <div class="card-icon-wrapper">
            <svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M12 8V12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M12 16H12.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>
        <div class="card-footer">
          <span>{{ $t('stats.students_in_debt', { count: debtStudentsCount }) }}</span>
        </div>
      </div>

      <!-- Active Groups Stat Card -->
      <div class="stat-card card-green" @click="$router.push('/groups')">
        <div class="card-content">
          <div class="card-info">
            <span class="card-label">{{ $t('stats.active_groups') }}</span>
            <h2 class="card-value" v-if="!loading">{{ activeGroupsCount }}</h2>
            <div class="spinner-small" v-else></div>
          </div>
          <div class="card-icon-wrapper">
            <svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"></path>
              <circle cx="9" cy="7" r="4"></circle>
              <path d="M23 21v-2a4 4 0 00-3-3.87"></path>
              <path d="M16 3.13a4 4 0 010 7.75"></path>
            </svg>
          </div>
        </div>
        <div class="card-footer">
          <span>{{ $t('stats.view_groups') }}</span>
        </div>
      </div>

      <!-- Current Month Income Card (Non-clickable) -->
      <div class="stat-card card-orange non-clickable">
        <div class="card-content">
          <div class="card-info">
            <span class="card-label">{{ $t('stats.monthly_income') }}</span>
            <h2 class="card-value" v-if="!loading">{{ formatPrice(currentMonthIncome) }} UZS</h2>
            <div class="spinner-small" v-else></div>
          </div>
          <div class="card-icon-wrapper">
            <svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="1" x2="12" y2="23"></line>
              <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
            </svg>
          </div>
        </div>
        <div class="card-footer">
          <span>{{ $t('stats.income_collected') }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Home',
  data() {
    return {
      username: '',
      studentCount: 0,
      teacherCount: 0,
      totalDebtAmount: 0,
      debtStudentsCount: 0,
      activeGroupsCount: 0,
      currentMonthIncome: 0,
      loading: false,
      error: null
    }
  },
  mounted() {
    this.username = localStorage.getItem('username') || 'User'
    this.fetchStats()
  },
  methods: {
    async fetchStats() {
      this.loading = true
      this.error = null

      try {
        const [studentsRes, usersRes, enrollmentsRes, groupsRes, paymentsRes] = await Promise.all([
          axios.get('/api/students/'),
          axios.get('/api/users/'),
          axios.get('/api/enrollments/'),
          axios.get('/api/groups/'),
          axios.get('/api/payments/')
        ])

        this.studentCount = studentsRes.data.length
        this.teacherCount = usersRes.data.filter(u => u.role === 'teacher').length
        
        // Calculate active ongoing groups
        this.activeGroupsCount = groupsRes.data.filter(g => g.status === 'ongoing').length
        
        // Calculate current month income
        const now = new Date()
        const currentYear = now.getFullYear()
        const currentMonth = now.getMonth()
        const currentMonthPayments = paymentsRes.data.filter(p => {
          const pDate = new Date(p.payment_date)
          return p.is_active && p.status === 'accepted' && pDate.getFullYear() === currentYear && pDate.getMonth() === currentMonth
        })
        this.currentMonthIncome = currentMonthPayments.reduce((sum, p) => sum + parseFloat(p.amount || 0), 0)

        // Filter active debt enrollments
        const activeDebtEnrollments = enrollmentsRes.data.filter(
          e => e.status === 'enrolled' && e.payment_status === 'debt'
        )
        
        // Calculate total outstanding debt
        this.totalDebtAmount = activeDebtEnrollments.reduce(
          (sum, e) => sum + parseFloat(e.debt_amount || 0),
          0
        )
        
        // Calculate unique students in debt
        const uniqueDebtStudents = new Set(activeDebtEnrollments.map(e => e.student))
        this.debtStudentsCount = uniqueDebtStudents.size
        
        this.loading = false
      } catch (err) {
        console.error('Error fetching statistics:', err)
        this.error = this.$t('stats.api_error')
        this.loading = false
      }
    },
    formatPrice(price) {
      if (!price && price !== 0) return '0'
      const val = Math.round(parseFloat(price))
      return val.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

.dashboard-home {
  font-family: 'Outfit', sans-serif;
  padding: 2.5rem;
  max-width: 1200px;
  margin: 0 auto;
  text-align: left;
  box-sizing: border-box;
}

.home-header {
  margin-bottom: 2.5rem;
}

.welcome-title {
  font-size: 2.25rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.5rem 0;
  letter-spacing: -0.5px;
}

.welcome-subtitle {
  font-size: 1rem;
  color: #64748b;
  margin: 0;
}

/* Info Banner */
.info-banner {
  background-color: rgba(59, 130, 246, 0.06);
  border: 1px solid rgba(59, 130, 246, 0.15);
  color: #2563eb;
  padding: 0.875rem 1.25rem;
  border-radius: 12px;
  margin-bottom: 2rem;
  font-size: 0.875rem;
  line-height: 1.4;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: white;
  border-radius: 20px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -2px rgba(0, 0, 0, 0.02);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  display: flex;
  flex-direction: column;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.02);
}

.card-content {
  padding: 1.75rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-grow: 1;
}

.card-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.card-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.card-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
  line-height: 1;
}

.card-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.card-icon {
  width: 28px;
  height: 28px;
}

/* Card Themes */
.card-purple .card-icon-wrapper {
  background-color: rgba(99, 102, 241, 0.08);
  color: #6366f1;
}
.card-purple:hover .card-icon-wrapper {
  background-color: #6366f1;
  color: white;
}

.card-blue .card-icon-wrapper {
  background-color: rgba(59, 130, 246, 0.08);
  color: #3b82f6;
}
.card-blue:hover .card-icon-wrapper {
  background-color: #3b82f6;
  color: white;
}

.card-red .card-icon-wrapper {
  background-color: rgba(239, 68, 68, 0.08);
  color: #ef4444;
}
.card-red:hover .card-icon-wrapper {
  background-color: #ef4444;
  color: white;
}
.card-red .card-footer {
  color: #ef4444;
}

.card-green .card-icon-wrapper {
  background-color: rgba(16, 185, 129, 0.08);
  color: #10b981;
}
.card-green:hover .card-icon-wrapper {
  background-color: #10b981;
  color: white;
}
.card-green .card-footer {
  color: #10b981;
}

.card-orange .card-icon-wrapper {
  background-color: rgba(249, 115, 22, 0.08);
  color: #f97316;
}
.card-orange:hover .card-icon-wrapper {
  background-color: #f97316;
  color: white;
}
.card-orange .card-footer {
  color: #f97316;
}

.stat-card.non-clickable {
  cursor: default !important;
}
.stat-card.non-clickable:hover {
  transform: none !important;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -2px rgba(0, 0, 0, 0.02) !important;
}
.stat-card.non-clickable:hover .card-footer {
  background-color: #f8fafc !important;
}
.stat-card.non-clickable:hover .card-icon-wrapper {
  background-color: rgba(249, 115, 22, 0.08) !important;
  color: #f97316 !important;
}

.card-footer {
  padding: 1rem 2rem;
  background-color: #f8fafc;
  border-top: 1px solid #f1f5f9;
  font-size: 0.85rem;
  font-weight: 600;
  color: #4f46e5;
  transition: background-color 0.2s;
}

.stat-card:hover .card-footer {
  background-color: #f1f5f9;
}

/* Loading Spinners */
.spinner-small {
  width: 24px;
  height: 24px;
  border: 2px solid rgba(99, 102, 241, 0.2);
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 480px) {
  .dashboard-home {
    padding: 1.5rem;
  }
  .welcome-title {
    font-size: 1.75rem;
  }
}
</style>
