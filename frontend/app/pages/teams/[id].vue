<script setup lang="ts">
definePageMeta({
    middleware: 'auth'
})

const route = useRoute()
const teamStore = useTeamStore()

onMounted(async () => {
    const teamId = Number(route.params.id)

    await Promise.all([
        teamStore.fetchTeam(teamId),
        teamStore.fetchMembers(teamId),
        teamStore.fetchTasks(teamId),
        teamStore.fetchMeetings(teamId),
    ])
})
</script>

<template>
<TeamHeader/>

    <a-layout class="team-layout">

        <a-layout-content class="content">
            <TeamTasks/>
            <TeamMeetings/>
        </a-layout-content>

        <a-layout-sider
            width="300"
            class="sider"
        >
            <TeamMembers/>
        </a-layout-sider>

    </a-layout>
</template>

<style scoped>
.team-layout {
    background: transparent;
    gap: 24px;
}

.content {
    background: white;
    border-radius: 12px;
    padding: 24px;
}

.sider {
    background: white;
    border-radius: 12px;
    padding: 24px;
}
</style>