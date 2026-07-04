<template>
  <div class="view-container timetable-view-container">
    <div class="view-header">
      <div>
        <h1 class="view-title">{{ $t('timetable.title') }}</h1>
        <p class="view-subtitle">{{ $t('timetable.sub') }}</p>
      </div>
      <div v-if="layout.positionedCards.length" class="badge-count">
        {{ $t('timetable.active_slots', { count: layout.positionedCards.length }) }}
      </div>
    </div>

    <!-- Error/Warning Banner -->
    <div v-if="error" class="info-banner">
      <span>{{ error }}</span>
    </div>

    <!-- Filter Controls -->
    <div class="filter-bar" style="margin-bottom: 1.5rem; display: flex; gap: 1rem; flex-wrap: wrap;">
      <div style="width: 200px;">
        <select v-model="selectedBranch" class="form-input" @change="handleBranchChange">
          <option value="">{{ $t('timetable.filter_branch') }}</option>
          <option v-for="branch in branches" :key="branch.id" :value="branch.id">
            {{ branch.name }}
          </option>
        </select>
      </div>

      <div style="width: 200px;">
        <select v-model="selectedRoom" class="form-input" :disabled="!selectedBranch">
          <option value="">{{ selectedBranch ? $t('timetable.filter_room') : $t('timetable.select_branch_first') }}</option>
          <option v-for="room in filteredRooms" :key="room.id" :value="room.id">
            {{ room.name }}
          </option>
        </select>
      </div>

      <div style="width: 200px;" v-if="userRole !== 'teacher'">
        <select v-model="selectedTeacher" class="form-input">
          <option value="">{{ $t('timetable.filter_teacher') }}</option>
          <option v-for="teacher in teachers" :key="teacher.id" :value="teacher.id">
            {{ teacher.first_name }} {{ teacher.last_name }}
          </option>
        </select>
      </div>
    </div>

    <!-- Timetable Grid Card -->
    <div class="table-card" style="padding: 1.5rem; background: white; overflow-x: auto;">
      <div v-if="loading" class="loading-state" style="padding: 6rem 0;">
        <div class="spinner"></div>
        <span style="margin-top: 1rem; display: block; color: #64748b;">{{ $t('timetable.loading') }}</span>
      </div>

      <div v-else class="timetable-wrapper">
        <div class="timetable-grid" :style="{ gridTemplateRows: `40px repeat(${layout.totalRows}, 50px)` }">
          <!-- Top Left Empty corner -->
          <div class="grid-header-cell day-time-corner">{{ $t('timetable.day_time') }}</div>

          <!-- Day Headers (Row Headers, Column 1) -->
          <div 
            v-for="dh in layout.dayHeaders" 
            :key="dh.name" 
            class="grid-header-cell day-row-header"
            :style="{ gridColumn: 1, gridRowStart: dh.gridRowStart, gridRowEnd: dh.gridRowEnd }"
          >
            {{ dh.name }}
          </div>

          <!-- Background Hourly Grid Lines & Hour Labels (Columns) -->
          <template v-for="(hourLabel, hIndex) in hours" :key="hourLabel">
            <!-- Hour Label Row 1 -->
            <div 
              class="hour-label-cell"
              :class="{ 'last-hour-cell': hIndex === hours.length - 1 }"
              :style="{ gridRow: 1, gridColumnStart: (hIndex * 4) + 2, gridColumnEnd: (hIndex * 4) + 6 }"
            >
              <span class="time-text">{{ hourLabel }}</span>
              <span v-if="hIndex === hours.length - 1" class="time-text">18:00</span>
            </div>
          </template>

          <!-- Hour background cells across rows -->
          <template v-for="rb in layout.rowBackgrounds" :key="'bg-row-' + rb.gridRow">
            <div 
              v-for="(hourLabel, hIndex) in hours" 
              :key="'cell-' + rb.gridRow + '-' + hIndex"
              class="grid-bg-cell"
              :style="{ 
                gridRow: rb.gridRow, 
                gridColumnStart: (hIndex * 4) + 2, 
                gridColumnEnd: (hIndex * 4) + 6 
              }"
            ></div>
          </template>

          <div 
            v-for="card in layout.positionedCards" 
            :key="card.key"
            class="group-schedule-card"
            :style="{
              gridRow: card.gridRow,
              gridColumnStart: card.gridColumnStart,
              gridColumnEnd: card.gridColumnEnd,
              backgroundColor: card.color.bg,
              color: card.color.text,
              borderLeftColor: card.color.border
            }"
            :title="`${card.name}\n👤 ${card.teacherName}\n🏫 ${card.roomName} (${card.branchName})\n🕒 ${card.starts_at} - ${card.ends_at}`"
            @click="navigateToGroup(card.groupId)"
          >
            <span class="group-card-name">{{ card.name }}</span>
            <span class="group-card-teacher">👤 {{ card.teacherName }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Timetable',
  data() {
    return {
      groups: [],
      teachers: [],
      rooms: [],
      branches: [],
      courses: [],
      selectedBranch: '',
      selectedRoom: '',
      selectedTeacher: '',
      loading: false,
      error: null,
      days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
      hours: ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00'],
      userRole: localStorage.getItem('user_role') || '',
      userId: parseInt(localStorage.getItem('user_id')) || null
    }
  },
  computed: {
    filteredRooms() {
      if (!this.selectedBranch) return []
      return this.rooms.filter(r => r.branch === this.selectedBranch)
    },
    layout() {
      // Group cards by day (0 to 5)
      const dayCards = Array.from({ length: 6 }, () => [])
      const dayKeys = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat']
      
      this.groups.forEach(group => {
        if (group.status === 'finished') return
        
        const teacher = this.teachers.find(t => t.id === group.teacher) || {}
        const teacherName = teacher.first_name ? `${teacher.first_name} ${teacher.last_name}` : `${this.$t('groupDetail.teacher')} #${group.teacher}`
        const room = this.rooms.find(r => r.id === group.room) || {}
        const roomName = room.name || `${this.$t('groupDetail.room')} #${group.room}`
        const branch = this.branches.find(b => b.id === group.branch) || {}
        const branchName = branch.name || `${this.$t('groupDetail.branch')} #${group.branch}`

        if (!group.starts_at) return
        const parts = group.starts_at.split(':')
        const startHour = parseInt(parts[0])
        const startMin = parseInt(parts[1])

        const startMinutesTotal = startHour * 60 + startMin
        const endMinutesTotal = startMinutesTotal + parseInt(group.duration || 90)

        if (startMinutesTotal >= 1080 || endMinutesTotal <= 540) return

        const gridColumnStart = Math.max(2, Math.round((startMinutesTotal - 540) / 15) + 2)
        const gridColumnEnd = Math.min(38, Math.round((endMinutesTotal - 540) / 15) + 2)
        if (gridColumnStart >= gridColumnEnd) return

        const formatTimeFromMinutes = (totalMinutes) => {
          const hh = Math.floor(totalMinutes / 60)
          const mm = totalMinutes % 60
          return `${hh.toString().padStart(2, '0')}:${mm.toString().padStart(2, '0')}`
        }

        const formattedStarts = formatTimeFromMinutes(startMinutesTotal)
        const formattedEnds = formatTimeFromMinutes(endMinutesTotal)

        let dayIndexes = []
        const daysStr = group.group_days_at || 'Mon-Wed-Fri'
        if (daysStr === 'Mon-Wed-Fri') {
          dayIndexes = [0, 2, 4]
        } else if (daysStr === 'Tue-Thur-Sat') {
          dayIndexes = [1, 3, 5]
        } else if (daysStr === 'Everyday') {
          dayIndexes = [0, 1, 2, 3, 4, 5]
        }

        const color = this.getGroupColor(group.id)

        dayIndexes.forEach(dayIdx => {
          dayCards[dayIdx].push({
            key: `card-${group.id}-${dayIdx}`,
            groupId: group.id,
            name: group.name,
            teacherId: group.teacher,
            teacherName,
            roomId: group.room,
            roomName,
            branchId: group.branch,
            branchName,
            starts_at: formattedStarts,
            ends_at: formattedEnds,
            startMin: startMinutesTotal,
            endMin: endMinutesTotal,
            gridColumnStart,
            gridColumnEnd,
            dayIdx,
            color
          })
        })
      })

      // Prepare layout arrays
      const dayHeaders = []
      const positionedCards = []
      const rowBackgrounds = []
      let currentGridRow = 2 // Row 1 is header

      for (let dayIdx = 0; dayIdx < 6; dayIdx++) {
        // Filter cards in this day based on active selection filters
        let cardsInDay = dayCards[dayIdx]
        if (this.selectedBranch) {
          cardsInDay = cardsInDay.filter(c => c.branchId === this.selectedBranch)
        }
        if (this.selectedRoom) {
          cardsInDay = cardsInDay.filter(c => c.roomId === this.selectedRoom)
        }
        if (this.selectedTeacher) {
          cardsInDay = cardsInDay.filter(c => c.teacherId === this.selectedTeacher)
        }

        // Sort by starting minutes to do interval scheduling
        cardsInDay.sort((a, b) => a.startMin - b.startMin)

        const lanes = []
        cardsInDay.forEach(card => {
          let placed = false
          for (let l = 0; l < lanes.length; l++) {
            const laneCards = lanes[l]
            const hasOverlap = laneCards.some(lc => {
              return card.startMin < lc.endMin && card.endMin > lc.startMin
            })
            if (!hasOverlap) {
              laneCards.push(card)
              card.laneIdx = l
              placed = true
              break
            }
          }
          if (!placed) {
            lanes.push([card])
            card.laneIdx = lanes.length - 1
          }
        })

        const rowCount = Math.max(1, lanes.length)

        dayHeaders.push({
          name: this.$t('timetable.days.' + dayKeys[dayIdx]),
          gridRowStart: currentGridRow,
          gridRowEnd: currentGridRow + rowCount
        })

        cardsInDay.forEach(card => {
          positionedCards.push({
            ...card,
            gridRow: currentGridRow + card.laneIdx
          })
        })

        for (let r = 0; r < rowCount; r++) {
          rowBackgrounds.push({
            gridRow: currentGridRow + r,
            dayIdx
          })
        }

        currentGridRow += rowCount
      }

      const totalRows = currentGridRow - 2

      return {
        dayHeaders,
        positionedCards,
        rowBackgrounds,
        totalRows
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
        const [groupsRes, usersRes, roomsRes, branchesRes, coursesRes] = await Promise.all([
          axios.get('/api/groups/'),
          axios.get('/api/users/'),
          axios.get('/api/rooms/'),
          axios.get('/api/branches/'),
          axios.get('/api/courses/')
        ])

        let groupsData = groupsRes.data
        if (this.userRole === 'teacher' && this.userId) {
          groupsData = groupsData.filter(g => g.teacher === this.userId)
        }

        this.groups = groupsData
        this.teachers = usersRes.data.filter(u => u.role === 'teacher')
        this.rooms = roomsRes.data
        this.branches = branchesRes.data
        this.courses = coursesRes.data
      } catch (err) {
        console.error('Error fetching timetable data:', err)
        this.error = this.$t('timetable.error_load')
      } finally {
        this.loading = false
      }
    },
    handleBranchChange() {
      this.selectedRoom = ''
    },
    navigateToGroup(id) {
      this.$router.push(`/groups/${id}`)
    },
    getGroupColor(groupId) {
      const colors = [
        { bg: '#e0e7ff', text: '#3730a3', border: '#818cf8' }, // Indigo
        { bg: '#dcfce7', text: '#15803d', border: '#4ade80' }, // Green
        { bg: '#fee2e2', text: '#991b1b', border: '#f87171' }, // Red
        { bg: '#fef3c7', text: '#b45309', border: '#fbbf24' }, // Amber
        { bg: '#fae8ff', text: '#86198f', border: '#e879f9' }, // Fuchsia
        { bg: '#e0f2fe', text: '#0369a1', border: '#38bdf8' }, // Sky
        { bg: '#ffedd5', text: '#9a3412', border: '#fb923c' }, // Orange
        { bg: '#f3e8ff', text: '#6b21a8', border: '#c084fc' }  // Purple
      ]
      return colors[groupId % colors.length]
    }
  }
}
</script>

