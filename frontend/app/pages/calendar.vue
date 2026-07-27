<script setup lang="ts">
definePageMeta({
    middleware: 'auth'
})

const calendarStore = useCalendarStore()

onMounted(async () => {
    const now = new Date()

    const from = new Date(
        now.getFullYear(),
        now.getMonth(),
        1
    ).toISOString()

    const to = new Date(
        now.getFullYear(),
        now.getMonth() + 1,
        0
    ).toISOString()

    await calendarStore.fetchCalendar(from, to)
})
</script>

<template>
    <a-card>
        <CalendarView/>
    </a-card>
</template>