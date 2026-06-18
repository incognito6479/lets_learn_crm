<template>
  <div class="payments">
    <h1>Payments</h1>
    <table>
      <thead>
        <tr>
          <th>Student</th>
          <th>Amount</th>
          <th>Date</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="payment in payments" :key="payment.id">
          <td>{{ payment.student }}</td>
          <td>{{ payment.amount }}</td>
          <td>{{ payment.payment_date }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      payments: []
    }
  },
  mounted() {
    this.fetchPayments()
  },
  methods: {
    async fetchPayments() {
      try {
        const response = await axios.get('http://localhost:8000/api/payments/')
        this.payments = response.data
      } catch (error) {
        console.error('Error fetching payments:', error)
      }
    }
  }
}
</script>