<style scoped>
@import '../assets/views.css';

.timetable-view-container {
  max-width: 1280px;
}

.timetable-wrapper {
  min-width: 900px;
  position: relative;
}

.timetable-grid {
  display: grid;
  /* Column 1 is Day header (100px). Next 36 columns are 15-min intervals */
  grid-template-columns: 100px repeat(36, 1fr);
  /* Row 1 is Time header (40px). Next 6 rows are Days of week (50px height each) */
  grid-template-rows: 40px repeat(6, 50px);
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  background-color: #ffffff;
  overflow: hidden;
  position: relative;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
}

.grid-header-cell {
  background-color: #f8fafc;
  border-bottom: 2px solid #e2e8f0;
  border-right: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #475569;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.day-time-corner {
  border-right: 2px solid #e2e8f0;
  border-bottom: 2px solid #e2e8f0;
}

.day-row-header {
  border-right: 2px solid #e2e8f0;
  border-bottom: 1px solid #e2e8f0;
}

.hour-label-cell {
  background-color: #f8fafc;
  border-bottom: 2px solid #e2e8f0;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  padding-left: 6px;
  box-sizing: border-box;
}

.hour-label-cell.last-hour-cell {
  justify-content: space-between;
  padding-right: 6px;
}

.time-text {
  font-size: 0.8rem;
  font-weight: 700;
  color: #64748b;
  font-family: monospace;
}

.grid-bg-cell {
  border-right: 1px solid #e2e8f0; /* Hour line dividers */
  border-bottom: 1px solid #f1f5f9; /* Day row dividers */
  box-sizing: border-box;
}

/* Group Overlay Card styling */
.group-schedule-card {
  position: relative;
  z-index: 5;
  margin: 2px;
  padding: 4px 6px;
  border-radius: 6px;
  border-left: 3px solid;
  box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 1px;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  box-sizing: border-box;
  overflow: hidden;
}

.group-schedule-card:hover {
  transform: translateY(-1px) scale(1.01);
  z-index: 10;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
}

.card-top {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.group-card-name {
  font-weight: 700;
  font-size: 0.75rem;
  line-height: 1.1;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.group-card-time {
  font-size: 0.725rem;
  font-weight: 600;
  opacity: 0.85;
  font-family: monospace;
}

.card-bottom {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.group-card-teacher,
.group-card-room {
  font-size: 0.7rem;
  font-weight: 500;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
  opacity: 0.85;
}
</style>
