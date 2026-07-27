<script setup lang="ts">
import type {LoginPayload} from '~/types/auth'

definePageMeta({
    layout: 'auth',
    middleware: 'guest',
})

const auth = useAuthStore()

const form = reactive<LoginPayload>({
    username: '',
    password: '',
})

const submit = async () => {
    await auth.login(form)
    await navigateTo('/')
}
</script>

<template>
    <a-card title="Login" class="auth-card">
        <a-form layout="vertical" :model="form" @finish="submit">
            <a-form-item label="Username" name="username">
                <a-input v-model:value="form.username"/>
            </a-form-item>

            <a-form-item label="Password" name="password">
                <a-input-password v-model:value="form.password"/>
            </a-form-item>

            <a-button type="primary" html-type="submit" block>
                Login
            </a-button>
        </a-form>

        <div class="footer">
            Нет аккаунта?

            <NuxtLink to="/register">
                Регистрация
            </NuxtLink>
        </div>

    </a-card>

</template>

<style scoped>
    .auth-card {
        width: 400px;
        border-radius: 16px;
        backdrop-filter: blur(10px);
        box-shadow: 0 10px 30px rgba(233, 30, 99, 0.2);
    }

    .footer {
        margin-top: 16px;
        text-align: center;
    }
</style>