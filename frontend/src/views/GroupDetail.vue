<template>
  <div class="view-container">
    <!-- Breadcrumb Header -->
    <div class="breadcrumb-header">
      <router-link to="/groups" class="btn btn-secondary back-btn">
        <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="19" y1="12" x2="5" y2="12"></line>
          <polyline points="12 19 5 12 12 5"></polyline>
        </svg>
        {{ $t('groupDetail.back') }}
      </router-link>
    </div>

    <!-- View Header -->
    <div class="view-header" style="margin-top: 1rem;">
      <div>
        <h1 class="view-title">{{ group ? group.name : $t('groupDetail.loading') }}</h1>
        <p class="view-subtitle">{{ $t('groupDetail.details_sub') }}</p>
      </div>
      <div v-if="group" style="display: flex; gap: 1rem; align-items: center;">
        <span :class="['status-badge', group.status || 'ongoing']" style="font-size: 0.95rem; padding: 0.4rem 1rem;">
          {{ $t('groups.status_' + (group.status || 'ongoing')) }}
        </span>
        <button 
          v-if="group.status !== 'finished' && userRole !== 'teacher'"
          @click="confirmFinishGroup" 
          class="btn btn-danger"
          style="background-color: #ef4444;"
          :disabled="submittingFinishGroup"
        >
          {{ $t('groupDetail.finish_group_btn') }}
        </button>
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
          <h3 class="info-card-title">{{ $t('groupDetail.details_title') }}</h3>
          <div class="info-details-list">
            <div class="info-item">
              <span class="info-label">{{ $t('groupDetail.course') }}</span>
              <span class="info-value font-semibold">{{ getCourseName(group.course) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">{{ $t('groupDetail.teacher') }}</span>
              <span class="info-value">{{ getTeacherName(group.teacher) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">{{ $t('groupDetail.room') }}</span>
              <span class="info-value">{{ getRoomName(group.room) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">{{ $t('groupDetail.branch') }}</span>
              <span class="info-value">{{ getBranchName(group.branch) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">{{ $t('groupDetail.start_date') }}</span>
              <span class="info-value">{{ formatDate(group.started_at) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">{{ $t('groupDetail.time') }}</span>
              <span class="info-value font-mono">{{ formatTime(group.starts_at) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">{{ $t('groupDetail.days') }}</span>
              <span class="info-value">{{ $t('groups.' + (group.group_days_at || 'Mon-Wed-Fri')) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">{{ $t('groupDetail.duration') }}</span>
              <span class="info-value">{{ $t('groupDetail.duration_value', { val: group.duration }) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">{{ $t('groupDetail.price') }}</span>
              <span class="info-value font-mono font-semibold">{{ formatPrice(group.price) }} UZS</span>
            </div>
          </div>
          <div class="info-description-box" v-if="group.description">
            <span class="info-label" style="display: block; margin-bottom: 0.4rem;">{{ $t('common.description') }}</span>
            <p class="description-text">{{ group.description }}</p>
          </div>
        </div>
      </div>

      <!-- Bottom Section: Students Roster -->
      <div class="main-column">
        <!-- Enrolled Students (Hidden for teachers) -->
        <div v-if="userRole !== 'teacher'" class="table-card">
          <div class="table-header-bar">
            <h2 class="card-section-title">{{ $t('groupDetail.enrolled_students') }}</h2>
            <button v-if="userRole !== 'teacher'" @click="openEnrollModal" class="btn btn-primary btn-sm">
              <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              {{ $t('groupDetail.enroll_student') }}
            </button>
          </div>
          <div class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>{{ $t('groupDetail.student_fullname') }}</th>
                  <th>{{ $t('groupDetail.student_phone1') }}</th>
                  <th>{{ $t('groupDetail.enrollment_status') }}</th>
                  <th v-if="userRole !== 'teacher'">{{ $t('groupDetail.payment_status_label') }}</th>
                  <th>{{ $t('groupDetail.enrollment_date') }}</th>
                  <th v-if="userRole !== 'teacher'" style="text-align: right;">{{ $t('common.actions') }}</th>
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
                      {{ $t('groupDetail.status_' + (enrolled.status || 'enrolled')) }}
                    </span>
                  </td>
                   <td v-if="userRole !== 'teacher'">
                    <div class="payment-status-cell">
                      <span v-if="enrolled.enrolled_free" class="status-badge free-badge">
                        {{ $t('groupDetail.status_free') }}
                      </span>
                      <span v-else :class="['status-badge', enrolled.payment_status || 'debt']">
                        {{ $t('groupDetail.status_' + (enrolled.payment_status || 'debt')) }}
                      </span>
                      <span v-if="!enrolled.enrolled_free && (enrolled.payment_status || 'debt') === 'debt'" class="debt-amount">
                        {{ formatPrice(enrolled.debt_amount) }} UZS
                      </span>
                      <button
                        v-if="!enrolled.enrolled_free && (enrolled.payment_status || 'debt') === 'debt' && enrolled.status !== 'dropped'"
                        @click="openPaymentModal(enrolled)"
                        class="btn-pay"
                        :title="$t('groupDetail.record_payment_title')"
                      >
                        {{ $t('groupDetail.pay') }}
                      </button>
                    </div>
                  </td>
                  <td>{{ formatDate(enrolled.date) }}</td>
                   <td v-if="userRole !== 'teacher'" class="actions-cell">
                    <button
                      v-if="enrolled.status !== 'dropped'"
                      @click="unenrollStudent(enrolled)"
                      class="btn-icon btn-icon-danger"
                      :title="$t('groupDetail.unenroll_student_title')"
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
                   <td :colspan="userRole === 'teacher' ? 5 : 7" class="empty-state">{{ $t('groupDetail.no_students') }}</td>
                 </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Weekly Attendance & Grading Grid (For teachers only) -->
        <div v-if="userRole === 'teacher'" class="table-card">
          <div class="table-header-bar flex-header">
            <h2 class="card-section-title">{{ $t('groupDetail.weekly_grid') }}</h2>
            <div class="week-navigation">
              <button type="button" @click="prevWeek" class="nav-btn" :title="$t('groupDetail.prev_week')">
                <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <polyline points="15 18 9 12 15 6"></polyline>
                </svg>
              </button>
              <span class="week-label font-semibold">{{ formatWeekRange() }}</span>
              <button type="button" @click="nextWeek" class="nav-btn" :title="$t('groupDetail.next_week')">
                <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <polyline points="9 18 15 12 9 6"></polyline>
                </svg>
              </button>
            </div>
          </div>
          <div class="table-wrapper">
            <table class="data-table grid-table">
              <thead>
                <tr>
                  <th class="student-col-header">{{ $t('stats.student') }}</th>
                  <th v-for="day in weekDays" :key="day.dateStr" :class="{ 'today-col-header': day.isToday }" class="date-col-header">
                    <div class="day-header-info">
                      <span class="day-name font-semibold">{{ $t('groupDetail.day_' + day.name.toLowerCase()) }}</span>
                      <span class="day-date text-muted">{{ day.dateLabel }}</span>
                      <span v-if="day.isToday" class="today-badge">{{ $t('groupDetail.today') }}</span>
                    </div>
                  </th>
                  <th v-if="!weekDays.length">{{ $t('groupDetail.no_days') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="student in activeEnrolledStudents" :key="student.studentId" class="table-row">
                  <td class="student-cell">
                    <div class="student-cell-content">
                      <div class="student-avatar-circle">{{ getInitials(student.full_name) }}</div>
                      <div class="student-info-text">
                        <span class="student-name font-semibold">{{ student.full_name }}</span>
                        <span class="student-id font-mono text-muted">#{{ student.id }}</span>
                      </div>
                    </div>
                  </td>
                  
                  <td v-for="day in weekDays" :key="day.dateStr" :class="{ 'today-cell': day.isToday }" class="grid-cell">
                    <!-- Today (Editable) -->
                    <div v-if="day.isToday" class="editable-cell-wrapper">
                      <!-- Grade Select -->
                      <div class="cell-input-group">
                        <select 
                          :value="getGradeValue(student.studentId, day.dateStr)" 
                          @change="handleGradeChange(student.studentId, day.dateStr, $event.target.value)"
                          class="grid-select"
                        >
                          <option value="">{{ $t('groupDetail.grade_placeholder') }}</option>
                          <option value="5">{{ $t('groupDetail.grade_5') }}</option>
                          <option value="4">{{ $t('groupDetail.grade_4') }}</option>
                          <option value="3">{{ $t('groupDetail.grade_3') }}</option>
                          <option value="2">{{ $t('groupDetail.grade_2') }}</option>
                        </select>
                      </div>
                      
                      <!-- Absence Toggle -->
                      <div class="cell-input-group absence-toggle-group">
                        <label class="absence-checkbox-label">
                          <input 
                            type="checkbox" 
                            :checked="isAbsent(student.studentId, day.dateStr)" 
                            @change="handleAbsenceToggle(student.studentId, day.dateStr, $event.target.checked)"
                            class="checkbox-input grid-checkbox"
                          />
                          <span class="checkbox-custom-text">{{ $t('groupDetail.absent') }}</span>
                        </label>
                      </div>
                    </div>
                    
                    <!-- Other days (Read-only status badges) -->
                    <div v-else class="readonly-cell-wrapper">
                      <div class="badge-stack">
                        <!-- Absence Badge -->
                        <span v-if="isAbsent(student.studentId, day.dateStr)" class="absence-badge-static">
                          {{ $t('groupDetail.absent') }} ❌
                        </span>
                        
                        <!-- Grade Badge -->
                        <span 
                          v-if="getGradeValue(student.studentId, day.dateStr)" 
                          :class="['grade-badge', `grade-${getGradeValue(student.studentId, day.dateStr)}`]"
                        >
                          {{ getGradeLabelReadOnly(getGradeValue(student.studentId, day.dateStr)) }}
                        </span>
                        
                        <!-- Empty Placeholder -->
                        <span v-if="!isAbsent(student.studentId, day.dateStr) && !getGradeValue(student.studentId, day.dateStr)" class="empty-cell-dash">
                          -
                        </span>
                      </div>
                    </div>
                  </td>
                </tr>
                <tr v-if="!activeEnrolledStudents.length">
                  <td class="empty-state" colspan="8">{{ $t('groupDetail.no_students') }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Monthly Attendance Grid (Admins and CEO only) -->
        <div v-if="userRole === 'admin' || userRole === 'CEO' || userRole === 'superuser'" class="table-card" style="margin-top: 2rem;">
          <div class="table-header-bar flex-header">
            <h2 class="card-section-title">
              {{ $t('groupDetail.monthly_grid') }}
              <span class="month-info-label" style="font-size: 0.95rem; color: #64748b; font-weight: 500; margin-left: 0.75rem; text-transform: capitalize; vertical-align: middle;">
                ({{ getMonthName(monthlyGridMonth) }} {{ monthlyGridYear }})
              </span>
            </h2>
            <div class="month-year-selectors">
              <!-- Month Dropdown -->
              <select :value="monthlyGridMonth" @change="monthlyGridMonth = parseInt($event.target.value)" class="form-input selector-dropdown">
                <option v-for="m in 12" :key="m - 1" :value="m - 1">
                  {{ getMonthName(m - 1) }}
                </option>
              </select>
              <!-- Year Dropdown -->
              <select :value="monthlyGridYear" @change="monthlyGridYear = parseInt($event.target.value)" class="form-input selector-dropdown">
                <option v-for="y in availableYears" :key="y" :value="y">
                  {{ y }}
                </option>
              </select>
            </div>
          </div>
          <div class="table-wrapper monthly-grid-wrapper">
            <table class="data-table grid-table monthly-grid-table">
              <thead>
                <tr>
                  <th class="student-col-header">{{ $t('stats.student') }}</th>
                  <th v-for="day in monthlyGridDays" :key="day.dayNum" :class="{ 'today-col-header': day.isToday, 'weekend-col-header': day.weekday === 'Sun' }" class="date-col-header monthly-date-header">
                    <div class="day-header-info">
                      <span class="day-date font-semibold">{{ day.dayNum }}</span>
                      <span class="day-name text-muted" style="font-size: 0.7rem;">{{ formatWeekdayShort(day.weekday) }}</span>
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="student in activeEnrolledStudents" :key="student.studentId" class="table-row">
                  <td class="student-cell">
                    <div class="student-cell-content">
                      <div class="student-avatar-circle">{{ getInitials(student.full_name) }}</div>
                      <div class="student-info-text">
                        <span class="student-name font-semibold">{{ student.full_name }}</span>
                        <span class="student-id font-mono text-muted">#{{ student.id }}</span>
                      </div>
                    </div>
                  </td>
                  
                  <td v-for="day in monthlyGridDays" :key="day.dayNum" :class="{ 'today-cell': day.isToday, 'non-class-day': !isClassDay(student.studentId, day.dateStr) }" class="grid-cell monthly-cell">
                    <div class="readonly-cell-wrapper">
                      <!-- Class Day -->
                      <template v-if="isClassDay(student.studentId, day.dateStr)">
                        <!-- Absence -->
                        <span v-if="isAbsent(student.studentId, day.dateStr)" class="absence-dot" :title="$t('groupDetail.absent')">
                          ❌
                        </span>
                        <!-- Grade -->
                        <span 
                          v-else-if="getGradeValue(student.studentId, day.dateStr)" 
                          :class="['monthly-grade-badge', `grade-${getGradeValue(student.studentId, day.dateStr)}`]"
                          :title="getGradeLabelReadOnly(getGradeValue(student.studentId, day.dateStr))"
                        >
                          {{ getGradeValue(student.studentId, day.dateStr) }}
                        </span>
                        <!-- Present -->
                        <span v-else class="present-dot" :title="$t('groupDetail.present') || 'Present'">
                          ✔
                        </span>
                      </template>
                      <!-- Non-class Day -->
                      <template v-else>
                        <span class="empty-cell-dash">-</span>
                      </template>
                    </div>
                  </td>
                </tr>
                <tr v-if="!activeEnrolledStudents.length">
                  <td class="empty-state" :colspan="monthlyGridDays.length + 1">{{ $t('groupDetail.no_students') }}</td>
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
      <span>{{ $t('groupDetail.loading') }}</span>
    </div>

    <!-- Enroll Students Modal -->
    <div v-if="showEnrollModal" class="modal-backdrop" @click.self="closeEnrollModal">
      <div class="modal-content" style="max-width: 500px;">
        <div class="modal-header">
          <h2 class="modal-title">{{ $t('groupDetail.enroll_modal_title') }}</h2>
          <button @click="closeEnrollModal" class="modal-close">
            <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <p class="modal-instructions" v-html="$t('groupDetail.enroll_instructions', { name: `<strong>${group.name}</strong>` })"></p>
          
          <!-- Search box & New Student Button -->
          <div style="display: flex; gap: 0.5rem; margin-bottom: 0.75rem;">
            <input
              type="text"
              v-model="enrollSearchQuery"
              :placeholder="$t('groupDetail.search_students')"
              class="form-input"
              style="padding: 0.55rem 0.75rem; font-size: 0.875rem; flex: 1;"
            />
            <button
              type="button"
              @click="openCreateStudentModal"
              class="btn btn-primary"
              style="font-size: 0.85rem; padding: 0.55rem 0.75rem; flex-shrink: 0; white-space: nowrap;"
            >
              {{ $t('groupDetail.new_student_btn') }}
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
              {{ $t('groupDetail.no_students_available') }}
            </div>
          </div>
          
          <!-- Free Enrollment toggle -->
          <div style="margin-top: 1rem; text-align: left; display: flex; align-items: center; gap: 0.5rem;">
            <label class="absence-checkbox-label" style="font-size: 0.9rem; color: #475569; font-weight: 500; display: inline-flex; align-items: center; gap: 0.5rem; cursor: pointer;">
              <input
                type="checkbox"
                v-model="enrollFreeChecked"
                class="checkbox-input"
                style="width: 18px; height: 18px; cursor: pointer;"
              />
              {{ $t('groupDetail.enroll_free_label') }}
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" @click="closeEnrollModal" class="btn btn-secondary">{{ $t('common.cancel') }}</button>
          <button
            type="button"
            @click="enrollSelectedStudents"
            class="btn btn-primary"
            :disabled="submittingEnrollment || !selectedStudentIds.length"
          >
            {{ submittingEnrollment ? $t('groupDetail.enrolling') : $t('groupDetail.enroll_selected_btn', { count: selectedStudentIds.length }) }}
          </button>
        </div>
      </div>
    </div>

    <!-- Confirm Payment Modal -->
    <div v-if="showPaymentModal" class="modal-backdrop" @click.self="closePaymentModal">
      <div class="modal-content" style="max-width: 500px;">
        <div class="modal-header">
          <h2 class="modal-title">{{ $t('groupDetail.record_payment_title') }}</h2>
          <button @click="closePaymentModal" class="modal-close">
            <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <form @submit.prevent="confirmPayment">
          <div class="modal-body">
            <p class="modal-instructions" style="margin-bottom: 1.25rem;" v-html="$t('groupDetail.confirm_payment_instructions', { student: '<strong>' + (paymentEnrollment ? paymentEnrollment.full_name : '') + '</strong>', group: '<strong>' + group.name + '</strong>' })">
            </p>

            <div class="form-group" style="margin-bottom: 1.25rem; display: flex; flex-direction: column; gap: 0.5rem; text-align: left;">
              <label for="paymentAmount" class="form-label" style="font-size: 0.875rem; font-weight: 500; color: #cbd5e1;">{{ $t('groupDetail.payment_amount') }}</label>
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
              <label for="paymentMethod" class="form-label" style="font-size: 0.875rem; font-weight: 500; color: #cbd5e1;">{{ $t('groupDetail.payment_method') }}</label>
              <select id="paymentMethod" v-model="paymentForm.payment_method" required class="form-input" style="width: 100%; box-sizing: border-box;">
                <option value="cash">{{ $t('groupDetail.cash') }}</option>
                <option value="card">{{ $t('groupDetail.card') }}</option>
              </select>
            </div>

            <div class="form-group" style="display: flex; flex-direction: column; gap: 0.5rem; text-align: left;">
              <label for="paymentDescription" class="form-label" style="font-size: 0.875rem; font-weight: 500; color: #cbd5e1;">{{ $t('groupDetail.payment_desc') }}</label>
              <textarea
                id="paymentDescription"
                v-model="paymentForm.description"
                class="form-input"
                rows="3"
                :placeholder="$t('groupDetail.payment_desc_placeholder')"
                style="width: 100%; box-sizing: border-box; resize: vertical;"
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" @click="closePaymentModal" class="btn btn-secondary">{{ $t('common.cancel') }}</button>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="submittingPayment || !paymentForm.amount"
            >
              {{ submittingPayment ? $t('groupDetail.processing') : $t('groupDetail.confirm_payment_btn') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Create Student Modal -->
    <div v-if="showCreateStudentModal" class="modal-backdrop" @click.self="closeCreateStudentModal" style="z-index: 10000;">
      <div class="modal-content" style="max-width: 480px;">
        <div class="modal-header">
          <h2 class="modal-title">{{ $t('groupDetail.create_student_title') }}</h2>
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
              <label for="newStudentName" class="form-label" style="font-size: 0.875rem; font-weight: 500; color: #475569;">{{ $t('groupDetail.student_fullname') }}</label>
              <input
                type="text"
                id="newStudentName"
                v-model="studentForm.full_name"
                required
                :placeholder="$t('groupDetail.student_fullname_placeholder')"
                class="form-input"
                style="width: 100%; box-sizing: border-box;"
              />
            </div>

            <div class="form-group" style="margin-bottom: 1.25rem; display: flex; flex-direction: column; gap: 0.5rem; text-align: left;">
              <label for="newStudentPhone1" class="form-label" style="font-size: 0.875rem; font-weight: 500; color: #475569;">{{ $t('groupDetail.student_phone1') }}</label>
              <div class="phone-input-wrapper">
                <span class="phone-prefix">+998</span>
                <input
                  type="text"
                  inputmode="numeric"
                  maxlength="12"
                  id="newStudentPhone1"
                  :value="studentForm.phone1"
                  @input="handleStudentPhoneInput($event, 'phone1')"
                  @keypress="onlyNumber"
                  required
                  placeholder="90 123 45 67"
                  class="phone-editable-input"
                />
              </div>
            </div>

            <div class="form-group" style="margin-bottom: 1.25rem; display: flex; flex-direction: column; gap: 0.5rem; text-align: left;">
              <label for="newStudentPhone2" class="form-label" style="font-size: 0.875rem; font-weight: 500; color: #475569;">{{ $t('groupDetail.student_phone2') }}</label>
              <div class="phone-input-wrapper">
                <span class="phone-prefix">+998</span>
                <input
                  type="text"
                  inputmode="numeric"
                  maxlength="12"
                  id="newStudentPhone2"
                  :value="studentForm.phone2"
                  @input="handleStudentPhoneInput($event, 'phone2')"
                  @keypress="onlyNumber"
                  placeholder="90 123 45 67"
                  class="phone-editable-input"
                />
              </div>
            </div>

            <div class="form-group" style="display: flex; flex-direction: column; gap: 0.5rem; text-align: left;">
              <label for="newStudentDescription" class="form-label" style="font-size: 0.875rem; font-weight: 500; color: #475569;">{{ $t('common.description') }}</label>
              <textarea
                id="newStudentDescription"
                v-model="studentForm.description"
                class="form-input"
                rows="3"
                :placeholder="$t('groupDetail.student_desc_placeholder')"
                style="width: 100%; box-sizing: border-box; resize: vertical;"
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" @click="closeCreateStudentModal" class="btn btn-secondary">{{ $t('common.cancel') }}</button>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="submittingNewStudent || !studentForm.full_name || !studentForm.phone1"
            >
              {{ submittingNewStudent ? $t('groupDetail.creating') : $t('groupDetail.create_student_btn') }}
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
      absences: [],
      currentWeekStart: null,

      // Enrollment modal state
      showEnrollModal: false,
      enrollSearchQuery: '',
      selectedStudentIds: [],
      submittingEnrollment: false,
      enrollFreeChecked: false,

      // Payment modal state
      showPaymentModal: false,
      paymentEnrollment: null,
      paymentForm: {
        amount: '',
        payment_method: 'cash',
        description: ''
      },
      submittingPayment: false,
      submittingFinishGroup: false,

      // Create student modal state
      showCreateStudentModal: false,
      submittingNewStudent: false,
      studentForm: {
        full_name: '',
        phone1: '',
        phone2: '',
        description: ''
      },

      // Monthly grid state
      monthlyGridMonth: new Date().getMonth(),
      monthlyGridYear: new Date().getFullYear()
    }
  },
  computed: {
    todayStr() {
      const tzoffset = (new Date()).getTimezoneOffset() * 60000;
      const localISOTime = (new Date(Date.now() - tzoffset)).toISOString().slice(0, 10);
      return localISOTime;
    },
    weekDays() {
      if (!this.currentWeekStart) return []
      const daysList = []
      const weekDaysNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
      for (let i = 0; i < 6; i++) {
        const d = new Date(this.currentWeekStart)
        d.setDate(this.currentWeekStart.getDate() + i)
        const dateStr = d.toISOString().split('T')[0]
        daysList.push({
          name: weekDaysNames[i],
          dateLabel: d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          dateStr,
          isToday: dateStr === this.todayStr
        })
      }
      return daysList
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
          enrolled_free: e.enrolled_free,
          ...studentInfo
        }
      }).filter(item => item.full_name)
    },
    activeEnrolledStudents() {
      return this.enrolledStudents.filter(s => s.status !== 'dropped')
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
    },
    availableYears() {
      const currentYear = new Date().getFullYear()
      const years = []
      for (let y = currentYear - 2; y <= currentYear + 1; y++) {
        years.push(y)
      }
      return years
    },
    monthlyGridDays() {
      if (this.monthlyGridMonth === null || this.monthlyGridYear === null) return []
      const days = []
      const daysInMonth = new Date(this.monthlyGridYear, this.monthlyGridMonth + 1, 0).getDate()
      for (let i = 1; i <= daysInMonth; i++) {
        const d = new Date(this.monthlyGridYear, this.monthlyGridMonth, i)
        const weekday = d.toLocaleDateString('en-US', { weekday: 'short' }) // Mon, Tue, etc.
        const monthStr = String(this.monthlyGridMonth + 1).padStart(2, '0')
        const dayStr = String(i).padStart(2, '0')
        const dateStr = `${this.monthlyGridYear}-${monthStr}-${dayStr}`
        days.push({
          dayNum: i,
          weekday,
          dateStr,
          isToday: dateStr === this.todayStr
        })
      }
      return days
    }
  },
  created() {
    this.currentWeekStart = this.getMonday(new Date())
  },
  mounted() {
    this.fetchData()
  },
  methods: {
    async confirmFinishGroup() {
      const debtStudents = this.enrolledStudents.filter(s => s.status === 'enrolled' && s.payment_status === 'debt')
      
      if (debtStudents.length > 0) {
        const studentDetails = debtStudents.map(s => {
          const debtFormatted = this.formatPrice(s.debt_amount)
          return `- ${s.full_name} (${debtFormatted} ${this.$t('common.uzs')})`
        }).join('\n')
        
        alert(this.$t('groupDetail.finish_group_debt_error', { students: studentDetails }))
        return
      }
      
      if (!confirm(this.$t('groupDetail.finish_group_confirm'))) {
        return
      }
      
      this.submittingFinishGroup = true
      try {
        await axios.patch(`http://localhost:8000/api/groups/${this.group.id}/`, {
          status: 'finished'
        })
        alert(this.$t('groupDetail.finish_group_success'))
        this.fetchData()
      } catch (err) {
        console.error('Error finishing group:', err)
        const errorMsg = err.response && err.response.data && typeof err.response.data === 'string'
          ? err.response.data
          : (err.response && err.response.data && err.response.data.detail
            ? err.response.data.detail
            : (err.response && err.response.data && typeof err.response.data === 'object'
              ? Object.values(err.response.data).join(', ')
              : ''))
        alert(errorMsg || 'Failed to finish the group.')
      } finally {
        this.submittingFinishGroup = false
      }
    },
    async fetchData() {
      this.loading = true
      this.error = null
      const id = this.$route.params.id
      try {
        const [groupRes, coursesRes, usersRes, roomsRes, branchesRes, studentsRes, enrollmentsRes, gradesRes, absencesRes] = await Promise.all([
          axios.get(`http://localhost:8000/api/groups/${id}/`),
          axios.get('http://localhost:8000/api/courses/'),
          axios.get('http://localhost:8000/api/users/'),
          axios.get('http://localhost:8000/api/rooms/'),
          axios.get('http://localhost:8000/api/branches/'),
          axios.get('http://localhost:8000/api/students/'),
          axios.get('http://localhost:8000/api/enrollments/'),
          axios.get('http://localhost:8000/api/grades/'),
          axios.get('http://localhost:8000/api/absences/')
        ])

        this.group = groupRes.data
        this.courses = coursesRes.data
        this.teachers = usersRes.data.filter(u => u.role === 'teacher')
        this.rooms = roomsRes.data
        this.branches = branchesRes.data
        this.students = studentsRes.data
        this.enrollments = enrollmentsRes.data
        this.grades = gradesRes.data
        this.absences = absencesRes.data

        // Set default month and year of the monthly grid to the group's start date on initial load
        if (this.group && this.group.started_at && this.hasInitializedMonthlyGrid === undefined) {
          const startDate = new Date(this.group.started_at)
          this.monthlyGridMonth = startDate.getMonth()
          this.monthlyGridYear = startDate.getFullYear()
          this.hasInitializedMonthlyGrid = true
        }
      } catch (err) {
        console.error('Error fetching group details:', err)
        this.error = this.$t('stats.api_error')
      } finally {
        this.loading = false
      }
    },
    getMonday(d) {
      d = new Date(d)
      const day = d.getDay()
      const diff = d.getDate() - day + (day === 0 ? -6 : 1)
      return new Date(d.setDate(diff))
    },
    prevWeek() {
      const prev = new Date(this.currentWeekStart)
      prev.setDate(prev.getDate() - 7)
      this.currentWeekStart = prev
    },
    nextWeek() {
      const next = new Date(this.currentWeekStart)
      next.setDate(next.getDate() + 7)
      this.currentWeekStart = next
    },
    formatWeekRange() {
      if (!this.currentWeekStart) return ""
      const start = this.currentWeekStart
      const end = new Date(this.currentWeekStart)
      end.setDate(end.getDate() + 5) // Saturday
      const locale = this.$i18n.locale === 'uz' ? 'uz-UZ' : 'ru-RU'
      return `${start.toLocaleDateString(locale, { month: 'short', day: 'numeric', year: 'numeric' })} - ${end.toLocaleDateString(locale, { month: 'short', day: 'numeric', year: 'numeric' })}`
    },
    getGradeValue(studentId, dateStr) {
      if (!this.grades || !this.grades.length) return ""
      const g = this.grades.find(
        x => x.enrolled_student === studentId && x.group === this.group.id && x.date === dateStr && x.is_active !== false
      )
      return g ? g.grade : ""
    },
    isAbsent(studentId, dateStr) {
      if (!this.absences || !this.absences.length) return false
      return this.absences.some(
        x => x.student === studentId && x.group === this.group.id && x.date === dateStr && x.is_active !== false
      )
    },
    async handleGradeChange(studentId, dateStr, value) {
      const existingGrade = this.grades.find(
        x => x.enrolled_student === studentId && x.group === this.group.id && x.date === dateStr && x.is_active !== false
      )
      
      try {
        if (value === "") {
          if (existingGrade) {
            await axios.delete(`http://localhost:8000/api/grades/${existingGrade.id}/`)
          }
        } else {
          const valNum = parseInt(value)
          if (existingGrade) {
            await axios.patch(`http://localhost:8000/api/grades/${existingGrade.id}/`, { grade: valNum })
          } else {
            await axios.post('http://localhost:8000/api/grades/', {
              enrolled_student: studentId,
              group: this.group.id,
              teacher: this.userId,
              grade: valNum,
              date: dateStr
            })
          }
        }
        await this.fetchData()
      } catch (err) {
        console.error('Error changing grade:', err)
        alert(this.$t('groupDetail.error_grade'))
      }
    },
    async handleAbsenceToggle(studentId, dateStr, isChecked) {
      const existingAbsence = this.absences.find(
        x => x.student === studentId && x.group === this.group.id && x.date === dateStr && x.is_active !== false
      )

      try {
        if (isChecked) {
          if (!existingAbsence) {
            await axios.post('http://localhost:8000/api/absences/', {
              student: studentId,
              group: this.group.id,
              teacher: this.userId,
              date: dateStr
            })
          }
        } else {
          if (existingAbsence) {
            await axios.delete(`http://localhost:8000/api/absences/${existingAbsence.id}/`)
          }
        }
        await this.fetchData()
      } catch (err) {
        console.error('Error changing absence:', err)
        alert(this.$t('groupDetail.error_absence'))
      }
    },
    getGradeLabelReadOnly(grade) {
      switch (grade) {
        case 5: return this.$t('groupDetail.grade_5')
        case 4: return this.$t('groupDetail.grade_4')
        case 3: return this.$t('groupDetail.grade_3')
        case 2: return this.$t('groupDetail.grade_2')
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
        const locale = this.$i18n.locale === 'uz' ? 'uz-UZ' : 'ru-RU'
        return date.toLocaleDateString(locale, { month: 'short', day: 'numeric', year: 'numeric' })
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
      this.enrollFreeChecked = false
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
            payment_status: this.enrollFreeChecked ? 'paid' : 'debt',
            enrolled_free: this.enrollFreeChecked
          })
        })

        await Promise.all(requests)
        this.closeEnrollModal()
        await this.fetchData()
      } catch (err) {
        console.error('Error enrolling students:', err)
        alert(this.$t('groupDetail.error_enroll'))
      } finally {
        this.submittingEnrollment = false
      }
    },
    async unenrollStudent(enrolled) {
      if (!confirm(this.$t('groupDetail.drop_confirm', { name: enrolled.full_name }))) {
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
        alert(this.$t('groupDetail.error_payment'))
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
      
      const rawPhone1 = this.studentForm.phone1.replace(/\D/g, '')
      if (rawPhone1.length !== 9) {
        alert(this.$t('students.phone_length_error'))
        this.submittingNewStudent = false
        return
      }
      if (this.studentForm.phone2) {
        const rawPhone2 = this.studentForm.phone2.replace(/\D/g, '')
        if (rawPhone2.length !== 9) {
          alert(this.$t('students.phone_length_error'))
          this.submittingNewStudent = false
          return
        }
      }

      const payload = {
        ...this.studentForm,
        phone1: '+998' + rawPhone1,
        phone2: this.studentForm.phone2 ? ('+998' + this.studentForm.phone2.replace(/\D/g, '')) : null
      }
      try {
        const response = await axios.post('http://localhost:8000/api/students/', payload)
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
        alert(this.$t('groupDetail.error_create_student'))
      } finally {
        this.submittingNewStudent = false
      }
    },
    formatStudentPhoneInput(val) {
      if (!val) return ''
      const digits = val.replace(/\D/g, '').slice(0, 9)
      let formatted = ''
      if (digits.length > 0) {
        formatted += digits.substring(0, 2)
      }
      if (digits.length > 2) {
        formatted += ' ' + digits.substring(2, 5)
      }
      if (digits.length > 5) {
        formatted += ' ' + digits.substring(5, 7)
      }
      if (digits.length > 7) {
        formatted += ' ' + digits.substring(7, 9)
      }
      return formatted
    },
    handleStudentPhoneInput(e, field) {
      const input = e.target
      const rawValue = input.value
      
      const selectionStart = input.selectionStart
      const digitsBefore = rawValue.substring(0, selectionStart).replace(/\D/g, '').length
      
      const formatted = this.formatStudentPhoneInput(rawValue)
      this.studentForm[field] = formatted
      
      this.$nextTick(() => {
        let newCursorPos = 0
        let digitCount = 0
        for (let i = 0; i < formatted.length; i++) {
          if (/\d/.test(formatted[i])) {
            digitCount++
          }
          newCursorPos = i + 1
          if (digitCount === digitsBefore) {
            break
          }
        }
        input.setSelectionRange(newCursorPos, newCursorPos)
      })
    },
    onlyNumber(event) {
      const charCode = event.which ? event.which : event.keyCode
      if (charCode > 31 && (charCode < 48 || charCode > 57)) {
        event.preventDefault()
      }
      return true
    },
    getInitials(name) {
      if (!name) return ''
      return name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()
    },
    getMonthName(monthIndex) {
      const date = new Date(this.monthlyGridYear || new Date().getFullYear(), monthIndex, 1)
      const locale = this.$i18n.locale === 'uz' ? 'uz-UZ' : 'ru-RU'
      return date.toLocaleDateString(locale, { month: 'long' })
    },
    formatWeekdayShort(weekdayShort) {
      const key = weekdayShort.toLowerCase()
      if (key === 'sun') {
        return this.$i18n.locale === 'uz' ? 'Yak' : 'Вс'
      }
      return this.$t('timetable.days.' + key)
    },
    isClassDay(studentId, dateStr) {
      if (this.isAbsent(studentId, dateStr) || this.getGradeValue(studentId, dateStr)) {
        return true
      }
      if (!this.group) return false
      if (this.group.started_at && dateStr < this.group.started_at) {
        return false
      }
      if (dateStr > this.todayStr) {
        return false
      }
      const d = new Date(dateStr)
      const dayOfWeek = d.getDay()
      const daysAt = this.group.group_days_at || 'Mon-Wed-Fri'
      if (daysAt === 'Mon-Wed-Fri') {
        return [1, 3, 5].includes(dayOfWeek)
      } else if (daysAt === 'Tue-Thur-Sat') {
        return [2, 4, 6].includes(dayOfWeek)
      } else if (daysAt === 'Everyday') {
        return dayOfWeek >= 1 && dayOfWeek <= 6
      }
      return false
    },
    handleMonthlyGridDateChange() {
      // local reaction if needed, but computed properties handle re-renders automatically
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

.status-badge.free-badge {
  background-color: #f5f3ff;
  color: #7c3aed;
  border: 1px solid #ddd6fe;
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

.today-row {
  background-color: rgba(99, 102, 241, 0.04) !important;
}

.grade-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.2rem 0.55rem;
  border-radius: 9999px;
  font-size: 0.75rem;
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

/* Week Navigation */
.flex-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.week-navigation {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background-color: #f1f5f9;
  padding: 0.35rem 0.75rem;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.nav-btn {
  background: white;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #475569;
}

.nav-btn:hover {
  background-color: #f8fafc;
  color: #0f172a;
  border-color: #94a3b8;
}

.week-label {
  font-size: 0.875rem;
  color: #334155;
  min-width: 180px;
  text-align: center;
}

/* Grid Table specific styling */
.grid-table {
  border-collapse: separate;
  border-spacing: 0;
}

.grid-table th, 
.grid-table td {
  border: 1px solid #e2e8f0;
  border-top: none;
  border-left: none;
}

.grid-table th {
  background-color: #f8fafc;
  color: #475569;
  font-weight: 600;
  text-align: center;
  padding: 1rem;
  vertical-align: middle;
}

.grid-table th:first-child,
.grid-table td:first-child {
  border-left: 1px solid #e2e8f0;
}

.grid-table tr:first-child th {
  border-top: 1px solid #e2e8f0;
}

.date-col-header {
  min-width: 130px;
}

.today-col-header {
  background-color: #f5f3ff !important;
  border-bottom: 2px solid #6366f1 !important;
}

.student-col-header {
  position: sticky;
  left: 0;
  z-index: 3;
  background-color: #f8fafc !important;
  box-shadow: 2px 0 5px -2px rgba(0, 0, 0, 0.05);
  white-space: nowrap;
}

.student-header-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-align: left;
}

.student-avatar-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #6366f1;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.775rem;
  box-shadow: 0 2px 4px rgba(99, 102, 241, 0.15);
  flex-shrink: 0;
}

.student-name {
  color: #0f172a;
  font-size: 0.9rem;
  display: block;
}

.student-id {
  font-size: 0.75rem;
  display: block;
}

.student-cell {
  position: sticky;
  left: 0;
  z-index: 2;
  background-color: white;
  box-shadow: 2px 0 5px -2px rgba(0, 0, 0, 0.05);
  white-space: nowrap;
}

.table-row:hover .student-cell {
  background-color: #f8fafc;
}

.student-cell-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.35rem 0.5rem;
  text-align: left;
  white-space: nowrap;
}

/* Media Query for mobile screen sizes (small phone views) */
@media (max-width: 768px) {
  .student-col-header {
    padding-left: 6px !important;
    padding-right: 6px !important;
  }
  .student-cell {
    padding-left: 6px !important;
    padding-right: 6px !important;
  }
  .student-cell-content {
    padding-left: 0 !important;
    padding-right: 0 !important;
  }
}

.student-info-text {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.15rem;
}

.day-header-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.day-name {
  font-size: 0.9rem;
  color: #1e293b;
}

.day-date {
  font-size: 0.775rem;
}

.today-badge {
  background-color: #6366f1;
  color: white;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.grid-cell {
  padding: 0.75rem !important;
  text-align: center;
  vertical-align: middle;
  transition: background-color 0.2s ease;
}

.today-cell {
  background-color: rgba(99, 102, 241, 0.04) !important;
}

.editable-cell-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: center;
  justify-content: center;
}

.cell-input-group {
  width: 100%;
}

.grid-select {
  width: 100%;
  padding: 0.4rem 0.5rem;
  border-radius: 6px;
  border: 1px solid #cbd5e1;
  background-color: white;
  font-size: 0.8rem;
  color: #334155;
  outline: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.grid-select:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.15);
}

.absence-checkbox-label {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  user-select: none;
  font-size: 0.85rem;
  color: #64748b;
  font-weight: 500;
}

.grid-checkbox {
  width: 18px;
  height: 18px;
  accent-color: #ef4444; /* red for absence */
  cursor: pointer;
}

.readonly-cell-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
}

.badge-stack {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35rem;
}

.absence-badge-static {
  background-color: #fee2e2;
  color: #ef4444;
  border: 1px solid #fca5a5;
  padding: 0.2rem 0.55rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.empty-cell-dash {
  color: #cbd5e1;
  font-weight: bold;
}

/* Monthly grid custom styling */
.monthly-grid-wrapper {
  overflow-x: auto;
  max-width: 100%;
}

.monthly-grid-table {
  min-width: 1200px;
}

.monthly-cell {
  padding: 0.5rem !important;
  text-align: center;
  vertical-align: middle;
  min-width: 45px;
}

.monthly-date-header {
  min-width: 45px;
  padding: 0.5rem !important;
}

.monthly-grade-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: 700;
  border: 1px solid transparent;
}

.present-dot {
  color: #10b981;
  font-weight: bold;
  font-size: 0.95rem;
}

.absence-dot {
  color: #ef4444;
  font-weight: bold;
  font-size: 0.95rem;
}

.month-year-selectors {
  display: flex;
  gap: 0.75rem;
}

.selector-dropdown {
  padding: 0.35rem 2rem 0.35rem 0.75rem;
  font-size: 0.875rem;
  border-radius: 8px;
  border: 1px solid #cbd5e1;
  background-color: white;
  color: #334155;
  cursor: pointer;
  outline: none;
}

.selector-dropdown:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.15);
}

.non-class-day {
  background-color: #f8fafc !important;
  opacity: 0.6;
}

.weekend-col-header {
  background-color: #fee2e2 !important;
}
</style>
