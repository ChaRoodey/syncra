import type {
    User,
    LoginPayload,
    RegisterPayload
} from '~/types/auth'


export const useAuthStore = defineStore('auth', () => {
        const api = useApi()
        const user = ref<User | null>(null)
        const accessToken = ref<string | null>(null)
        const initialized = ref(false)

        const isAuthenticated = computed(() => {
            return !!user.value
        })

        const isManager = computed(() => {
            return user.value?.role === 'manager'
        })

        const isAdmin = computed(() => {
            return user.value?.role === 'admin'
        })

        async function login(payload: LoginPayload) {
            const response = await api('/auth/login', {
                method: 'POST',
                body: payload,
            })
            accessToken.value = response.token

            await fetchMe()
        }

        async function register(payload: RegisterPayload) {
            await api('/auth/register', {
                method: 'POST',
                body: payload,
            })
            await navigateTo('/login')
        }

        async function fetchMe() {
            if (!accessToken.value) {
                return
            }

            user.value = await api('/users/me')
        }
        async function logout() {
            try {
                await api('/auth/logout', {
                    method: 'POST',
                })
            } finally {
                user.value = null
                accessToken.value = null

                await navigateTo('/login')
            }
        }

        const init = async () => {
            if (initialized.value) {
                return
            }

            initialized.value = true

            try {
                const response = await api('/auth/refresh', {
                    method: 'POST'
                })

                accessToken.value = response.token

                await fetchMe()

            } catch {
                accessToken.value = null
                user.value = null
            }
        }

        return {
            user,
            accessToken,

            initialized,
            isAuthenticated,
            isManager,
            isAdmin,

            login,
            register,
            fetchMe,
            logout,
            init,
        }
    },
//     {
//     persist: {
//         storage: persistedState.localStorage,
//         pick: [
//             'accessToken',
//             'user'
//         ]
//     }
// }
)