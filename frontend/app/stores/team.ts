import type {
    Team,
    TeamMember
} from '~/types/team'

import type {
    Task,
    TaskCreate
} from '~/types/task'

export const useTeamStore = defineStore('team', () => {
        const api = useApi()

        const teams = ref<Team[]>([])
        const tasks = ref<Task[]>([])
        const currentTeam = ref<Team | null>(null)
        const members = ref<TeamMember[]>([])
        const meetings = ref([])

        async function fetchTasks(teamId: number) {
            tasks.value = await api(`/teams/${teamId}/tasks`)
        }

        async function createTask(
            teamId: number,
            data: TaskCreate
        ) {
            const task = await api(`/teams/${teamId}/tasks`, {
                method: 'POST',
                body: data
            })

            tasks.value.push(task)

            return task
        }

        async function fetchTeams() {
            teams.value = await api('/teams')
        }

        async function fetchTeam(teamId: number) {
            currentTeam.value = await api(`/teams/${teamId}`)
        }

        async function joinTeam(inviteCode: string) {
            const team = await api('/teams/join', {
                method: 'POST',
                body: {
                    invite_code: inviteCode
                }
            })

            await fetchTeams()

            return team
        }

        async function fetchMembers(teamId: number) {
            members.value = await api(`/teams/${teamId}/members`)
        }

        async function createTeam(name: string) {
            const team = await api('/teams', {
                method: 'POST',
                body: {
                    name
                }
            })

            teams.value.push(team)

            return team
        }

        async function updateTask(teamId: number, taskId: number, data: any) {
            const task = await api(`/teams/${teamId}/tasks/${taskId}`, {
                method: 'PATCH',
                body: data
            })

            const index = tasks.value.findIndex(t => t.id === taskId)

            if (index !== -1) {
                tasks.value[index] = task
            }

            return task
        }

        async function deleteTask(teamId: number, taskId: number) {
            await api(`/teams/${teamId}/tasks/${taskId}`, {
                method: 'DELETE'
            })

            tasks.value = tasks.value.filter(t => t.id !== taskId)
        }

        async function fetchMeetings(teamId: number) {
            meetings.value = await api(`/teams/${teamId}/meetings`)
        }

        async function createMeeting(teamId: number, data: any) {
            const meeting = await api(`/teams/${teamId}/meetings`, {
                method: 'POST',
                body: data
            })

            meetings.value.push(meeting)

            return meeting
        }

        return {
            tasks,
            teams,
            members,
            currentTeam,
            meetings,
            fetchTasks,
            createTask,
            fetchTeams,
            fetchTeam,
            joinTeam,
            createTeam,
            fetchMembers,

            updateTask,
            deleteTask,

            fetchMeetings,
            createMeeting,
        }
    }
)