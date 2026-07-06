<template>
  <div id="app" :class="{ 'dashboard-layout': isLoggedIn, 'sidebar-collapsed': isSidebarCollapsed, 'is-mobile': isMobile, 'drawer-open': !isSidebarCollapsed && isMobile }">
    <!-- Sidebar mobile backdrop overlay -->
    <div v-if="isLoggedIn && !isSidebarCollapsed && isMobile" class="sidebar-backdrop" @click="closeSidebar"></div>

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
          <span class="nav-text">{{ $t('nav.statistics') }}</span>
        </router-link>
        <router-link to="/timetable" class="nav-item">
          <span class="nav-icon">📅</span>
          <span class="nav-text">{{ $t('nav.timetable') }}</span>
        </router-link>
        <router-link to="/groups" class="nav-item">
          <span class="nav-icon">👥</span>
          <span class="nav-text">{{ $t('nav.groups') }}</span>
        </router-link>
        <router-link v-if="userRole !== 'teacher'" to="/payments" class="nav-item">
          <span class="nav-icon">💰</span>
          <span class="nav-text">{{ $t('nav.payments') }}</span>
        </router-link>
        <router-link v-if="userRole !== 'teacher'" to="/debts" class="nav-item">
          <span class="nav-icon">⚠️</span>
          <span class="nav-text">{{ $t('nav.debts') }}</span>
        </router-link>
        <router-link v-if="userRole !== 'teacher'" to="/students" class="nav-item">
          <span class="nav-icon">🎓</span>
          <span class="nav-text">{{ $t('nav.students') }}</span>
        </router-link>
        <router-link v-if="userRole !== 'teacher'" to="/teachers" class="nav-item">
          <span class="nav-icon">👨‍🏫</span>
          <span class="nav-text">{{ $t('nav.teachers') }}</span>
        </router-link>
        <router-link v-if="userRole !== 'teacher'" to="/rooms" class="nav-item">
          <span class="nav-icon">🏫</span>
          <span class="nav-text">{{ $t('nav.rooms') }}</span>
        </router-link>
        <router-link v-if="userRole !== 'teacher'" to="/branches" class="nav-item">
          <span class="nav-icon">🏢</span>
          <span class="nav-text">{{ $t('nav.branches') }}</span>
        </router-link>
        <router-link v-if="userRole !== 'teacher'" to="/courses" class="nav-item">
          <span class="nav-icon">📚</span>
          <span class="nav-text">{{ $t('nav.courses') }}</span>
        </router-link>
      </nav>
    </aside>

    <!-- Main Content Container -->
    <div class="main-container">
      <!-- Top Header (Logged In Only) -->
      <header v-if="isLoggedIn" class="top-header">
        <div class="header-left">
          <button @click="toggleSidebar" class="sidebar-toggle-btn" :title="$t('common.menu') || 'Menu'">
            <svg class="toggle-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <line x1="3" y1="12" x2="21" y2="12"></line>
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <line x1="3" y1="18" x2="21" y2="18"></line>
            </svg>
          </button>
        </div>
        <div class="header-right">
          <!-- Language Switcher -->
          <div class="lang-switcher">
            <button 
              type="button"
              @click="changeLang('uz')" 
              :class="{ active: currentLang === 'uz' }" 
              class="lang-btn"
            >UZ</button>
            <button 
              type="button"
              @click="changeLang('ru')" 
              :class="{ active: currentLang === 'ru' }" 
              class="lang-btn"
            >RU</button>
          </div>

          <!-- Notification Button with count in light yellow rectangle -->
          <div class="notification-container" v-if="isLoggedIn">
            <button 
              @click="$router.push({ name: 'Notifications' })" 
              class="notif-yellow-btn" 
              :title="$t('common.notifications')"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="notif-bell-icon">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
                <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
              </svg>
              <span v-if="unreadNotificationsCount > 0" class="notif-yellow-count">
                {{ unreadNotificationsCount }}
              </span>
            </button>
          </div>

          <!-- User Profile Dropdown -->
          <div class="user-dropdown-container" v-if="isLoggedIn">
            <button @click.stop="toggleUserDropdown" class="user-profile-trigger">
              <span class="avatar">{{ userInitials }}</span>
              <span class="username" v-if="!isMobile">{{ username }}</span>
              <span class="chevron">▼</span>
            </button>
            <div v-if="isUserDropdownOpen" class="dropdown-menu">
              <button @click="triggerChangePassword" class="dropdown-link">
                <span class="dropdown-link-icon">🔑</span>
                <span>{{ $t('nav.changePassword') }}</span>
              </button>
              <button @click="logout" class="dropdown-link logout-link">
                <svg class="logout-icon-svg" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 16px; height: 16px; margin-right: 0.5rem;">
                  <path d="M9 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M16 17L21 12L16 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M21 12H9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span>{{ $t('nav.signOut') }}</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <!-- Viewport area -->
      <main class="content-area">
        <router-view />
      </main>
    </div>

    <!-- Change Password Modal -->
    <div v-if="showChangePasswordModal" class="modal-backdrop-cp" @click.self="closeChangePasswordModal">
      <div class="modal-content-cp">
        <div class="modal-header-cp">
          <h2 class="modal-title-cp">{{ $t('nav.changePassword') }}</h2>
          <button @click="closeChangePasswordModal" class="modal-close-cp">
            <svg class="icon-svg-cp" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <form @submit.prevent="submitChangePassword">
          <div class="modal-body-cp">
            <div v-if="changePasswordError" class="error-banner-cp">
              {{ changePasswordError }}
            </div>
            
            <div class="form-group-cp">
              <label for="newPassword" class="form-label-cp">{{ $t('nav.newPassword') }}</label>
              <input
                type="password"
                id="newPassword"
                v-model="changePasswordForm.newPassword"
                required
                class="form-input-cp"
              />
            </div>
            
            <div class="form-group-cp">
              <label for="confirmPassword" class="form-label-cp">{{ $t('nav.confirmPassword') }}</label>
              <input
                type="password"
                id="confirmPassword"
                v-model="changePasswordForm.confirmPassword"
                required
                class="form-input-cp"
              />
            </div>
          </div>
          <div class="modal-footer-cp">
            <button type="button" @click="closeChangePasswordModal" class="btn-cp btn-secondary-cp">{{ $t('common.cancel') }}</button>
            <button
              type="submit"
              class="btn-cp btn-primary-cp"
              :disabled="submittingChangePassword || !changePasswordForm.newPassword || !changePasswordForm.confirmPassword"
            >
              {{ submittingChangePassword ? $t('common.saving') || 'Saving...' : $t('common.save') || 'Save' }}
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
  name: 'App',
  data() {
    return {
      username: '',
      userRole: '',
      isSidebarCollapsed: false,
      isMobile: false,
      isUserDropdownOpen: false,
      showChangePasswordModal: false,
      changePasswordForm: {
        newPassword: '',
        confirmPassword: ''
      },
      submittingChangePassword: false,
      changePasswordError: null,
      unreadNotificationsCount: 0,
      notificationPollingInterval: null
    }
  },
  computed: {
    isLoggedIn() {
      return this.$route.name !== 'Login' && !!localStorage.getItem('auth_token')
    },
    userInitials() {
      if (!this.username) return 'U'
      return this.username.charAt(0).toUpperCase()
    },
    currentLang() {
      return this.$i18n.locale
    }
  },
  watch: {
    $route() {
      this.updateUser()
      // Automatically collapse/close sidebar drawer on route navigation on mobile
      if (this.isMobile) {
        this.isSidebarCollapsed = true
      }
    }
  },
  created() {
    // Inject authorization header if active session exists
    const token = localStorage.getItem('auth_token')
    if (token) {
      axios.defaults.headers.common['Authorization'] = 'Bearer ' + token
    }

    // Set up Axios interceptors for JWT token attachment and automatic refreshing
    axios.interceptors.request.use(
      (config) => {
        const activeToken = localStorage.getItem('auth_token')
        if (activeToken) {
          config.headers['Authorization'] = 'Bearer ' + activeToken
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config
        if (error.response && error.response.status === 401 && !originalRequest._retry) {
          if (originalRequest.url.includes('/api/token/')) {
            return Promise.reject(error)
          }
          originalRequest._retry = true
          const refreshToken = localStorage.getItem('refresh_token')
          if (refreshToken) {
            try {
              const res = await axios.post('/api/token/refresh/', {
                refresh: refreshToken
              })
              const newAccessToken = res.data.access
              localStorage.setItem('auth_token', newAccessToken)
              axios.defaults.headers.common['Authorization'] = 'Bearer ' + newAccessToken
              originalRequest.headers['Authorization'] = 'Bearer ' + newAccessToken
              return axios(originalRequest)
            } catch (refreshErr) {
              console.error('Refresh token expired or invalid:', refreshErr)
              this.logout()
              return Promise.reject(refreshErr)
            }
          } else {
            this.logout()
          }
        }
        return Promise.reject(error)
      }
    )

    this.updateUser()
    
    // Initialize resize check and collapsed state
    this.handleResize()
    window.addEventListener('resize', this.handleResize)
    
    const storedCollapsed = localStorage.getItem('sidebar_collapsed')
    if (storedCollapsed !== null) {
      this.isSidebarCollapsed = storedCollapsed === 'true'
    } else {
      this.isSidebarCollapsed = this.isMobile
    }

    document.addEventListener('click', this.handleDocumentClick)
    window.addEventListener('update-unread-badge', this.fetchNotifications)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize)
    document.removeEventListener('click', this.handleDocumentClick)
    window.removeEventListener('update-unread-badge', this.fetchNotifications)
    this.stopNotificationPolling()
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize)
    document.removeEventListener('click', this.handleDocumentClick)
    window.removeEventListener('update-unread-badge', this.fetchNotifications)
    this.stopNotificationPolling()
  },
  methods: {
    updateUser() {
      this.username = localStorage.getItem('username') || ''
      this.userRole = localStorage.getItem('user_role') || ''
      if (this.isLoggedIn) {
        this.fetchNotifications()
        this.startNotificationPolling()
      } else {
        this.stopNotificationPolling()
      }
    },
    logout() {
      // Clear storage
      localStorage.removeItem('auth_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('username')
      localStorage.removeItem('user_role')
      localStorage.removeItem('user_id')
      this.stopNotificationPolling()
      
      // Clear axios defaults
      delete axios.defaults.headers.common['Authorization']
      
      // Redirect to login page
      this.$router.push('/login')
    },
    changeLang(lang) {
      this.$i18n.locale = lang
    },
    toggleSidebar() {
      this.isSidebarCollapsed = !this.isSidebarCollapsed
      localStorage.setItem('sidebar_collapsed', this.isSidebarCollapsed)
    },
    closeSidebar() {
      this.isSidebarCollapsed = true
      localStorage.setItem('sidebar_collapsed', true)
    },
    handleResize() {
      this.isMobile = window.innerWidth <= 768
      if (this.isMobile) {
        this.isSidebarCollapsed = true
      }
    },
    toggleUserDropdown(event) {
      this.isUserDropdownOpen = !this.isUserDropdownOpen
    },
    closeUserDropdown() {
      this.isUserDropdownOpen = false
    },
    handleDocumentClick(event) {
      if (this.isUserDropdownOpen) {
        this.closeUserDropdown()
      }
      if (this.isNotificationDropdownOpen && !event.target.closest('.notification-container')) {
        this.closeNotificationDropdown()
      }
    },
    triggerChangePassword() {
      this.closeUserDropdown()
      this.changePasswordForm.newPassword = ''
      this.changePasswordForm.confirmPassword = ''
      this.changePasswordError = null
      this.showChangePasswordModal = true
    },
    closeChangePasswordModal() {
      this.showChangePasswordModal = false
    },
    async fetchNotifications() {
      if (!this.isLoggedIn) return
      try {
        const countRes = await axios.get('/api/notifications/unread-count/')
        this.unreadNotificationsCount = countRes.data.unread_count
      } catch (err) {
        console.error('Error fetching notifications:', err)
      }
    },
    startNotificationPolling() {
      if (this.notificationPollingInterval) return
      this.notificationPollingInterval = setInterval(() => {
        this.fetchNotifications()
      }, 30000)
    },
    stopNotificationPolling() {
      if (this.notificationPollingInterval) {
        clearInterval(this.notificationPollingInterval)
        this.notificationPollingInterval = null
      }
    },
    async submitChangePassword() {
      if (this.changePasswordForm.newPassword !== this.changePasswordForm.confirmPassword) {
        this.changePasswordError = this.$t('nav.passwordMismatch')
        return
      }
      if (this.changePasswordForm.newPassword.length < 6) {
        this.changePasswordError = this.$t('nav.passwordTooShort')
        return
      }
      
      this.submittingChangePassword = true
      this.changePasswordError = null
      const userId = localStorage.getItem('user_id')
      try {
        await axios.patch(`/api/users/${userId}/`, {
          password: this.changePasswordForm.newPassword
        })
        
        // Relogin programmatically with the new password to update tokens
        const username = localStorage.getItem('username')
        const tokenRes = await axios.post('/api/token/', {
          username: username,
          password: this.changePasswordForm.newPassword
        })
        
        const { access, refresh } = tokenRes.data
        localStorage.setItem('auth_token', access)
        localStorage.setItem('refresh_token', refresh)
        axios.defaults.headers.common['Authorization'] = 'Bearer ' + access
        
        this.closeChangePasswordModal()
        alert(this.$t('nav.passwordChangeSuccess'))
      } catch (err) {
        console.error('Error changing password:', err)
        this.changePasswordError = this.$t('nav.passwordChangeError')
      } finally {
        this.submittingChangePassword = false
      }
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
  transition: width 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.5rem 1.75rem;
  border-bottom: 1px solid #1e293b;
  transition: all 0.2s ease;
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
  justify-content: space-between;
  padding: 0 2rem;
  box-sizing: border-box;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
}

.sidebar-toggle-btn {
  background: none;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  width: 38px;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.sidebar-toggle-btn:hover {
  color: #1e293b;
  background-color: #f1f5f9;
  border-color: #cbd5e1;
}

.toggle-icon {
  width: 20px;
  height: 20px;
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

/* Language Switcher */
.lang-switcher {
  display: flex;
  background-color: #f1f5f9;
  border-radius: 8px;
  padding: 0.2rem;
  border: 1px solid #e2e8f0;
  margin-right: 0.5rem;
}

.lang-btn {
  background: none;
  border: none;
  padding: 0.25rem 0.6rem;
  font-size: 0.8rem;
  font-weight: 600;
  border-radius: 6px;
  cursor: pointer;
  color: #64748b;
  transition: all 0.2s;
}

.lang-btn:hover {
  color: #1e293b;
}

.lang-btn.active {
  background-color: white;
  color: #6366f1;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* Collapsed Sidebar on Desktop */
@media (min-width: 769px) {
  #app.sidebar-collapsed .sidebar {
    width: 72px;
  }
  #app.sidebar-collapsed .brand-name,
  #app.sidebar-collapsed .nav-text {
    display: none;
  }
  #app.sidebar-collapsed .sidebar-brand {
    padding: 1.5rem 0.5rem;
    justify-content: center;
  }
  #app.sidebar-collapsed .nav-item {
    padding: 0.75rem;
    justify-content: center;
    gap: 0;
  }
}

/* Mobile Responsiveness Styles */
@media (max-width: 768px) {
  .dashboard-layout {
    position: relative;
  }
  
  .sidebar {
    position: fixed;
    top: 0;
    bottom: 0;
    left: 0;
    z-index: 10000;
    transform: translateX(-100%);
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 10px 0 15px -3px rgba(0, 0, 0, 0.1);
  }
  
  #app.drawer-open .sidebar {
    transform: translateX(0);
  }
  
  .sidebar-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-color: rgba(15, 23, 42, 0.4);
    backdrop-filter: blur(4px);
    z-index: 9999;
  }
  
  .top-header {
    padding: 0 1rem;
  }
  
  .logout-btn span {
    display: none;
  }
}

