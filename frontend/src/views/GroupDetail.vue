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
      <!-- Top Section: Group Metadata -->
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
              <span class="info-label">Days</span>
              <span class="info-value">{{ group.group_days_at || 'Mon-Wed-Fri' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Duration</span>
              <span class="info-value">{{ group.duration }} minutes</span>
            </div>
            <div class="info-item">
              <span class="info-label">Price</span>
              <span class="info-value font-mono font-semibold">{{ formatPrice(group.price) }} UZS</span>
            </div>
          </div>
          <div class="info-description-box" v-if="group.description">
            <span class="info-label" style="display: block; margin-bottom: 0.4rem;">Description</span>
            <p class="description-text">{{ group.description }}</p>
          </div>
        </div>
      </div>

      <!-- Bottom Section: Students Roster -->
      <div class="main-column">
        <div class="table-card">
          <div class="table-header-bar">
            <h2 class="card-section-title">Enrolled Students</h2>
            <button v-if="userRole !== 'teacher'" @click="openEnrollModal" class="btn btn-primary btn-sm">
              <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              Enroll a Student
            </button>
            <button v-if="userRole === 'teacher'" @click="openGradeModal" class="btn btn-primary btn-sm">
              <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              Grade Students
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
                  <th v-if="userRole !== 'teacher'">Payment Status</th>
                  <th>Enrollment Date</th>
                  <th v-if="userRole !== 'teacher'" style="text-align: right;">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="enrolled in enrolledStudents" :key="enrolled.enrollmentId" class="table-row">
                  <td class="font-mono text-muted">#{{ enrolled.id }}</td>
                  <td class="font-semibold">
                    <router-link :to="`/enrollments/${enrolled.enrollmentId}`" class="student-detail-link">
                      {{ enrolled.full_name }}
                    </router-link>
                  </td>
                  <td>{{ enrolled.phone1 }}</td>
                  <td>
                    <span :class="['status-badge', enrolled.status || 'enrolled']">
                      {{ enrolled.status || 'enrolled' }}
                    </span>
                  </td>
                   <td v-if="userRole !== 'teacher'">
                    <div class="payment-status-cell">
                      <span :class="['status-badge', enrolled.payment_status || 'debt']">
                        {{ enrolled.payment_status || 'debt' }}
                      </span>
                      <span v-if="(enrolled.payment_status || 'debt') === 'debt'" class="debt-amount">
                        {{ formatPrice(enrolled.debt_amount) }} UZS
                      </span>
                      <button
                        v-if="(enrolled.payment_status || 'debt') === 'debt' && enrolled.status !== 'dropped'"
                        @click="openPaymentModal(enrolled)"
                        class="btn-pay"
                        title="Record Payment"
                      >
                        Pay
                      </button>
                    </div>
                  </td>
                  <td>{{ formatDate(enrolled.date) }}</td>
                   <td v-if="userRole !== 'teacher'" class="actions-cell">
                    <button
                      v-if="enrolled.status !== 'dropped'"
                      @click="unenrollStudent(enrolled)"
                      class="btn-icon btn-icon-danger"
                      title="Unenroll Student"
                    >
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
                  <td :colspan="userRole === 'teacher' ? 5 : 7" class="empty-state">No students currently enrolled in this group.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Graded Students Card -->
        <div class="table-card" style="margin-top: 1.5rem;">
          <div class="table-header-bar">
            <h2 class="card-section-title">Graded Students</h2>
          </div>
          <div class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Student Name</th>
                  <th>Grade</th>
                  <th>Date</th>
                  <th>Teacher</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="grade in groupGrades" :key="grade.id" class="table-row">
                  <td class="font-semibold">{{ grade.studentName }}</td>
                  <td>
                    <span :class="['grade-badge', 'grade-' + grade.grade]">
                      {{ getGradeLabel(grade.grade) }}
                    </span>
                  </td>
                  <td>{{ formatDate(grade.date) }}</td>
                  <td>{{ grade.teacherName }}</td>
                  <td class="text-muted">{{ grade.description || '-' }}</td>
                </tr>
                <tr v-if="!groupGrades.length">
                  <td colspan="5" class="empty-state">No grades recorded yet.</td>
                </tr>
              </tbody>
            </table>
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
          
          <!-- Search box & New Student Button -->
          <div style="display: flex; gap: 0.5rem; margin-bottom: 0.75rem;">
            <input
              type="text"
              v-model="enrollSearchQuery"
              placeholder="Search students by name..."
              class="form-input"
              style="padding: 0.55rem 0.75rem; font-size: 0.875rem; flex: 1;"
            />
            <button
              type="button"
              @click="openCreateStudentModal"
              class="btn btn-primary"
              style="font-size: 0.85rem; padding: 0.55rem 0.75rem; flex-shrink: 0; white-space: nowrap;"
            >
              New Student
            </button>
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

    <!-- Grade Students Modal -->
    <div v-if="showGradeModal" class="modal-backdrop" @click.self="closeGradeModal">
      <div class="modal-content" style="max-width: 480px;">
        <div class="modal-header">
          <h2 class="modal-title">Grade Student</h2>
          <button @click="closeGradeModal" class="modal-close">
            <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <form @submit.prevent="submitGrade">
          <div class="modal-body">
            <div class="form-group" style="margin-bottom: 1.25rem; display: flex; flex-direction: column; gap: 0.5rem; text-align: left;">
              <label for="gradeStudent" class="form-label" style="font-size: 0.875rem; font-weight: 500; color: #475569;">Select Student</label>
              <select id="gradeStudent" v-model="gradeForm.enrolled_student" required class="form-input" style="width: 100%;">
                <option value="" disabled>Select Student...</option>
                <option v-for="student in activeEnrolledStudents" :key="student.id" :value="student.studentId">
                  {{ student.full_name }}
                </option>
              </select>
            </div>

            <div class="form-group" style="margin-bottom: 1.25rem; display: flex; flex-direction: column; gap: 0.5rem; text-align: left;">
              <label for="gradeValue" class="form-label" style="font-size: 0.875rem; font-weight: 500; color: #475569;">Grade</label>
              <select id="gradeValue" v-model.number="gradeForm.grade" required class="form-input" style="width: 100%;">
                <option :value="5">5 - Excellent 🤩</option>
                <option :value="4">4 - Good 🙂</option>
                <option :value="3">3 - Not bad 😐</option>
                <option :value="2">2 - Bad 😞</option>
              </select>
            </div>

            <div class="form-group" style="margin-bottom: 1.25rem; display: flex; flex-direction: column; gap: 0.5rem; text-align: left;">
              <label for="gradeDescription" class="form-label" style="font-size: 0.875rem; font-weight: 500; color: #475569;">Description (Optional)</label>
              <textarea
                id="gradeDescription"
                v-model="gradeForm.description"
                placeholder="Remarks on performance, homework, etc..."
                class="form-input"
                rows="3"
                style="width: 100%; box-sizing: border-box; resize: vertical;"
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" @click="closeGradeModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="submittingGrade || !gradeForm.enrolled_student">
              {{ submittingGrade ? 'Saving...' : 'Submit Grade' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Confirm Payment Modal -->
    <div v-if="showPaymentModal" class="modal-backdrop" @click.self="closePaymentModal">
      <div class="modal-content" style="max-width: 500px;">
        <div class="modal-header">
          <h2 class="modal-title">Record Payment</h2>
          <button @click="closePaymentModal" class="modal-close">
            <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <form @submit.prevent="confirmPayment">
          <div class="modal-body">
            <p class="modal-instructions" style="margin-bottom: 1.25rem;">
              Confirm payment for student <strong>{{ paymentEnrollment ? paymentEnrollment.full_name : '' }}</strong> in group <strong>{{ group.name }}</strong>.
            </p>

            <div class="form-group" style="margin-bottom: 1.25rem; display: flex; flex-direction: column; gap: 0.5rem; text-align: left;">
              <label for="paymentAmount" class="form-label" style="font-size: 0.875rem; font-weight: 500; color: #cbd5e1;">Amount (UZS)</label>
              <input
                type="text"
                inputmode="numeric"
                id="paymentAmount"
                :value="paymentForm.amount"
                @input="formatPaymentInputPrice"
                required
                class="form-input"
                style="width: 100%; box-sizing: border-box;"
              />
            </div>

            <div class="form-group" style="margin-bottom: 1.25rem; display: flex; flex-direction: column; gap: 0.5rem; text-align: left;">
              <label for="paymentMethod" class="form-label" style="font-size: 0.875rem; font-weight: 500; color: #cbd5e1;">Payment Method</label>
              <select id="paymentMethod" v-model="paymentForm.payment_method" required class="form-input" style="width: 100%; box-sizing: border-box;">
                <option value="cash">Cash</option>
                <option value="card">Card</option>
              </select>
            </div>

            <div class="form-group" style="display: flex; flex-direction: column; gap: 0.5rem; text-align: left;">
              <label for="paymentDescription" class="form-label" style="font-size: 0.875rem; font-weight: 500; color: #cbd5e1;">Description (Optional)</label>
              <textarea
                id="paymentDescription"
                v-model="paymentForm.description"
                class="form-input"
                rows="3"
                placeholder="e.g. Monthly tuition fee payment"
                style="width: 100%; box-sizing: border-box; resize: vertical;"
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" @click="closePaymentModal" class="btn btn-secondary">Cancel</button>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="submittingPayment || !paymentForm.amount"
            >
              {{ submittingPayment ? 'Processing...' : 'Confirm Payment' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Create Student Modal -->
    <div v-if="showCreateStudentModal" class="modal-backdrop" @click.self="closeCreateStudentModal" style="z-index: 10000;">
      <div class="modal-content" style="max-width: 480px;">
        <div class="modal-header">
          <h2 class="modal-title">Create New Student</h2>
          <button @click="closeCreateStudentModal" class="modal-close">
            <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <form @submit.prevent="saveNewStudent">
          <div class="modal-body">
            <div class="form-group" style="margin-bottom: 1.25rem; display: flex; flex-direction: column; gap: 0.5rem; text-align: left;">
              <label for="newStudentName" class="form-label" style="font-size: 0.875rem; font-weight: 500; color: #475569;">Full Name</label>
              <input
                type="text"
                id="newStudentName"
                v-model="studentForm.full_name"
                required
                placeholder="e.g. John Doe"
                class="form-input"
                style="width: 100%; box-sizing: border-box;"
              />
            </div>

            <div class="form-group" style="margin-bottom: 1.25rem; display: flex; flex-direction: column; gap: 0.5rem; text-align: left;">
              <label for="newStudentPhone1" class="form-label" style="font-size: 0.875rem; font-weight: 500; color: #475569;">Primary Phone</label>
              <input
                type="text"
                id="newStudentPhone1"
                v-model="studentForm.phone1"
                required
                placeholder="e.g. +998 90 123 45 67"
                class="form-input"
                style="width: 100%; box-sizing: border-box;"
              />
            </div>

            <div class="form-group" style="margin-bottom: 1.25rem; display: flex; flex-direction: column; gap: 0.5rem; text-align: left;">
              <label for="newStudentPhone2" class="form-label" style="font-size: 0.875rem; font-weight: 500; color: #475569;">Secondary Phone (Optional)</label>
              <input
                type="text"
                id="newStudentPhone2"
                v-model="studentForm.phone2"
                placeholder="e.g. +998 90 987 65 43"
                class="form-input"
                style="width: 100%; box-sizing: border-box;"
              />
            </div>

            <div class="form-group" style="display: flex; flex-direction: column; gap: 0.5rem; text-align: left;">
              <label for="newStudentDescription" class="form-label" style="font-size: 0.875rem; font-weight: 500; color: #475569;">Description (Optional)</label>
              <textarea
                id="newStudentDescription"
                v-model="studentForm.description"
                class="form-input"
                rows="3"
                placeholder="e.g. Prep for IELTS"
                style="width: 100%; box-sizing: border-box; resize: vertical;"
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" @click="closeCreateStudentModal" class="btn btn-secondary">Cancel</button>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="submittingNewStudent || !studentForm.full_name || !studentForm.phone1"
            >
              {{ submittingNewStudent ? 'Creating...' : 'Create Student' }}
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
      userRole: localStorage.getItem('user_role') || '',
      userId: parseInt(localStorage.getItem('user_id')) || null,
      grades: [],

      // Grading state
      showGradeModal: false,
      submittingGrade: false,
      gradeForm: {
        enrolled_student: '',
        grade: 5,
        description: ''
      },

      // Enrollment modal state
      showEnrollModal: false,
      enrollSearchQuery: '',
      selectedStudentIds: [],
      submittingEnrollment: false,

      // Payment modal state
      showPaymentModal: false,
      paymentEnrollment: null,
      paymentForm: {
        amount: '',
        payment_method: 'cash',
        description: ''
      },
      submittingPayment: false,

      // Create student modal state
      showCreateStudentModal: false,
      submittingNewStudent: false,
      studentForm: {
        full_name: '',
        phone1: '',
        phone2: '',
        description: ''
      }
    }
  },
  computed: {
    groupGrades() {
      if (!this.group || !this.grades.length) return []
      return this.grades
        .filter(g => g.group === this.group.id && g.is_active !== false)
        .map(g => {
          const student = this.students.find(s => s.id === g.enrolled_student)
          const teacher = this.teachers.find(t => t.id === g.teacher)
          return {
            ...g,
            studentName: student ? student.full_name : `Student #${g.enrolled_student}`,
            teacherName: teacher ? `${teacher.first_name} ${teacher.last_name}` : `Teacher #${g.teacher}`
          }
        })
        .sort((a, b) => new Date(b.date) - new Date(a.date) || b.id - a.id)
    },
    activeEnrolledStudents() {
      return this.enrolledStudents.filter(s => s.status !== 'dropped')
    },
    enrolledStudents() {
      if (!this.group || !this.students.length || !this.enrollments.length) return []
      // Filter active enrollments for this group
      const groupEnrollments = this.enrollments.filter(e => e.group === this.group.id)
      return groupEnrollments.map(e => {
        const studentInfo = this.students.find(s => s.id === e.student)
        return {
          enrollmentId: e.id,
          status: e.status,
          payment_status: e.payment_status,
          debt_amount: e.debt_amount,
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
        const [groupRes, coursesRes, usersRes, roomsRes, branchesRes, studentsRes, enrollmentsRes, gradesRes] = await Promise.all([
          axios.get(`http://localhost:8000/api/groups/${id}/`),
          axios.get('http://localhost:8000/api/courses/'),
          axios.get('http://localhost:8000/api/users/'),
          axios.get('http://localhost:8000/api/rooms/'),
          axios.get('http://localhost:8000/api/branches/'),
          axios.get('http://localhost:8000/api/students/'),
          axios.get('http://localhost:8000/api/enrollments/'),
          axios.get('http://localhost:8000/api/grades/')
        ])
        
        this.group = groupRes.data
        this.courses = coursesRes.data
        this.teachers = usersRes.data.filter(u => u.role === 'teacher')
        this.rooms = roomsRes.data
        this.branches = branchesRes.data
        this.students = studentsRes.data
        this.enrollments = enrollmentsRes.data
        this.grades = gradesRes.data
      } catch (err) {
        console.error('Error fetching group details:', err)
        this.error = 'Failed to load group detail from the server.'
      } finally {
        this.loading = false
      }
    },
    openGradeModal() {
      this.gradeForm = {
        enrolled_student: '',
        grade: 5,
        description: ''
      }
      this.showGradeModal = true
    },
    closeGradeModal() {
      this.showGradeModal = false
    },
    async submitGrade() {
      this.submittingGrade = true
      try {
        const payload = {
          enrolled_student: this.gradeForm.enrolled_student,
          group: this.group.id,
          teacher: this.userId,
          grade: this.gradeForm.grade,
          description: this.gradeForm.description,
          date: new Date().toISOString().split('T')[0]
        }
        await axios.post('http://localhost:8000/api/grades/', payload)
        this.closeGradeModal()
        this.fetchData()
      } catch (err) {
        console.error('Error submitting grade:', err)
        alert('An error occurred while saving the student grade record.')
      } finally {
        this.submittingGrade = false
      }
    },
    getGradeLabel(grade) {
      switch (grade) {
        case 5: return 'Excellent 🤩'
        case 4: return 'Good 🙂'
        case 3: return 'Not bad 😐'
        case 2: return 'Bad 😞'
        default: return `${grade}`
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
    formatPrice(price) {
      if (!price && price !== 0) return '0'
      const val = Math.round(parseFloat(price))
      return val.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
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
            status: 'enrolled',
            payment_status: 'debt'
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
      if (!confirm(`Are you sure you want to drop "${enrolled.full_name}" from this group?`)) {
        return
      }
      try {
        await axios.delete(`http://localhost:8000/api/enrollments/${enrolled.enrollmentId}/`)
        await this.fetchData()
      } catch (err) {
        console.error('Error removing student:', err)
      }
    },
    openPaymentModal(enrolled) {
      this.paymentEnrollment = enrolled
      const val = Math.round(parseFloat(this.group.price || 0))
      this.paymentForm.amount = val.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
      this.paymentForm.payment_method = 'cash'
      this.paymentForm.description = ''
      this.showPaymentModal = true
    },
    closePaymentModal() {
      this.showPaymentModal = false
      this.paymentEnrollment = null
      this.paymentForm.amount = ''
      this.paymentForm.payment_method = 'cash'
      this.paymentForm.description = ''
    },
    formatPaymentInputPrice(event) {
      const value = event.target.value
      const selectionStart = event.target.selectionStart
      const oldLength = value.length

      const digits = value.replace(/\D/g, '')
      const formatted = digits.replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
      
      this.paymentForm.amount = formatted
      
      this.$nextTick(() => {
        if (event.target) {
          const newLength = formatted.length
          const delta = newLength - oldLength
          const newCursorPos = selectionStart + delta
          event.target.setSelectionRange(newCursorPos, newCursorPos)
        }
      })
    },
    async confirmPayment() {
      this.submittingPayment = true
      try {
        // Create payment record
        const rawAmount = String(this.paymentForm.amount).replace(/\s/g, '')
        const amountVal = parseFloat(rawAmount || 0)
        
        await axios.post('http://localhost:8000/api/payments/', {
          group: this.group.id,
          student: this.paymentEnrollment.studentId,
          amount: amountVal,
          payment_method: this.paymentForm.payment_method,
          description: this.paymentForm.description || `Payment for group: ${this.group.name}`
        })
        
        this.closePaymentModal()
        await this.fetchData()
      } catch (err) {
        console.error('Error confirming payment:', err)
        alert('An error occurred while confirming the payment.')
      } finally {
        this.submittingPayment = false
      }
    },
    openCreateStudentModal() {
      this.studentForm = {
        full_name: '',
        phone1: '',
        phone2: '',
        description: ''
      }
      this.showCreateStudentModal = true
    },
    closeCreateStudentModal() {
      this.showCreateStudentModal = false
    },
    async saveNewStudent() {
      this.submittingNewStudent = true
      try {
        const response = await axios.post('http://localhost:8000/api/students/', this.studentForm)
        const newStudent = response.data
        
        // Refresh students list
        const studentsRes = await axios.get('http://localhost:8000/api/students/')
        this.students = studentsRes.data
        
        // Auto-select the new student for enrollment
        if (newStudent && newStudent.id) {
          if (!this.selectedStudentIds.includes(newStudent.id)) {
            this.selectedStudentIds.push(newStudent.id)
          }
        }
        
        this.closeCreateStudentModal()
      } catch (err) {
        console.error('Error creating new student:', err)
        alert('An error occurred while creating the student.')
      } finally {
        this.submittingNewStudent = false
      }
    }
  }
}
</script>

<style scoped>
@import '../assets/views.css';

/* Layout Grid */
.detail-grid {
  display: flex;
  flex-direction: column;
  gap: 2rem;
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
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  font-size: 0.9rem;
  gap: 0.35rem;
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
  text-align: left;
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

.status-badge.paid {
  background-color: #dcfce7;
  color: #15803d;
}

.status-badge.debt {
  background-color: #fee2e2;
  color: #991b1b;
}

.payment-status-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.debt-amount {
  color: #dc2626;
  font-weight: 600;
  font-size: 0.85rem;
  white-space: nowrap;
}

.student-detail-link {
  color: #4f46e5;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.15s ease;
}

.student-detail-link:hover {
  color: #312e81;
  text-decoration: underline;
}

.btn-pay {
  background-color: #4f46e5;
  color: white;
  border: none;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  font-size: 0.775rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  display: inline-flex;
  align-items: center;
}

.btn-pay:hover {
  background-color: #4338ca;
  transform: translateY(-1px);
  box-shadow: 0 2px 5px rgba(79, 70, 229, 0.2);
}

.btn-pay:active {
  transform: translateY(0);
}

.grade-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
  font-size: 0.8rem;
  font-weight: 600;
  border: 1px solid transparent;
}
.grade-5 {
  background-color: #dcfce7;
  color: #15803d;
  border-color: #bbf7d0;
}
.grade-4 {
  background-color: #e0f2fe;
  color: #0369a1;
  border-color: #bae6fd;
}
.grade-3 {
  background-color: #fef3c7;
  color: #b45309;
  border-color: #fde68a;
}
.grade-2 {
  background-color: #fee2e2;
  color: #991b1b;
  border-color: #fca5a5;
}
</style>
