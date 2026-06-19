<template>
  <div class="dashboard-home">
    <!-- Header Section -->
    <div class="home-header">
      <h1 class="welcome-title">Dashboard Overview</h1>
      <p class="welcome-subtitle">Welcome back, {{ username }}! Here is what's happening today.</p>
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
            <span class="card-label">Registered Students</span>
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
          <span>View all students &rarr;</span>
        </div>
      </div>

      <!-- Teachers Stat Card -->
      <div class="stat-card card-blue" @click="$router.push('/teachers')">
        <div class="card-content">
          <div class="card-info">
            <span class="card-label">Active Instructors</span>
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
          <span>View all instructors &rarr;</span>
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
        const [studentsRes, usersRes] = await Promise.all([
          axios.get('http://localhost:8000/api/students/'),
          axios.get('http://localhost:8000/api/users/')
        ])

        this.studentCount = studentsRes.data.length
        this.teacherCount = usersRes.data.filter(u => u.role === 'teacher').length
        this.loading = false
      } catch (err) {
        console.error('Error fetching statistics:', err)
        this.error = 'Unable to connect to backend API.'
        this.loading = false
      }
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
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
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
