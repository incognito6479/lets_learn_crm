<template>
  <div class="view-container">
    <!-- Breadcrumb Header -->
    <div class="breadcrumb-header">
      <router-link to="/groups" class="btn btn-secondary back-btn">
        <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="19" y1="12" x2="5" y2="12"></line>
          <polyline points="12 19 5 12 12 5"></polyline>
        </svg>
        Back to Groups
      </router-link>
    </div>

    <!-- View Header -->
    <div class="view-header" style="margin-top: 1rem;">
      <div>
        <h1 class="view-title">{{ group ? group.name : 'Loading Group...' }}</h1>
        <p class="view-subtitle">Detailed information and enrolled students roster</p>
      </div>
      <div v-if="group" style="display: flex; gap: 1rem; align-items: center;">
        <span :class="['status-badge', group.status || 'enrolled']" style="font-size: 0.95rem; padding: 0.4rem 1rem;">
          {{ group.status || 'enrolled' }}
        </span>
      </div>
    </div>

    <!-- Error/Warning Banner -->
    <div v-if="error" class="info-banner">
      <span>{{ error }}</span>
    </div>

    <!-- Layout Grid -->
    <div class="detail-grid" v-if="group">
      <!-- Left Main Column: Students Roster -->
      <div class="main-column">
        <div class="table-card">
          <div class="table-header-bar">
            <h2 class="card-section-title">Enrolled Students</h2>
            <button @click="openEnrollModal" class="btn btn-primary btn-sm">
              <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              Enroll a Student
            </button>
          </div>
          <div class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Full Name</th>
                  <th>Primary Phone</th>
                  <th>Enrollment Status</th>
                  <th>Enrollment Date</th>
                  <th style="text-align: right;">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="enrolled in enrolledStudents" :key="enrolled.enrollmentId" class="table-row">
                  <td class="font-mono text-muted">#{{ enrolled.id }}</td>
                  <td class="font-semibold">{{ enrolled.full_name }}</td>
                  <td>{{ enrolled.phone1 }}</td>
                  <td>
                    <span :class="['status-badge', enrolled.status || 'enrolled']">
                      {{ enrolled.status || 'enrolled' }}
                    </span>
                  </td>
                  <td>{{ formatDate(enrolled.date) }}</td>
                  <td class="actions-cell">
                    <button @click="unenrollStudent(enrolled)" class="btn-icon btn-icon-danger" title="Unenroll Student">
                      <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"></path>
                        <line x1="10" y1="11" x2="10" y2="17"></line>
                        <line x1="14" y1="11" x2="14" y2="17"></line>
                      </svg>
                    </button>
                  </td>
                </tr>
                <tr v-if="!enrolledStudents.length">
                  <td colspan="6" class="empty-state">No students currently enrolled in this group.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Right Side Column: Group Metadata -->
      <div class="sidebar-column">
        <div class="info-card">
          <h3 class="info-card-title">Group Details</h3>
          <div class="info-details-list">
            <div class="info-item">
              <span class="info-label">Course</span>
              <span class="info-value font-semibold">{{ getCourseName(group.course) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Teacher</span>
              <span class="info-value">{{ getTeacherName(group.teacher) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Location (Room)</span>
              <span class="info-value">{{ getRoomName(group.room) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Campus Branch</span>
              <span class="info-value">{{ getBranchName(group.branch) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Start Date</span>
              <span class="info-value">{{ formatDate(group.started_at) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Schedule Time</span>
              <span class="info-value font-mono">{{ formatTime(group.starts_at) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Duration</span>
              <span class="info-value">{{ group.duration }} minutes</span>
            </div>
          </div>
          <div class="info-description-box" v-if="group.description">
            <span class="info-label" style="display: block; margin-bottom: 0.4rem;">Description</span>
            <p class="description-text">{{ group.description }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading Screen fallback -->
    <div v-if="loading && !group" class="loading-state-fullscreen">
      <div class="spinner"></div>
      <span>Loading group details...</span>
    </div>

    <!-- Enroll Students Modal -->
    <div v-if="showEnrollModal" class="modal-backdrop" @click.self="closeEnrollModal">
      <div class="modal-content" style="max-width: 500px;">
        <div class="modal-header">
          <h2 class="modal-title">Enroll Students</h2>
          <button @click="closeEnrollModal" class="modal-close">
            <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <p class="modal-instructions">Select one or more students to enroll into <strong>{{ group.name }}</strong>.</p>
          
          <!-- Search box -->
          <div class="search-bar-container" style="margin-bottom: 0.75rem;">
            <input
              type="text"
              v-model="enrollSearchQuery"
              placeholder="Search students by name..."
              class="form-input"
              style="padding: 0.55rem 0.75rem; font-size: 0.875rem;"
            />
          </div>

          <!-- Students checklist container -->
          <div class="checklist-wrapper">
            <div v-for="student in availableStudents" :key="student.id" class="checklist-item">
              <label class="checklist-label">
                <input
                  type="checkbox"
                  v-model="selectedStudentIds"
                  :value="student.id"
                  class="checkbox-input"
                />
                <div class="checklist-student-details">
                  <span class="checklist-student-name">{{ student.full_name }}</span>
                  <span class="checklist-student-phone">{{ student.phone1 }}</span>
                </div>
              </label>
            </div>
            <div v-if="!availableStudents.length" class="empty-state" style="padding: 2rem 1rem;">
              No available students to enroll.
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" @click="closeEnrollModal" class="btn btn-secondary">Cancel</button>
          <button
            type="button"
            @click="enrollSelectedStudents"
            class="btn btn-primary"
            :disabled="submittingEnrollment || !selectedStudentIds.length"
          >
            {{ submittingEnrollment ? 'Enrolling...' : `Enroll Selected (${selectedStudentIds.length})` }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'GroupDetail',
  data() {
    return {
      group: null,
      courses: [],
      teachers: [],
      rooms: [],
      branches: [],
      students: [],
      enrollments: [],
      loading: false,
      error: null,

      // Enrollment modal state
      showEnrollModal: false,
      enrollSearchQuery: '',
      selectedStudentIds: [],
      submittingEnrollment: false
    }
  },
  computed: {
    enrolledStudents() {
      if (!this.group || !this.students.length || !this.enrollments.length) return []
      // Filter active enrollments for this group
      const groupEnrollments = this.enrollments.filter(e => e.group === this.group.id)
      return groupEnrollments.map(e => {
        const studentInfo = this.students.find(s => s.id === e.student)
        return {
          enrollmentId: e.id,
          status: e.status,
          date: e.date,
          studentId: e.student,
          ...studentInfo
        }
      }).filter(item => item.full_name)
    },
    availableStudents() {
      if (!this.students.length) return []
      const enrolledIds = this.enrolledStudents.map(e => e.studentId)
      
      // Filter out students already enrolled
      let list = this.students.filter(s => !enrolledIds.includes(s.id))
      
      // Filter by search query
      const query = this.enrollSearchQuery.toLowerCase().trim()
      if (query) {
        list = list.filter(s => s.full_name && s.full_name.toLowerCase().includes(query))
      }
      return list
    }
  },
  mounted() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      this.loading = true
      this.error = null
      const id = this.$route.params.id
      try {
        const [groupRes, coursesRes, usersRes, roomsRes, branchesRes, studentsRes, enrollmentsRes] = await Promise.all([
          axios.get(`http://localhost:8000/api/groups/${id}/`),
          axios.get('http://localhost:8000/api/courses/'),
          axios.get('http://localhost:8000/api/users/'),
          axios.get('http://localhost:8000/api/rooms/'),
          axios.get('http://localhost:8000/api/branches/'),
          axios.get('http://localhost:8000/api/students/'),
          axios.get('http://localhost:8000/api/enrollments/')
        ])
        
        this.group = groupRes.data
        this.courses = coursesRes.data
        this.teachers = usersRes.data.filter(u => u.role === 'teacher')
        this.rooms = roomsRes.data
        this.branches = branchesRes.data
        this.students = studentsRes.data
        this.enrollments = enrollmentsRes.data
      } catch (err) {
        console.error('Error fetching group details:', err)
        this.error = 'Failed to load group detail from the server.'
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
    openEnrollModal() {
      this.selectedStudentIds = []
      this.enrollSearchQuery = ''
      this.showEnrollModal = true
    },
    closeEnrollModal() {
      this.showEnrollModal = false
    },
    async enrollSelectedStudents() {
      this.submittingEnrollment = true
      try {
        // Build an array of API requests for each student to enroll
        const requests = this.selectedStudentIds.map(studentId => {
          return axios.post('http://localhost:8000/api/enrollments/', {
            student: studentId,
            group: this.group.id,
            status: 'enrolled'
          })
        })

        await Promise.all(requests)
        this.closeEnrollModal()
        await this.fetchData()
      } catch (err) {
        console.error('Error enrolling students:', err)
        alert('An error occurred while enrolling the students.')
      } finally {
        this.submittingEnrollment = false
      }
    },
    async unenrollStudent(enrolled) {
      if (!confirm(`Are you sure you want to remove "${enrolled.full_name}" from this group?`)) {
        return
      }
      try {
        await axios.delete(`http://localhost:8000/api/enrollments/${enrolled.enrollmentId}/`)
        await this.fetchData()
      } catch (err) {
        console.error('Error removing student:', err)
        alert('An error occurred while removing the student.')
      }
    }
  }
}
</script>

<style scoped>
@import '../assets/views.css';

/* Layout Grid */
.detail-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  align-items: start;
}

@media (max-width: 900px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
}

/* Back Button */
.back-btn {
  font-size: 0.85rem;
  padding: 0.45rem 0.85rem;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

/* Card layout enhancements */
.table-header-bar {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-section-title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: #0f172a;
}

/* Info Card Sidebar */
.info-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
  padding: 1.5rem;
}

.info-card-title {
  margin: 0 0 1.25rem 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: #0f172a;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e2e8f0;
}

.info-details-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-size: 0.9rem;
  gap: 1rem;
}

.info-label {
  color: #64748b;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  color: #334155;
  text-align: right;
}

.info-description-box {
  margin-top: 1.5rem;
  padding-top: 1.25rem;
  border-top: 1px solid #f1f5f9;
}

.description-text {
  margin: 0;
  font-size: 0.9rem;
  color: #475569;
  line-height: 1.5;
  background-color: #f8fafc;
  padding: 0.75rem;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  white-space: pre-wrap;
}

/* Loading Fullscreen */
.loading-state-fullscreen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8rem 2rem;
  color: #64748b;
  gap: 1rem;
}

/* Enroll checklist modal styling */
.modal-instructions {
  font-size: 0.9rem;
  color: #475569;
  margin: 0 0 1rem 0;
}

.checklist-wrapper {
  max-height: 250px;
  overflow-y: auto;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background-color: white;
}

.checklist-item {
  border-bottom: 1px solid #f1f5f9;
  transition: background-color 0.15s;
}

.checklist-item:last-child {
  border-bottom: none;
}

.checklist-item:hover {
  background-color: #f8fafc;
}

.checklist-label {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  cursor: pointer;
  width: 100%;
  box-sizing: border-box;
}

.checkbox-input {
  margin-right: 1rem;
  width: 16px;
  height: 16px;
  accent-color: #6366f1;
  cursor: pointer;
}

.checklist-student-details {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.checklist-student-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: #0f172a;
}

.checklist-student-phone {
  font-size: 0.775rem;
  color: #64748b;
}

/* Small button utility */
.btn-sm {
  padding: 0.4rem 0.8rem;
  font-size: 0.8rem;
  border-radius: 8px;
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
