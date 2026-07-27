<script setup lang="ts">
import {message} from 'ant-design-vue'

const route = useRoute()
const teamStore = useTeamStore()
const {canManageTeams} = usePermissions()

const visible = ref(false)

const teamId = Number(route.params.id)

const form = reactive({
    title: '',
    description: '',
    starts_at: '',
    ends_at: ''
})

const columns = [
    {
        title: 'Название',
        dataIndex: 'title',
        key: 'title'
    },
    {
        title: 'Начало',
        dataIndex: 'starts_at',
        key: 'starts_at'
    },
    {
        title: 'Конец',
        dataIndex: 'ends_at',
        key: 'ends_at'
    }
]

async function submit() {
    await teamStore.createMeeting(
        teamId,
        {
            title: form.title,
            description: form.description,
            starts_at: form.starts_at.format(),
            ends_at: form.ends_at.format()
        }
    )

    message.success('Митинг создан')

    visible.value = false

    form.title = ''
    form.description = ''
    form.starts_at = ''
    form.ends_at = ''
}
</script>

<template>
    <div class="meetings-header">
        <a-typography-title :level="3">
            Meetings
        </a-typography-title>

        <a-button
                v-if="canManageTeams"
                type="primary"
                shape="circle"
                @click="visible=true"
        >
            +
        </a-button>
    </div>

    <a-table
            :columns="columns"
            :data-source="teamStore.meetings"
            row-key="id"
    />

    <a-modal
            v-model:open="visible"
            title="Create meeting"
            @ok="submit"
    >
        <a-form layout="vertical">

            <a-form-item label="Title">
                <a-input v-model:value="form.title"/>
            </a-form-item>


            <a-form-item label="Description">
                <a-textarea v-model:value="form.description"/>
            </a-form-item>


            <a-form-item label="Start">
                <a-date-picker
                        v-model:value="form.starts_at"
                        show-time
                />
            </a-form-item>


            <a-form-item label="End">
                <a-date-picker
                        v-model:value="form.ends_at"
                        show-time
                />
            </a-form-item>

        </a-form>

    </a-modal>
</template>

<style scoped>
.meetings-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 24px;
}
</style>