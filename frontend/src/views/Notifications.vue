<template>
  <div class="notifications-view-container">
    <div class="page-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
      <div>
        <h1 class="page-title">{{ $t('notifications.title') || 'Notifications' }}</h1>
        <p class="page-subtitle" style="color: #64748b; font-size: 0.875rem; margin-top: 0.25rem;">
          {{ $t('notifications.subtitle') }}
        </p>
      </div>
      <button 
        @click="markAllAsRead" 
        v-if="hasUnread" 
        class="btn btn-secondary"
        style="display: flex; align-items: center; gap: 0.5rem; padding: 0.625rem 1.25rem; font-size: 0.95rem; font-weight: 600;"
      >
        ✓ {{ $t('common.markAllRead') || 'Mark all read' }}
      </button>
    </div>

    <div v-if="loading" class="loading-state" style="padding: 3rem; text-align: center; color: #64748b;">
      {{ $t('common.loading') || 'Loading...' }}
    </div>

    <div v-else-if="notifications.length === 0" class="card empty-state" style="padding: 4rem 2rem; text-align: center; display: flex; flex-direction: column; align-items: center; gap: 1.25rem; border-radius: 12px; background-color: white; border: 1px solid #e2e8f0;">
      <!-- Premium SVG bell icon for empty state -->
      <div style="width: 80px; height: 80px; border-radius: 50%; display: flex; align-items: center; justify-content: center; background-color: #f8fafc; border: 1px solid #f1f5f9; color: #94a3b8;">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="width: 40px; height: 40px;">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
          <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
        </svg>
      </div>
      <h2 style="font-size: 1.25rem; font-weight: 600; color: #334155;">{{ $t('common.noNotifications') || 'No notifications' }}</h2>
      <p style="color: #64748b; max-width: 350px; font-size: 0.875rem; line-height: 1.5; margin: 0;">
        {{ $t('notifications.empty_desc') }}
      </p>
    </div>

    <div v-else class="notifications-list" style="display: flex; flex-direction: column; gap: 1rem;">
      <div 
        v-for="notif in sortedNotifications" 
        :key="notif.id" 
        class="card notification-card-item"
        style="padding: 1.25rem; display: flex; gap: 1rem; position: relative; transition: all 0.2s; border-radius: 10px; background-color: white; border: 1px solid #e2e8f0; border-left-width: 4px;"
        :style="getCardStyle(notif)"
      >
        <!-- Icon/Indicator — color-coded SVG Bell icon -->
        <div class="notif-icon-wrapper" style="width: 42px; height: 42px; border-radius: 50%; display: flex; align-items: center; justify-content: center; background-color: #f8fafc; border: 1px solid #f1f5f9; flex-shrink: 0;">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 20px; height: 20px;" :style="getIconStyle(notif)">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
            <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
          </svg>
        </div>

        <!-- Content -->
        <div class="notif-details" style="flex: 1; min-width: 0; padding-right: 9rem;">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; margin-bottom: 0.35rem;">
            <h3 class="notif-item-title" style="font-size: 1rem; margin: 0; color: #1e293b;" :style="{ fontWeight: notif.is_read ? '600' : '800' }">
              {{ getLocalizedTitle(notif) }}
            </h3>
            <span style="font-size: 0.75rem; color: #94a3b8; white-space: nowrap;">
              {{ formatTime(notif.created_at) }}
            </span>
          </div>
          <p style="font-size: 0.9rem; color: #475569; line-height: 1.5; margin: 0 0 0.5rem 0; white-space: pre-wrap;">
            {{ getLocalizedMessage(notif) }}
          </p>

          <!-- Actions -->
          <div v-if="notif.notification_type === 'payment_pending' && !isPayoutAccepted(notif)" style="margin-top: 0.75rem; display: flex; gap: 0.5rem; align-items: center;">
            <button 
              @click="confirmPayout(notif)" 
              class="btn btn-primary" 
              style="padding: 0.4rem 1rem; font-size: 0.825rem; display: inline-flex; align-items: center; gap: 0.35rem; font-family: inherit;"
              :disabled="confirmingId === notif.id"
            >
              <span v-if="confirmingId === notif.id">⏳ Processing...</span>
              <span v-else>✓ {{ $t('common.confirmReceipt') || 'Confirm Receipt' }}</span>
            </button>
          </div>
        </div>

        <!-- Unread Badge dot / Mark single read -->
        <div style="position: absolute; right: 1.25rem; top: 1.25rem; display: flex; flex-direction: column; align-items: flex-end; gap: 1rem;">
          <div 
            v-if="!notif.is_read" 
            class="unread-dot"
            style="width: 10px; height: 10px; border-radius: 50%; background-color: #ef4444;"
          ></div>
          <button 
            v-if="!notif.is_read" 
            @click="markAsRead(notif)"
            class="mark-read-link"
            style="background: none; border: none; color: #6366f1; font-size: 0.75rem; font-weight: 600; cursor: pointer; padding: 0.25rem; transition: color 0.15s;"
          >
            {{ $t('notifications.mark_read') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Notifications',
  data() {
    return {
      notifications: [],
      loading: true,
      confirmingId: null
    }
  },
  computed: {
    currentLang() {
      return this.$i18n.locale
    },
    hasUnread() {
      return this.notifications.some(n => !n.is_read)
    },
    sortedNotifications() {
      // Sort unread notifications first, then by date descending
      return [...this.notifications].sort((a, b) => {
        if (a.is_read !== b.is_read) {
          return a.is_read ? 1 : -1
        }
        return new Date(b.created_at) - new Date(a.created_at)
      })
    }
  },
  async created() {
    await this.fetchNotifications()
    this.$emit('refresh-badge')
  },
  methods: {
    async fetchNotifications() {
      this.loading = true
      try {
        const res = await axios.get('/api/notifications/')
        this.notifications = res.data
      } catch (err) {
        console.error('Error fetching notifications:', err)
      } finally {
        this.loading = false
      }
    },
    isPayoutAccepted(notif) {
      return notif.title && notif.title.includes('Payout Confirmed')
    },
    getCardStyle(notif) {
      if (!notif.is_read) {
        const colorMap = {
          absence: '#f97316',
          payment_pending: '#f59e0b',
          payment_accepted: '#10b981'
        }
        return {
          borderLeftColor: colorMap[notif.notification_type] || '#6366f1',
          backgroundColor: '#fafcfe'
        }
      }
      return {
        borderLeftColor: '#e2e8f0',
        backgroundColor: '#ffffff'
      }
    },
    getIconStyle(notif) {
      let type = notif.notification_type
      if (type === 'payment_pending' && this.isPayoutAccepted(notif)) {
        type = 'payment_accepted'
      }
      const colorMap = {
        absence: '#f97316',
        payment_pending: '#f59e0b',
        payment_accepted: '#10b981'
      }
      return {
        color: colorMap[type] || '#6366f1'
      }
    },
    getLocalizedTitle(notif) {
      const match = notif.title.match(/#(\d+)/)
      const suffix = match ? ` #${match[1]}` : ''
      if (notif.notification_type === 'absence') {
        return this.$t('notifications.absence_title') + suffix
      } else if (notif.notification_type === 'payment_pending') {
        if (this.isPayoutAccepted(notif)) {
          return this.$t('notifications.payment_accepted_title') + suffix
        }
        return this.$t('notifications.payment_pending_title') + suffix
      } else if (notif.notification_type === 'payment_accepted') {
        return this.$t('notifications.payment_accepted_title') + suffix
      }
      return notif.title
    },
    getLocalizedMessage(notif) {
      if (notif.notification_type === 'absence') {
        // e.g. "Student Jane Doe was marked absent in group Physics by teacher Mr. Smith."
        const match = notif.message.match(/Student (.*?) was marked absent in group (.*?) by teacher (.*?)\./)
        if (match) {
          return this.$t('notifications.absence_msg', {
            student: match[1],
            group: match[2],
            teacher: match[3]
          })
        }
      } else if (notif.notification_type === 'payment_pending') {
        // e.g. "Admin registered a payout of 150000.00 UZS for group Physics. Please confirm receipt."
        const match = notif.message.match(/Admin registered a payout of (.*?) UZS for group (.*?)\. Please confirm receipt\./)
        if (match) {
          return this.$t('notifications.payment_pending_msg', {
            amount: this.formatMoney(match[1]),
            group: match[2]
          })
        }
      } else if (notif.notification_type === 'payment_accepted') {
        // e.g. "Teacher Mr. Smith confirmed receipt of 150000.00 UZS for group Physics."
        const match = notif.message.match(/Teacher (.*?) confirmed receipt of (.*?) UZS for group (.*?)\./)
        if (match) {
          return this.$t('notifications.payment_accepted_msg', {
            teacher: match[1],
            amount: this.formatMoney(match[2]),
            group: match[3]
          })
        }
      }
      return notif.message
    },
    formatMoney(amountStr) {
      if (!amountStr) return ''
      const num = Math.round(parseFloat(amountStr))
      if (isNaN(num)) return amountStr
      return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
    },
    formatTime(dateStr) {
      if (!dateStr) return ''
      const d = new Date(dateStr)
      return d.toLocaleString()
    },
    async markAsRead(notif) {
      if (notif.is_read) return
      try {
        await axios.post(`/api/notifications/${notif.id}/read/`)
        notif.is_read = true
        window.dispatchEvent(new CustomEvent('update-unread-badge'))
      } catch (err) {
        console.error('Error marking read:', err)
      }
    },
    async markAllAsRead() {
      try {
        for (const notif of this.notifications) {
          if (!notif.is_read) {
            await axios.post(`/api/notifications/${notif.id}/read/`)
            notif.is_read = true
          }
        }
        window.dispatchEvent(new CustomEvent('update-unread-badge'))
      } catch (err) {
        console.error('Error marking all read:', err)
      }
    },
    async confirmPayout(notif) {
      const match = notif.title.match(/#(\d+)/)
      if (!match) return
      const paymentId = match[1]
      this.confirmingId = notif.id
      try {
        await axios.post(`/api/payments/${paymentId}/confirm/`)
        alert(this.$t('notifications.payout_confirm_success'))
        if (!notif.is_read) {
          await axios.post(`/api/notifications/${notif.id}/read/`)
          notif.is_read = true
        }
        window.dispatchEvent(new CustomEvent('update-unread-badge'))
        await this.fetchNotifications()
      } catch (err) {
        console.error('Error confirming payout:', err)
        alert(this.$t('notifications.payout_confirm_error'))
      } finally {
        this.confirmingId = null
      }
    }
  }
}
</script>

<style scoped>
.notifications-view-container {
  max-width: 100%;
  margin: 0 auto;
  padding: 1rem 0;
}

.notification-card-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
}

.mark-read-link:hover {
  color: #4f46e5 !important;
  text-decoration: underline;
}
</style>
