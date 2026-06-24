<template>
  <div class="view-container">
    <div class="view-header">
      <div>
        <h1 class="view-title">{{ $t('branches.title') }}</h1>
        <p class="view-subtitle">{{ $t('branches.sub') }}</p>
      </div>
      <div style="display: flex; gap: 1rem; align-items: center;">
        <div class="badge-count" v-if="branches.length">{{ branches.length }} {{ $t('common.total') }}</div>
        <button @click="openCreateModal" class="btn btn-primary">
          <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          {{ $t('branches.new') }}
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
              <th>{{ $t('branches.col_name') }}</th>
              <th>{{ $t('common.description') }}</th>
              <th>{{ $t('common.status') }}</th>
              <th style="text-align: right;">{{ $t('common.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="branch in branches" :key="branch.id" class="table-row">
              <td class="font-mono text-muted">#{{ branch.id }}</td>
              <td class="font-semibold">{{ branch.name }}</td>
              <td>{{ branch.description || '-' }}</td>
              <td>
                <span class="status-badge active">{{ $t('teachers.active') }}</span>
              </td>
              <td class="actions-cell">
                <button @click="openEditModal(branch)" class="btn-icon" :title="$t('branches.modal_edit')">
                  <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 113 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                  </svg>
                </button>
                <button @click="deleteBranch(branch)" class="btn-icon btn-icon-danger" :title="$t('common.delete')">
                  <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"></path>
                    <line x1="10" y1="11" x2="10" y2="17"></line>
                    <line x1="14" y1="11" x2="14" y2="17"></line>
                  </svg>
                </button>
              </td>
            </tr>
            <tr v-if="!branches.length && !loading">
              <td colspan="5" class="empty-state">{{ $t('branches.no_branches') }}</td>
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
          <h2 class="modal-title">{{ isEdit ? $t('branches.modal_edit') : $t('branches.modal_new') }}</h2>
          <button @click="closeModal" class="modal-close">
            <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <form @submit.prevent="saveBranch">
          <div class="modal-body">
            <div class="form-group">
              <label for="branchName" class="form-label">{{ $t('branches.col_name') }}</label>
              <input
                type="text"
                id="branchName"
                v-model="form.name"
                required
                :placeholder="$t('branches.placeholder_name')"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label for="description" class="form-label">{{ $t('common.description') }}</label>
              <textarea
                id="description"
                v-model="form.description"
                :placeholder="$t('branches.placeholder_desc')"
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
  name: 'Branches',
  data() {
    return {
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
        description: ''
      }
    }
  },
  mounted() {
    this.fetchBranches()
  },
  methods: {
    async fetchBranches() {
      this.loading = true
      this.error = null

      try {
        const response = await axios.get('http://localhost:8000/api/branches/')
        this.branches = response.data
        this.loading = false
      } catch (err) {
        console.error('Error fetching branches:', err)
        this.error = this.$t('branches.error_load')
        this.loading = false
      }
    },
    openCreateModal() {
      this.isEdit = false
      this.form = { id: null, name: '', description: '' }
      this.showModal = true
    },
    openEditModal(branch) {
      this.isEdit = true
      this.form = { ...branch }
      this.showModal = true
    },
    closeModal() {
      this.showModal = false
    },
    async saveBranch() {
      this.submitting = true

      try {
        if (this.isEdit) {
          await axios.put(`http://localhost:8000/api/branches/${this.form.id}/`, this.form)
        } else {
          await axios.post('http://localhost:8000/api/branches/', this.form)
        }
        this.submitting = false
        this.closeModal()
        this.fetchBranches()
      } catch (err) {
        console.error('Error saving branch:', err)
        alert(this.$t('branches.error_save'))
        this.submitting = false
      }
    },
    async deleteBranch(branch) {
      if (!confirm(this.$t('branches.delete_confirm', { name: branch.name }))) {
        return
      }

      try {
        await axios.delete(`http://localhost:8000/api/branches/${branch.id}/`)
        this.fetchBranches()
      } catch (err) {
        console.error('Error deleting branch:', err)
        alert(this.$t('branches.error_delete'))
      }
    }
  }
}
</script>

<style scoped>
@import '../assets/views.css';
</style>
