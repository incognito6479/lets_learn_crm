<template>
  <div class="login-container">
    <!-- Premium Aurora/Mesh Background Elements -->
    <div class="glow-bg">
      <div class="blob blob-purple"></div>
      <div class="blob blob-blue"></div>
      <div class="blob blob-pink"></div>
    </div>

    <!-- Glassmorphic Login Card -->
    <div class="login-card">
      <div class="card-header">
        <div class="logo-wrapper">
          <svg class="logo-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <h1 class="title">{{ $t('login.title') }}</h1>
        <p class="subtitle">{{ $t('login.sub') }}</p>

      </div>

      <!-- Login Form -->
      <form @submit.prevent="handleLogin" class="login-form">
        <!-- Error Banner -->
        <div v-if="error" class="error-banner" role="alert">
          <svg class="error-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <line x1="12" y1="8" x2="12" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <line x1="12" y1="16" x2="12.01" y2="16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <span>{{ error }}</span>
        </div>



        <!-- Username Field -->
        <div class="form-group">
          <label for="username" class="form-label">{{ $t('login.username') }}</label>
          <div class="input-wrapper">
            <svg class="input-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <input
              type="text"
              id="username"
              name="username"
              v-model="username"
              autocomplete="username"
              required
              :placeholder="$t('login.username')"
              class="form-input"
              ref="usernameInput"
            />
          </div>
        </div>

        <!-- Password Field -->
        <div class="form-group">
          <div class="label-row">
            <label for="current-password" class="form-label">{{ $t('login.password') }}</label>
            <a href="#" @click.prevent="forgotPassword" class="forgot-link">{{ $t('login.forgot') }}</a>
          </div>
          <div class="input-wrapper">
            <svg class="input-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M7 11V7C7 5.67392 7.52678 4.40215 8.46447 3.46447C9.40215 2.52678 10.6739 2 12 2C13.3261 2 14.5979 2.52678 15.5355 3.46447C16.4732 4.40215 17 5.67392 17 7V11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <input
              :type="showPassword ? 'text' : 'password'"
              id="current-password"
              name="password"
              v-model="password"
              autocomplete="current-password"
              required
              :placeholder="$t('login.password')"
              class="form-input password-input"
            />
            <button
              type="button"
              class="password-toggle"
              @click="showPassword = !showPassword"
              :aria-label="showPassword ? 'Hide password' : 'Show password'"
            >
              <svg v-if="showPassword" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="eye-icon">
                <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="1" y1="1" x2="23" y2="23" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="eye-icon">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- Remember Me Checkbox -->
        <div class="remember-me">
          <label class="checkbox-container">
            <input type="checkbox" v-model="rememberMe" />
            <span class="checkmark"></span>
            <span class="checkbox-label">{{ $t('login.remember') }}</span>
          </label>
        </div>

        <!-- Submit Button -->
        <button type="submit" class="submit-btn" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>{{ $t('login.signIn') }}</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Login',
  data() {
    return {
      username: '',
      password: '',
      showPassword: false,
      rememberMe: false,
      loading: false,
      error: null
    }
  },
  mounted() {
    // Auto-focus username input on page mount
    this.$refs.usernameInput?.focus()
  },
  methods: {
    async handleLogin() {
      this.loading = true
      this.error = null

      // Create Basic Auth Token: base64(username:password)
      const credentials = `${this.username}:${this.password}`
      const token = btoa(credentials)

      try {
        // Test auth credentials by requesting list of branches or users
        const response = await axios.get('http://localhost:8000/api/branches/', {
          headers: {
            'Authorization': `Basic ${token}`
          }
        })

        // Success: set temporary auth header to fetch user info
        axios.defaults.headers.common['Authorization'] = 'Basic ' + token

        // Fetch users to find the role and ID of the logged-in user
        const usersResponse = await axios.get('http://localhost:8000/api/users/')
        const currentUser = usersResponse.data.find(
          u => u.username.toLowerCase() === this.username.toLowerCase()
        )
        const role = currentUser ? currentUser.role : 'admin'
        const userId = currentUser ? currentUser.id : null

        // Store auth credentials and user metadata in localStorage
        localStorage.setItem('auth_token', token)
        localStorage.setItem('username', this.username)
        localStorage.setItem('user_role', role)
        if (userId) {
          localStorage.setItem('user_id', String(userId))
        }

        this.loading = false
        this.$router.push('/')
      } catch (err) {
        // Clear any half-set auth headers on login failure
        delete axios.defaults.headers.common['Authorization']
        this.loading = false
        if (err.response && err.response.status === 401) {
          this.error = this.$t('login.error')
        } else if (!err.response) {
          this.error = this.$t('login.server_error')
        } else {
          this.error = this.$t('login.unknown_error')
        }
      }
    },
    forgotPassword() {
      alert(this.$t('login.forgot_alert'))
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

.login-container {
  font-family: 'Outfit', sans-serif;
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: #0b0f19;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  z-index: 9999;
}

/* Premium aurora animated background blobs */
.glow-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  pointer-events: none;
}

.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.25;
  animation: float 20s infinite alternate;
}

.blob-purple {
  width: 500px;
  height: 500px;
  background: #6366f1;
  top: -10%;
  left: -10%;
  animation-duration: 25s;
}

.blob-blue {
  width: 600px;
  height: 600px;
  background: #3b82f6;
  bottom: -20%;
  right: -10%;
  animation-duration: 30s;
}

.blob-pink {
  width: 400px;
  height: 400px;
  background: #d946ef;
  top: 40%;
  left: 50%;
  animation-duration: 22s;
}

