<script setup lang="ts">
const teamStore = useTeamStore()

const managers = computed(() =>
    teamStore.members.filter(member => member.role === 'manager')
)

const admins = computed(() =>
    teamStore.members.filter(member => member.role === 'admin')
)

const members = computed(() =>
    teamStore.members.filter(member => member.role === 'user')
)
</script>

<template>
    <a-typography-title :level="4">
        Участники
    </a-typography-title>

    <a-divider/>

    <template v-if="admins.length">

        <a-typography-title :level="5">
            👑 Admins
        </a-typography-title>

        <a-list size="small" :data-source="admins">
            <template #renderItem="{ item }">
                <a-list-item>
                    {{ item.username }}
                </a-list-item>
            </template>
        </a-list>

        <a-divider/>

    </template>

    <template v-if="managers.length">

        <a-typography-title :level="5">
            🛡 Managers
        </a-typography-title>

        <a-list size="small" :data-source="managers">
            <template #renderItem="{ item }">
                <a-list-item>
                    {{ item.username }}
                </a-list-item>
            </template>
        </a-list>

        <a-divider/>

    </template>

    <a-typography-title :level="5">
        👤 Members
    </a-typography-title>

    <a-list size="small" :data-source="members">
        <template #renderItem="{ item }">
            <a-list-item>
                {{ item.username }}
            </a-list-item>
        </template>
    </a-list>
</template>

<style scoped>

</style>