export const useCalendarStore = defineStore('calendar', () => {
    const api = useApi()

    const events = ref([])

    async function fetchCalendar(from: string, to: string) {
        events.value = await api('/calendar', {
            params: {
                from,
                to
            }
        })
    }

    return {
        events,
        fetchCalendar
    }
})