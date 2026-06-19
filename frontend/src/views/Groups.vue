<template>
  <div class="view-container">
    <div class="view-header">
      <div>
        <h1 class="view-title">Groups</h1>
        <p class="view-subtitle">Monitor class schedules and current groups</p>
      </div>
      <div style="display: flex; gap: 1rem; align-items: center;">
        <div class="badge-count" v-if="groups.length">{{ groups.length }} groups</div>
        <button @click="openCreateModal" class="btn btn-primary">
          <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          New Group
        </button>
      </div>
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
          placeholder="Search groups by name..."
          class="form-input"
        />
      </div>
      
      <div style="width: 200px;">
        <select v-model="selectedBranch" class="form-input">
          <option value="">All Branches</option>
          <option v-for="branch in branches" :key="branch.id" :value="branch.id">
            {{ branch.name }}
          </option>
        </select>
      </div>

      <div style="width: 200px;">
        <select v-model="selectedCourse" class="form-input">
          <option value="">All Courses</option>
          <option v-for="course in courses" :key="course.id" :value="course.id">
            {{ course.name }}
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
              <th>Group Name</th>
              <th>Course</th>
              <th>Teacher</th>
              <th>Location (Room)</th>
              <th>Branch</th>
              <th>Status</th>
              <th>Schedule</th>
              <th>Duration</th>
              <th style="text-align: right;">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="group in filteredGroups" :key="group.id" class="table-row clickable-row" @click="navigateToGroup(group.id)">
              <td class="font-mono text-muted">#{{ group.id }}</td>
              <td class="font-semibold">{{ group.name }}</td>
              <td>{{ getCourseName(group.course) }}</td>
              <td>{{ getTeacherName(group.teacher) }}</td>
              <td>{{ getRoomName(group.room) }}</td>
              <td>{{ getBranchName(group.branch) }}</td>
              <td>
                <span :class="['status-badge', group.status || 'enrolled']">
                  {{ group.status || 'enrolled' }}
                </span>
              </td>
              <td>
                <div class="schedule-cell">
                  <div class="starts-time">{{ formatTime(group.starts_at) }}</div>
                  <div class="started-date text-muted">Since {{ formatDate(group.started_at) }}</div>
                </div>
              </td>
              <td class="font-mono">{{ group.duration }} mins</td>
              <td class="actions-cell">
                <button @click.stop="navigateToGroup(group.id)" class="btn-icon" title="View Group Details">
                  <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                  </svg>
                </button>
                <button @click.stop="openEditModal(group)" class="btn-icon" title="Edit Group">
                  <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 113 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                  </svg>
                </button>
                <button @click.stop="deleteGroup(group)" class="btn-icon btn-icon-danger" title="Delete Group">
                  <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"></path>
                    <line x1="10" y1="11" x2="10" y2="17"></line>
                    <line x1="14" y1="11" x2="14" y2="17"></line>
                  </svg>
                </button>
              </td>
            </tr>
            <tr v-if="!filteredGroups.length && !loading">
              <td colspan="10" class="empty-state">No groups found.</td>
            </tr>
            <tr v-if="loading">
              <td colspan="10" class="loading-state">
                <div class="spinner"></div>
                <span>Loading groups...</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showModal" class="modal-backdrop" @click.self="closeModal">
      <div class="modal-content" style="max-width: 540px;">
        <div class="modal-header">
          <h2 class="modal-title">{{ isEdit ? 'Edit Group' : 'Add Group' }}</h2>
          <button @click="closeModal" class="modal-close">
            <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <form @submit.prevent="saveGroup">
          <div class="modal-body">
            <div class="form-group">
              <label for="groupName" class="form-label">Group Name</label>
              <input
                type="text"
                id="groupName"
                v-model="form.name"
                required
                placeholder="e.g. Phys-101 Morning"
                class="form-input"
              />
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
              <div class="form-group">
                <label for="groupBranch" class="form-label">Branch</label>
                <select id="groupBranch" v-model="form.branch" required class="form-input">
                  <option value="" disabled>Select Branch...</option>
                  <option v-for="branch in branches" :key="branch.id" :value="branch.id">
                    {{ branch.name }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label for="groupRoom" class="form-label">Room</label>
                <select id="groupRoom" v-model="form.room" required class="form-input" :disabled="!form.branch">
                  <option value="" disabled>{{ form.branch ? 'Select Room...' : 'Select branch first...' }}</option>
                  <option v-for="room in filteredRooms" :key="room.id" :value="room.id">
                    {{ room.name }}
                  </option>
                </select>
              </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
              <div class="form-group">
                <label for="groupCourse" class="form-label">Course</label>
                <select id="groupCourse" v-model="form.course" required class="form-input">
                  <option value="" disabled>Select Course...</option>
                  <option v-for="course in courses" :key="course.id" :value="course.id">
                    {{ course.name }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label for="groupTeacher" class="form-label">Teacher</label>
                <select id="groupTeacher" v-model="form.teacher" required class="form-input">
                  <option value="" disabled>Select Teacher...</option>
                  <option v-for="teacher in teachers" :key="teacher.id" :value="teacher.id">
                    {{ teacher.first_name }} {{ teacher.last_name }}
                  </option>
                </select>
              </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
              <div class="form-group">
                <label for="startedAt" class="form-label">Start Date</label>
                <input
                  type="date"
                  id="startedAt"
                  v-model="form.started_at"
                  required
                  class="form-input"
                />
              </div>

              <div class="form-group">
                <label for="startsAt" class="form-label">Start Time</label>
                <input
                  type="time"
                  id="startsAt"
                  v-model="form.starts_at"
                  required
                  class="form-input"
                />
              </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
              <div class="form-group">
                <label for="duration" class="form-label">Duration (Minutes)</label>
                <input
                  type="number"
                  id="duration"
                  v-model.number="form.duration"
                  required
                  min="1"
                  placeholder="e.g. 90"
                  class="form-input"
                />
              </div>

              <div class="form-group">
                <label for="groupStatus" class="form-label">Status</label>
                <select id="groupStatus" v-model="form.status" required class="form-input">
                  <option value="ongoing">Ongoing</option>
                  <option value="finished">Finished</option>
                  <option value="enrolled">Enrolled</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label for="description" class="form-label">Description (Optional)</label>
              <textarea
                id="description"
                v-model="form.description"
                placeholder="Details about group, target exam..."
                class="form-input"
                rows="3"
                style="resize: vertical; font-family: inherit;"
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="submitting">
              {{ submitting ? 'Saving...' : 'Save Changes' }}
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
  name: 'Groups',
  data() {
    return {
      groups: [],
      courses: [],
      teachers: [],
      rooms: [],
      branches: [],
      loading: false,
      error: null,

      // Search and Filter controls
      searchQuery: '',
      selectedBranch: '',
      selectedCourse: '',

      // Modal controls
      showModal: false,
      isEdit: false,
      submitting: false,
      form: {
        id: null,
        name: '',
        branch: '',
        course: '',
        teacher: '',
        room: '',
        started_at: '',
        starts_at: '',
        duration: 90,
        status: 'ongoing',
        description: ''
      }
    }
  },
  computed: {
    filteredGroups() {
      let list = this.groups
      
      // Filter by search query (group name)
      const query = this.searchQuery.toLowerCase().trim()
      if (query) {
        list = list.filter(g => g.name && g.name.toLowerCase().includes(query))
      }
      
      // Filter by selected branch
      if (this.selectedBranch) {
        list = list.filter(g => g.branch === this.selectedBranch)
      }
      
      // Filter by selected course
      if (this.selectedCourse) {
        list = list.filter(g => g.course === this.selectedCourse)
      }
      
      return list
    },
    filteredRooms() {
      if (!this.form.branch) return []
      return this.rooms.filter(r => r.branch === this.form.branch)
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
        const [groupsRes, coursesRes, usersRes, roomsRes, branchesRes] = await Promise.all([
          axios.get('http://localhost:8000/api/groups/'),
          axios.get('http://localhost:8000/api/courses/'),
          axios.get('http://localhost:8000/api/users/'),
          axios.get('http://localhost:8000/api/rooms/'),
          axios.get('http://localhost:8000/api/branches/')
        ])
        
        this.groups = groupsRes.data
        this.courses = coursesRes.data
        this.teachers = usersRes.data.filter(u => u.role === 'teacher')
        this.rooms = roomsRes.data
        this.branches = branchesRes.data
      } catch (err) {
        console.error('Error fetching groups data:', err)
        this.error = 'Unable to connect to backend API. Please check server status.'
      } finally {
        this.loading = false
      }
    },
    getCourseName(id) {
      const item = this.courses.find(c => c.id === id)
      return item ? item.name : `Course #${id}`
    },
    getTeacherName(id) {
      const item = this.teachers.find(t => t.id === id)
      return item ? `${item.first_name} ${item.last_name}` : `Teacher #${id}`
    },
    getRoomName(id) {
      const item = this.rooms.find(r => r.id === id)
      return item ? item.name : `Room #${id}`
    },
    getBranchName(id) {
      const item = this.branches.find(b => b.id === id)
      return item ? item.name : `Branch #${id}`
    },
    formatTime(timeStr) {
      if (!timeStr) return '-'
      const parts = timeStr.split(':')
      if (parts.length >= 2) {
        return `${parts[0]}:${parts[1]}`
      }
      return timeStr
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      try {
        const date = new Date(dateStr)
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
      } catch (e) {
        return dateStr
      }
    },
    openCreateModal() {
      this.isEdit = false
      this.form = {
        id: null,
        name: '',
        branch: '',
        course: '',
        teacher: '',
        room: '',
        started_at: '',
        starts_at: '',
        duration: 90,
        status: 'ongoing',
        description: ''
      }
      this.showModal = true
    },
    openEditModal(group) {
      this.isEdit = true
      this.form = {
        id: group.id,
        name: group.name,
        branch: group.branch,
        course: group.course,
        teacher: group.teacher,
        room: group.room,
        started_at: group.started_at,
        starts_at: group.starts_at ? group.starts_at.slice(0, 5) : '',
        duration: group.duration,
        status: group.status || 'ongoing',
        description: group.description || ''
      }
      this.showModal = true
    },
    closeModal() {
      this.showModal = false
    },
    async saveGroup() {
      this.submitting = true
      try {
        if (this.isEdit) {
          await axios.put(`http://localhost:8000/api/groups/${this.form.id}/`, this.form)
          this.closeModal()
          this.fetchData()
        } else {
          const response = await axios.post('http://localhost:8000/api/groups/', this.form)
          this.closeModal()
          const newGroupId = response.data.id
          this.$router.push(`/groups/${newGroupId}`)
        }
      } catch (err) {
        console.error('Error saving group:', err)
        alert('An error occurred while saving the group record.')
      } finally {
        this.submitting = false
      }
    },
    async deleteGroup(group) {
      if (!confirm(`Are you sure you want to delete group "${group.name}"?`)) {
        return
      }
      try {
        await axios.delete(`http://localhost:8000/api/groups/${group.id}/`)
        this.fetchData()
      } catch (err) {
        console.error('Error deleting group:', err)
        alert('An error occurred while deleting the group record.')
      }
    },
    navigateToGroup(id) {
      this.$router.push(`/groups/${id}`)
    }
  }
}
</script>

<style scoped>
@import '../assets/views.css';

.schedule-cell {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.starts-time {
  font-weight: 600;
  color: #0f172a;
}

.started-date {
  font-size: 0.8rem;
}

.clickable-row {
  cursor: pointer;
}

.group-link {
  color: #4f46e5;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.15s;
}

.group-link:hover {
  color: #3730a3;
  text-decoration: underline;
}

.status-badge.ongoing {
  background-color: #e0f2fe;
  color: #0369a1;
}

.status-badge.enrolled {
  background-color: #dcfce7;
  color: #15803d;
}

.status-badge.finished {
  background-color: #f1f5f9;
  color: #475569;
}
</style>