@keyframes float {
  0% {
    transform: translate(0px, 0px) scale(1);
  }
  50% {
    transform: translate(50px, 80px) scale(1.15);
  }
  100% {
    transform: translate(-30px, -50px) scale(0.9);
  }
}

/* Glassmorphic Login Card */
.login-card {
  width: 100%;
  max-width: 440px;
  padding: 3.5rem 2.5rem 3rem 2.5rem;
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4);
  position: relative;
  z-index: 10;
  box-sizing: border-box;
  animation: cardAppear 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes cardAppear {
  0% {
    opacity: 0;
    transform: translateY(30px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

.card-header {
  text-align: center;
  margin-bottom: 2.25rem;
}

.logo-wrapper {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #6366f1, #3b82f6);
  border-radius: 16px;
  color: white;
  margin-bottom: 1.25rem;
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.3);
}

.logo-icon {
  width: 32px;
  height: 32px;
}

.title {
  font-size: 2rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 0.5rem 0;
  letter-spacing: -0.5px;
}

.subtitle {
  font-size: 0.925rem;
  color: #94a3b8;
  margin: 0 0 1.5rem 0;
  line-height: 1.5;
}

/* Mode Selector Switch */
.mode-selector-container {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
}

.mode-selector {
  display: flex;
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.05);
  padding: 4px;
  border-radius: 9999px;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
}

.mode-btn {
  background: none;
  border: none;
  color: #64748b;
  padding: 0.4rem 1.15rem;
  border-radius: 9999px;
  font-size: 0.825rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.mode-btn.active {
  background-color: #6366f1;
  color: white;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.4);
}

/* Form Styles */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  text-align: left;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #cbd5e1;
}

.label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.forgot-link {
  font-size: 0.825rem;
  color: #6366f1;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.forgot-link:hover {
  color: #818cf8;
  text-decoration: underline;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 1rem;
  width: 20px;
  height: 20px;
  color: #64748b;
  pointer-events: none;
  transition: color 0.2s;
}

.form-input {
  width: 100%;
  padding: 0.875rem 1rem 0.875rem 2.75rem;
  background: rgba(30, 41, 59, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: white;
  font-size: 0.95rem;
  transition: all 0.2s ease-in-out;
  outline: none;
  box-sizing: border-box;
}

.form-input::placeholder {
  color: #475569;
}

.form-input:hover {
  border-color: rgba(255, 255, 255, 0.2);
  background: rgba(30, 41, 59, 0.6);
}

.form-input:focus {
  border-color: #6366f1;
  background: rgba(30, 41, 59, 0.8);
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.15);
}

.form-input:focus + .input-icon {
  color: #6366f1;
}

.password-input {
  padding-right: 2.75rem;
}

.password-toggle {
  position: absolute;
  right: 1rem;
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
}

.password-toggle:hover {
  color: #94a3b8;
}

.eye-icon {
  width: 20px;
  height: 20px;
}

/* Custom Autofill Styles */
.form-input:-webkit-autofill,
.form-input:-webkit-autofill:hover,
.form-input:-webkit-autofill:focus {
  -webkit-text-fill-color: #ffffff !important;
  -webkit-box-shadow: 0 0 0px 1000px #1e293b inset !important;
  box-shadow: 0 0 0px 1000px #1e293b inset !important;
  transition: background-color 5000s ease-in-out 0s;
  border: 1px solid rgba(99, 102, 241, 0.5) !important;
}

.form-input:autofill {
  border: 2px solid #6366f1;
  box-shadow: 0 0 0 1000px #1e293b inset;
}

/* Remember Me Checkbox */
.remember-me {
  display: flex;
  align-items: center;
}

.checkbox-container {
  display: flex;
  align-items: center;
  position: relative;
  padding-left: 2rem;
  cursor: pointer;
  user-select: none;
}

.checkbox-container input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.checkmark {
  position: absolute;
  left: 0;
  height: 20px;
  width: 20px;
  background-color: rgba(30, 41, 59, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  transition: all 0.2s;
}

.checkbox-container:hover input ~ .checkmark {
  border-color: rgba(255, 255, 255, 0.25);
  background-color: rgba(30, 41, 59, 0.6);
}

.checkbox-container input:checked ~ .checkmark {
  background-color: #6366f1;
  border-color: #6366f1;
}

.checkmark:after {
  content: "";
  position: absolute;
  display: none;
}

.checkbox-container input:checked ~ .checkmark:after {
  display: block;
}

.checkbox-container .checkmark:after {
  left: 7px;
  top: 3px;
  width: 5px;
  height: 10px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.checkbox-label {
  font-size: 0.875rem;
  color: #cbd5e1;
}

/* Banner Notifications */
.error-banner, .info-banner {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  border-radius: 12px;
  font-size: 0.85rem;
  text-align: left;
  line-height: 1.4;
}

.error-banner {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  color: #fca5a5;
}

.error-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  color: #ef4444;
}

.info-banner {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
  color: #93c5fd;
}

.info-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  color: #3b82f6;
}

/* Submit Button & Spinner */
.submit-btn {
  width: 100%;
  padding: 0.875rem;
  background: linear-gradient(135deg, #6366f1, #3b82f6);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease-in-out;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.2);
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.35);
  background: linear-gradient(135deg, #4f46e5, #2563eb);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(1px);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 480px) {
  .login-card {
    padding: 2.5rem 1.5rem 2rem 1.5rem;
    border-radius: 16px;
    border: none;
    background: rgba(15, 23, 42, 0.85);
  }
}
</style>
