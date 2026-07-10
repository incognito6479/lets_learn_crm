import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Payments from '../views/Payments.vue'
import Login from '../views/Login.vue'
import Students from '../views/Students.vue'
import Teachers from '../views/Teachers.vue'
import Rooms from '../views/Rooms.vue'
import Branches from '../views/Branches.vue'
import Courses from '../views/Courses.vue'
import Groups from '../views/Groups.vue'
import GroupDetail from '../views/GroupDetail.vue'
import DebtList from '../views/DebtList.vue'
import EnrollmentDetail from '../views/EnrollmentDetail.vue'
import Timetable from '../views/Timetable.vue'
import TeacherDetail from '../views/TeacherDetail.vue'
import Notifications from '../views/Notifications.vue'
import Leads from '../views/Leads.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/payments', name: 'Payments', component: Payments },
  { path: '/login', name: 'Login', component: Login },
  { path: '/students', name: 'Students', component: Students },
  { path: '/teachers', name: 'Teachers', component: Teachers },
  { path: '/rooms', name: 'Rooms', component: Rooms },
  { path: '/branches', name: 'Branches', component: Branches },
  { path: '/courses', name: 'Courses', component: Courses },
  { path: '/groups', name: 'Groups', component: Groups },
  { path: '/groups/:id', name: 'GroupDetail', component: GroupDetail },
  { path: '/debts', name: 'DebtList', component: DebtList },
  { path: '/leads', name: 'Leads', component: Leads },
  { path: '/enrollments/:id', name: 'EnrollmentDetail', component: EnrollmentDetail },
  { path: '/timetable', name: 'Timetable', component: Timetable },
  { path: '/teachers/:id', name: 'TeacherDetail', component: TeacherDetail },
  { path: '/notifications', name: 'Notifications', component: Notifications }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Authentication guard
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('auth_token')
  const role = localStorage.getItem('user_role')

  if (to.name !== 'Login' && !isAuthenticated) {
    next({ name: 'Login' })
  } else if (to.name === 'Login' && isAuthenticated) {
    if (role === 'teacher') {
      next({ name: 'Timetable' })
    } else {
      next({ name: 'Home' })
    }
  } else {
    if (isAuthenticated && role === 'teacher') {
      const allowedRoutesForTeacher = ['Timetable', 'Groups', 'GroupDetail', 'EnrollmentDetail', 'Login', 'Notifications']
      if (!allowedRoutesForTeacher.includes(to.name)) {
        next({ name: 'Timetable' })
        return
      }
    }
    next()
  }
})

export default router
