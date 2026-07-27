export const usePermissions = () => {
    const auth = useAuthStore()

    const isAdmin = computed(() => auth.user?.role === 'admin')

    const isManager = computed(() => auth.user?.role === 'manager')

    const canManageTeams = computed(() =>
        isAdmin.value || isManager.value
    )

    const canEvaluate = computed(() =>
        canManageTeams.value
    )

    return {
        isAdmin,
        isManager,
        canManageTeams,
        canEvaluate,
    }
}