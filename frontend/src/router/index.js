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
  { path: '/enrollments/:id', name: 'EnrollmentDetail', component: EnrollmentDetail }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Authentication guard
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('auth_token')
  if (to.name !== 'Login' && !isAuthenticated) {
    next({ name: 'Login' })
  } else if (to.name === 'Login' && isAuthenticated) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
