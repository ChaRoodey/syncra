// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
    components: true,
    compatibilityDate: '2025-07-15',
    devtools: {enabled: true},
    css: [
        '~/assets/css/main.css',
        'ant-design-vue/dist/reset.css',
    ],
    modules: [
        '@ant-design-vue/nuxt',
        '@pinia/nuxt',
        'pinia-plugin-persistedstate/nuxt',
    ],
})
