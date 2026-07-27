import {notification} from 'ant-design-vue'

export const useApi = () => {
    return async <T>(
        url: string,
        options: any = {}
    ) => {
        const auth = useAuthStore()

        try {
            return await $fetch<T>(url, {
                baseURL: "http://localhost:8000/api/v1",
                ...options,
                headers: {
                    ...options.headers,
                    Authorization: auth.accessToken
                        ? `Bearer ${auth.accessToken}`
                        : undefined,
                },
                credentials: "include",
            })
        } catch (error: any) {
            const detail = error.data?.detail || "Произошла ошибка"

            notification.error({
                message: "Ошибка",
                description: Array.isArray(detail)
                    ? detail.map(e => e.msg).join(", ")
                    : detail
            })

            throw error
        }
    }
}