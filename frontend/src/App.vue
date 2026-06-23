<template>
  <div id="app" :class="{ 'dashboard-layout': isLoggedIn }">
    <!-- Left Sidebar (Logged In Only) -->
    <aside v-if="isLoggedIn" class="sidebar">
      <div class="sidebar-brand">
        <div class="brand-logo">
          <svg class="logo-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <span class="brand-name">Let's Learn CRM</span>
      </div>
      
      <nav class="sidebar-nav">
        <router-link v-if="userRole !== 'teacher'" to="/" class="nav-item">
          <span class="nav-icon">📊</span>
          <span class="nav-text">Statistics</span>
        </router-link>
        <router-link to="/timetable" class="nav-item">
          <span class="nav-icon">📅</span>
          <span class="nav-text">Timetable</span>
        </router-link>
        <router-link to="/groups" class="nav-item">
          <span class="nav-icon">👥</span>
          <span class="nav-text">Groups</span>
        </router-link>
        <router-link v-if="userRole !== 'teacher'" to="/payments" class="nav-item">
          <span class="nav-icon">💰</span>
          <span class="nav-text">Payments</span>
        </router-link>
        <router-link v-if="userRole !== 'teacher'" to="/debts" class="nav-item">
          <span class="nav-icon">⚠️</span>
          <span class="nav-text">Debts</span>
        </router-link>
        <router-link v-if="userRole !== 'teacher'" to="/students" class="nav-item">
          <span class="nav-icon">🎓</span>
          <span class="nav-text">Students</span>
        </router-link>
        <router-link v-if="userRole !== 'teacher'" to="/teachers" class="nav-item">
          <span class="nav-icon">👨‍🏫</span>
          <span class="nav-text">Teachers</span>
        </router-link>
        <router-link v-if="userRole !== 'teacher'" to="/rooms" class="nav-item">
          <span class="nav-icon">🏫</span>
          <span class="nav-text">Rooms</span>
        </router-link>
        <router-link v-if="userRole !== 'teacher'" to="/branches" class="nav-item">
          <span class="nav-icon">🏢</span>
          <span class="nav-text">Branches</span>
        </router-link>
        <router-link v-if="userRole !== 'teacher'" to="/courses" class="nav-item">
          <span class="nav-icon">📚</span>
          <span class="nav-text">Courses</span>
        </router-link>
      </nav>
    </aside>

    <!-- Main Content Container -->
    <div class="main-container">
      <!-- Top Header (Logged In Only) -->
      <header v-if="isLoggedIn" class="top-header">
        <div class="header-right">
          <div class="user-profile">
            <span class="avatar">{{ userInitials }}</span>
            <span class="username">{{ username }}</span>
          </div>
          <button @click="logout" class="logout-btn">
            <svg class="logout-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M16 17L21 12L16 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M21 12H9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>Sign Out</span>
          </button>
        </div>
      </header>

      <!-- Viewport area -->
      <main class="content-area">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'App',
  data() {
    return {
      username: '',
      userRole: ''
    }
  },
  computed: {
    isLoggedIn() {
      return this.$route.name !== 'Login' && !!localStorage.getItem('auth_token')
    },
    userInitials() {
      if (!this.username) return 'U'
      return this.username.charAt(0).toUpperCase()
    }
  },
  watch: {
    $route() {
      this.updateUser()
    }
  },
  created() {
    // Inject authorization header if active session exists
    const token = localStorage.getItem('auth_token')
    if (token) {
      axios.defaults.headers.common['Authorization'] = 'Basic ' + token
    }
    this.updateUser()
  },
  methods: {
    updateUser() {
      this.username = localStorage.getItem('username') || ''
      this.userRole = localStorage.getItem('user_role') || ''
    },
    logout() {
      // Clear storage
      localStorage.removeItem('auth_token')
      localStorage.removeItem('username')
      localStorage.removeItem('user_role')
      
      // Clear axios defaults
      delete axios.defaults.headers.common['Authorization']
      
      // Redirect to login page
      this.$router.push('/login')
    }
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

body {
  margin: 0;
  padding: 0;
  background-color: #f8fafc;
  font-family: 'Outfit', sans-serif;
  color: #1e293b;
}

#app {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  min-height: 100vh;
  box-sizing: border-box;
}

/* Two column dashboard layout */
.dashboard-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* Left Sidebar Styles */
.sidebar {
  width: 260px;
  background-color: #0f172a;
  color: #f8fafc;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  border-right: 1px solid #1e293b;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.5rem 1.75rem;
  border-bottom: 1px solid #1e293b;
}

.brand-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #6366f1, #3b82f6);
  border-radius: 10px;
  color: white;
}

.logo-icon {
  width: 20px;
  height: 20px;
}

.brand-name {
  font-size: 1.15rem;
  font-weight: 700;
  letter-spacing: -0.25px;
  background: linear-gradient(to right, #ffffff, #cbd5e1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 1.5rem 1rem;
  overflow-y: auto;
  flex-grow: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: #94a3b8;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.95rem;
  border-radius: 10px;
  transition: all 0.2s ease;
}

.nav-item:hover {
  color: #ffffff;
  background-color: rgba(255, 255, 255, 0.05);
}

.nav-item.router-link-exact-active {
  color: #ffffff;
  background-color: #6366f1;
  font-weight: 600;
}

.nav-icon {
  font-size: 1.1rem;
}

/* Main Container Styles */
.main-container {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  overflow: hidden;
}

/* Top Header Styles */
.top-header {
  height: 70px;
  background-color: #ffffff;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0 2rem;
  box-sizing: border-box;
  flex-shrink: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.avatar {
  width: 32px;
  height: 32px;
  background-color: rgba(99, 102, 241, 0.1);
  color: #6366f1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-weight: 600;
  font-size: 0.9rem;
}

.username {
  font-weight: 600;
  color: #1e293b;
  font-size: 0.925rem;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: none;
  border: 1px solid #e2e8f0;
  padding: 0.4rem 0.85rem;
  border-radius: 8px;
  color: #64748b;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.logout-btn:hover {
  color: #ef4444;
  background-color: rgba(239, 68, 68, 0.05);
  border-color: rgba(239, 68, 68, 0.15);
}

.logout-icon {
  width: 15px;
  height: 15px;
}

/* Main Content Area */
.content-area {
  flex-grow: 1;
  overflow-y: auto;
  background-color: #f8fafc;
}
</style>
