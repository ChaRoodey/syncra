<script setup lang="ts">
const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const selectedKeys = computed(() => {
    if (route.path.startsWith('/teams')) {
        return ['/teams']
    }

    if (route.path.startsWith('/calendar')) {
        return ['/calendar']
    }

    return ['/']
})

function go(path: string) {
    router.push(path)
}
</script>

<template>
    <a-layout class="layout">
        <a-layout-sider v-model:collapsed="collapsed" collapsible class="sider">
            <div class="logo"> Syncra</div>

            <a-menu v-model:selectedKeys="selectedKeys" class="menu" mode="inline">

                <a-menu-item key="/" @click="go('/')">
                    <template #icon>
                        <HomeOutlined/>
                    </template>
                    Dashboard
                </a-menu-item>

                <a-menu-item key="/teams" @click="go('/teams')">
                    <template #icon>
                        <TeamOutlined/>
                    </template>
                    Teams
                </a-menu-item>

                <a-menu-item key="/calendar" @click="go('/calendar')">
                    <template #icon>
                        <CalendarOutlined/>
                    </template>
                    Calendar
                </a-menu-item>

            </a-menu>
        </a-layout-sider>

        <a-layout>
            <a-layout-header class="header">
                <div class="title">
                    Team Manager
                </div>

                <a-button class="logout" @click="auth.logout">
                    Logout
                </a-button>
            </a-layout-header>

            <a-layout-content class="content">
                <div class="page">
                    <slot/>
                </div>
            </a-layout-content>
        </a-layout>
    </a-layout>
</template>

<style scoped>
.layout {
    min-height: 100vh;
    background: #fff5f8;
}

.sider {
    background: linear-gradient(
            180deg,
            #be185d 0%,
            #831843 100%
    );
}

.menu {
    background: transparent;
}

:deep(.ant-menu-item) {
    color: rgba(255, 255, 255, 0.8);
}

:deep(.ant-menu-item:hover) {
    color: white;
}

:deep(.ant-menu-item-selected) {
    background: rgba(255, 255, 255, 0.18) !important;
    color: white !important;
}

.logo {
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: center;

    color: white;
    font-size: 22px;
    font-weight: 700;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    background: white;

    padding: 0 24px;

    border-bottom: 1px solid #fce7f3;
}

.title {
    color: #9d174d;
    font-size: 18px;
    font-weight: 600;
}

.logout {
    background: #db2777;
    border-color: #db2777;
    color: white;
}

.logout:hover {
    background: #be185d !important;
    border-color: #be185d !important;
}

.content {
    margin: 24px;
    background: transparent;
}

.page {
    min-height: calc(100vh - 112px);

    padding: 32px;

    background: white;

    border-radius: 20px;

    box-shadow: 0 10px 30px rgba(190, 24, 93, 0.08);
}

:deep(.ant-card) {
    border-radius: 16px;
    border-color: #fce7f3;
}

:deep(.ant-card:hover) {
    border-color: #db2777;
}
</style>