/* User Dropdown styles */
.user-dropdown-container {
  position: relative;
  display: inline-block;
}

.user-profile-trigger {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  background: transparent;
  border: none;
  cursor: pointer;
  color: #334155;
  font-family: inherit;
  transition: background-color 0.2s ease;
}

.user-profile-trigger:hover {
  background-color: #f1f5f9;
}

.user-profile-trigger .chevron {
  font-size: 0.7rem;
  color: #64748b;
  transition: transform 0.2s ease;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  min-width: 180px;
  z-index: 1000;
  padding: 0.5rem 0;
  animation: slideDown 0.15s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.6rem 1rem;
  font-size: 0.875rem;
  color: #334155;
  background: transparent;
  border: none;
  text-align: left;
  cursor: pointer;
  transition: background-color 0.15s ease, color 0.15s ease;
  box-sizing: border-box;
}

.dropdown-link:hover {
  background-color: #f8fafc;
  color: #6366f1;
}

.dropdown-link-icon {
  font-size: 1rem;
}

.logout-link {
  border-top: 1px solid #f1f5f9;
  margin-top: 0.25rem;
  padding-top: 0.5rem;
  color: #ef4444;
}

.logout-link:hover {
  background-color: #fef2f2;
  color: #dc2626;
}

/* Modal styling for Change Password */
.modal-backdrop-cp {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: fadeInModal 0.2s ease-out;
}

