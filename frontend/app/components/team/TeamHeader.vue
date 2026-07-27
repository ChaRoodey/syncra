<script setup lang="ts">
const route = useRoute()

const teamStore = useTeamStore()

function copyInvite() {
    if (!teamStore.currentTeam) {
        return
    }

    navigator.clipboard.writeText(inviteCode.value)

    message.success('Invite code copied')
}
</script>

<template>
    <a-card class="header">

        <div class="left">

            <NuxtLink to="/teams">
                ← Назад
            </NuxtLink>

            <a-typography-title :level="2">
                {{ teamStore.currentTeam?.name }}
            </a-typography-title>

        </div>

        <div class="right">

            <a-tag color="pink">
                {{ teamStore.currentTeam?.invite_code }}
            </a-tag>

            <a-button
                    type="primary"
                    @click="copyInvite"
            >
                Копировать
            </a-button>

        </div>

    </a-card>
</template>

<style scoped>
.header {
    margin-bottom: 24px;
}

.header :deep(.ant-card-body) {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.left {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.right {
    display: flex;
    align-items: center;
    gap: 12px;
}
</style>