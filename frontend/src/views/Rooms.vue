<template>
  <div class="view-container">
    <div class="view-header">
      <div>
        <h1 class="view-title">{{ $t('rooms.title') }}</h1>
        <p class="view-subtitle">{{ $t('rooms.sub') }}</p>
      </div>
      <div style="display: flex; gap: 1rem; align-items: center;">
        <div class="badge-count" v-if="rooms.length">{{ rooms.length }} {{ $t('common.total') }}</div>
        <button @click="openCreateModal" class="btn btn-primary">
          <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          {{ $t('rooms.new') }}
        </button>
      </div>
    </div>

    <!-- Error/Warning Banner -->
    <div v-if="error" class="info-banner">
      <span>{{ error }}</span>
    </div>

    <!-- Data Table Container -->
    <div class="table-card">
      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>{{ $t('rooms.col_name') }}</th>
              <th>{{ $t('groups.col_branch') }}</th>
              <th>{{ $t('common.description') }}</th>
              <th style="text-align: right;">{{ $t('common.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="room in rooms" :key="room.id" class="table-row">
              <td class="font-mono text-muted">#{{ room.id }}</td>
              <td class="font-semibold">{{ room.name }}</td>
              <td>{{ getBranchName(room.branch) }}</td>
              <td>{{ room.description || '-' }}</td>
              <td class="actions-cell">
                <button @click="openEditModal(room)" class="btn-icon" :title="$t('rooms.modal_edit')">
                  <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 113 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                  </svg>
                </button>
                <button @click="deleteRoom(room)" class="btn-icon btn-icon-danger" :title="$t('common.delete')">
                  <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"></path>
                    <line x1="10" y1="11" x2="10" y2="17"></line>
                    <line x1="14" y1="11" x2="14" y2="17"></line>
                  </svg>
                </button>
              </td>
            </tr>
            <tr v-if="!rooms.length && !loading">
              <td colspan="5" class="empty-state">{{ $t('rooms.no_rooms') }}</td>
            </tr>
            <tr v-if="loading">
              <td colspan="5" class="loading-state">
                <div class="spinner"></div>
                <span>{{ $t('common.loading') }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showModal" class="modal-backdrop" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2 class="modal-title">{{ isEdit ? $t('rooms.modal_edit') : $t('rooms.modal_new') }}</h2>
          <button @click="closeModal" class="modal-close">
            <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <form @submit.prevent="saveRoom">
          <div class="modal-body">
            <div class="form-group">
              <label for="roomName" class="form-label">{{ $t('rooms.col_name') }}</label>
              <input
                type="text"
                id="roomName"
                v-model="form.name"
                required
                :placeholder="$t('rooms.placeholder_name')"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label for="roomBranch" class="form-label">{{ $t('groups.col_branch') }}</label>
              <select id="roomBranch" v-model="form.branch" required class="form-input">
                <option value="" disabled>{{ $t('rooms.select_branch') }}</option>
                <option v-for="branch in branches" :key="branch.id" :value="branch.id">
                  {{ branch.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label for="description" class="form-label">{{ $t('common.description') }}</label>
              <textarea
                id="description"
                v-model="form.description"
                :placeholder="$t('rooms.placeholder_desc')"
                class="form-input"
                rows="3"
                style="resize: vertical; font-family: inherit;"
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" @click="closeModal" class="btn btn-secondary">{{ $t('common.cancel') }}</button>
            <button type="submit" class="btn btn-primary" :disabled="submitting">
              {{ submitting ? $t('common.loading') : $t('common.save') }}
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
  name: 'Rooms',
  data() {
    return {
      rooms: [],
      branches: [],
      loading: false,
      error: null,

      // Modal controls
      showModal: false,
      isEdit: false,
      submitting: false,
      form: {
        id: null,
        name: '',
        branch: '',
        description: ''
      }
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
        const [roomsRes, branchesRes] = await Promise.all([
          axios.get('http://localhost:8000/api/rooms/'),
          axios.get('http://localhost:8000/api/branches/')
        ])
        this.rooms = roomsRes.data
        this.branches = branchesRes.data
        this.loading = false
      } catch (err) {
        console.error('Error fetching data:', err)
        this.error = this.$t('rooms.error_load')
        this.loading = false
      }
    },
    openCreateModal() {
      this.isEdit = false
      this.form = { id: null, name: '', branch: '', description: '' }
      this.showModal = true
    },
    openEditModal(room) {
      this.isEdit = true
      this.form = { ...room }
      this.showModal = true
    },
    closeModal() {
      this.showModal = false
    },
    async saveRoom() {
      this.submitting = true

      try {
        if (this.isEdit) {
          await axios.put(`http://localhost:8000/api/rooms/${this.form.id}/`, this.form)
        } else {
          await axios.post('http://localhost:8000/api/rooms/', this.form)
        }
        this.submitting = false
        this.closeModal()
        this.fetchData()
      } catch (err) {
        console.error('Error saving room:', err)
        alert(this.$t('rooms.error_save'))
        this.submitting = false
      }
    },
    async deleteRoom(room) {
      if (!confirm(this.$t('rooms.delete_confirm', { name: room.name }))) {
        return
      }

      try {
        await axios.delete(`http://localhost:8000/api/rooms/${room.id}/`)
        this.fetchData()
      } catch (err) {
        console.error('Error deleting room:', err)
        alert(this.$t('rooms.error_delete'))
      }
    },
    getBranchName(branchId) {
      if (!branchId) return '-'
      const branch = this.branches.find(b => b.id === branchId)
      return branch ? branch.name : `Branch #${branchId}`
    }
  }
}
</script>

<style scoped>
@import '../assets/views.css';
</style>
