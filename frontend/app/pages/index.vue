<script setup lang="ts">
definePageMeta({
    layout: 'default',
    middleware: 'auth'
})

const auth = useAuthStore()

const cards = [
    {
        title: 'Teams',
        description: 'Управление командами',
        route: '/teams'
    },
    {
        title: 'Calendar',
        description: 'Календарь встреч и задач',
        route: '/calendar'
    },
    {
        title: 'Profile',
        description: 'Личный кабинет',
        route: '/profile'
    }
]
</script>

<template>
    <div>
        <div class="header">
            <div>
                <a-typography-title> Добро пожаловать в Syncra</a-typography-title>

                <a-typography-paragraph>
                    Здравствуйте,
                    <strong>{{ auth.user?.username }}</strong>
                </a-typography-paragraph>

                <a-tag color="blue"> {{ auth.user?.role }}</a-tag>
            </div>


        </div>

        <a-divider/>

        <a-row :gutter="[16, 16]">
            <a-col
                    v-for="card in cards"
                    :key="card.route"
                    :xs="24"
                    :md="12"
                    :lg="8"
            >
                <a-card hoverable @click="navigateTo(card.route)">
                    <a-card-meta :title="card.title" :description="card.description"/>
                </a-card>

            </a-col>
        </a-row>
    </div>
</template>

<style scoped>
.header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;

    gap: 20px;
}
</style>