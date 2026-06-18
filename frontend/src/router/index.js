import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Payments from '../views/Payments.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/payments', name: 'Payments', component: Payments },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
