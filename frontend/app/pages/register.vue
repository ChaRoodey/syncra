<script setup lang="ts">
import type {
    RegisterPayload
} from '~/types/auth'

definePageMeta({
    layout: 'auth',
    middleware: 'guest'
})

const auth = useAuthStore()

const form = reactive<RegisterPayload>({
    username: '',
    password: '',
    email: '',
    first_name: '',
    last_name: '',
})

const submit = async () => {
    try {
        await auth.register(form)
        await navigateTo('/login')
    } catch (error) {
        console.error(error)
    }
}
</script>

<template>
    <a-card title="Регистрация" class="auth-card">
        <a-form layout="vertical" :model="form" @finish="submit">

            <a-form-item label="Username" name="username" :rules="[{
                    required: true,
                    message: 'Введите username'
                  }]">
                <a-input v-model:value="form.username" placeholder="username"/>
            </a-form-item>

            <a-form-item label="Email" name="email" :rules="[{
                    required: true,
                    type: 'email',
                    message: 'Введите корректный email'
                  }]">
                <a-input v-model:value="form.email" placeholder="email@example.com"/>
            </a-form-item>

            <a-form-item label="Имя" name="first_name">
                <a-input v-model:value="form.first_name" placeholder="Имя"/>
            </a-form-item>

            <a-form-item label="Фамилия" name="last_name">
                <a-input v-model:value="form.last_name" placeholder="Фамилия"/>
            </a-form-item>

            <a-form-item label="Пароль" name="password" :rules="[{
                required: true,
                message: 'Введите пароль'
            }]">
                <a-input-password v-model:value="form.password" placeholder="Пароль"/>
            </a-form-item>

            <a-button type="primary" html-type="submit" block>
                Создать аккаунт
            </a-button>

        </a-form>

        <div class="footer">
            Уже есть аккаунт?

            <NuxtLink to="/login">
                Войти
            </NuxtLink>
        </div>

    </a-card>
</template>

<style scoped>
.auth-card {
    width: 400px;
}

.footer {
    margin-top: 16px;
    text-align: center;
}
</style>