@keyframes fadeInModal {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content-cp {
  background-color: white;
  width: 100%;
  max-width: 400px;
  border-radius: 12px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  animation: scaleUpModal 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes scaleUpModal {
  from { transform: scale(0.95); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.modal-header-cp {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #f1f5f9;
}

.modal-title-cp {
  font-size: 1.125rem;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.modal-close-cp {
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 6px;
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close-cp:hover {
  background-color: #f1f5f9;
  color: #475569;
}

.icon-svg-cp {
  width: 20px;
  height: 20px;
}

.modal-body-cp {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.error-banner-cp {
  background-color: #fef2f2;
  border: 1px solid #fca5a5;
  color: #991b1b;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.85rem;
  text-align: left;
}

.form-group-cp {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  text-align: left;
}

.form-label-cp {
  font-size: 0.875rem;
  font-weight: 500;
  color: #475569;
}

.form-input-cp {
  padding: 0.6rem 0.75rem;
  font-size: 0.9rem;
  border-radius: 8px;
  border: 1px solid #cbd5e1;
  background-color: white;
  color: #1e293b;
  outline: none;
  transition: all 0.2s ease;
  width: 100%;
  box-sizing: border-box;
}

.form-input-cp:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.modal-footer-cp {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.25rem 1.5rem;
  border-top: 1px solid #f1f5f9;
  background-color: #f8fafc;
}

.btn-cp {
  padding: 0.55rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
  border: 1px solid transparent;
}

.btn-secondary-cp {
  background-color: white;
  border-color: #cbd5e1;
  color: #475569;
}

.btn-secondary-cp:hover {
  background-color: #f8fafc;
  border-color: #94a3b8;
}

.btn-primary-cp {
  background-color: #6366f1;
  color: white;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.btn-primary-cp:hover {
  background-color: #4f46e5;
}

.btn-primary-cp:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
