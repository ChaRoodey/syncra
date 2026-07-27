<script setup lang="ts">
import {message} from 'ant-design-vue'

definePageMeta({
    middleware: 'auth'
})

const teamStore = useTeamStore()

const createModal = ref(false)
const joinModal = ref(false)

const teamName = ref('')
const inviteCode = ref('')

const {canManageTeams} = usePermissions()

onMounted(async () => {
    await teamStore.fetchTeams()
})

async function createTeam() {
    if (!teamName.value.trim()) {
        return
    }

    await teamStore.createTeam(teamName.value)

    teamName.value = ''
    createModal.value = false
}

async function joinTeam() {
    try {
        await teamStore.joinTeam(inviteCode.value)

        message.success('Вы успешно присоединились к команде')

        inviteCode.value = ''
    } catch (error) {
    }

    joinModal.value = false
}
</script>

<template>
    <div class="header">
        <a-typography-title :level="2">
            Мои команды
        </a-typography-title>

        <a-space>
            <a-button @click="joinModal = true">
                Присоединиться
            </a-button>

            <a-button v-if="canManageTeams" type="primary" @click="createModal = true">
                Создать команду
            </a-button>
        </a-space>
    </div>

    <a-list bordered :data-source="teamStore.teams" class="team-list">
        <template #renderItem="{ item }">
            <a-list-item class="team-item" @click="navigateTo(`/teams/${item.id}`)">
                <div class="team-name">
                    {{ item.name }}
                </div>

                <RightOutlined/>
            </a-list-item>
        </template>
    </a-list>

    <a-empty v-if="teamStore.teams.length === 0" description="Вы пока не состоите ни в одной команде"/>

    <a-modal v-model:open="createModal" title="Создать команду" @ok="createTeam">
        <a-input v-model:value="teamName" placeholder="Название команды"/>
    </a-modal>

    <a-modal v-model:open="joinModal" title="Присоединиться к команде" @ok="joinTeam">
        <a-input v-model:value="inviteCode" placeholder="Invite code"/>
    </a-modal>
</template>

<style scoped>
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
}

.team-list {
    border-radius: 12px;
    overflow: hidden;
}

.team-item {
    display: flex;
    justify-content: space-between;
    align-items: center;

    cursor: pointer;
    transition: .2s;
}

.team-item:hover {
    background: #fff1f6;
}

.team-name {
    font-size: 16px;
    font-weight: 500;
}
</style>