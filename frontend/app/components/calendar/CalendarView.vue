<script setup lang="ts">
const calendarStore = useCalendarStore()

function getListData(value) {
    return calendarStore.events.filter(event => {
        const date = new Date(event.starts_at ?? event.ends_at)

        return (
            date.getFullYear() === value.year() &&
            date.getMonth() === value.month() &&
            date.getDate() === value.date()
        )
    })
}

function formatTime(value: string) {
    return new Date(value).toLocaleTimeString('ru-RU', {
        hour: '2-digit',
        minute: '2-digit'
    })
}

function formatEventTime(event) {
    if (!event.starts_at) {
        return `до ${formatTime(event.ends_at)}`
    }

    return `${formatTime(event.starts_at)} - ${formatTime(event.ends_at)}`
}

async function changeMonth(date) {
    const from = new Date(
        date.year(),
        date.month(),
        1
    ).toISOString()

    const to = new Date(
        date.year(),
        date.month() + 1,
        0
    ).toISOString()

    await calendarStore.fetchCalendar(from, to)
}
</script>

<template>
    <a-calendar @panelChange="changeMonth">
        <template #dateCellRender="{current}">
            <ul class="events">
                <li
                        v-for="event in getListData(current)"
                        :key="event.id"
                >
                    <a-tag
                            :color="event.type==='task'?'blue':'green'"
                            class="event-tag"
                    >
                        <div>
                            {{ formatEventTime(event) }}
                        </div>
                        <div>
                            {{ event.title }}
                        </div>
                    </a-tag>
                </li>
            </ul>
        </template>
    </a-calendar>
</template>

<style scoped>
.events {
    padding: 0;
    margin: 0;
    list-style: none;
}

.event-tag {
    width: 100%;
    white-space: normal;
    margin-bottom: 4px;
}

.events li {
    margin-bottom: 4px;
}
</style>