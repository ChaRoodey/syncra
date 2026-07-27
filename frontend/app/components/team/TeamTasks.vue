<script setup lang="ts">
import TaskComments from "./TaskComments.vue";

const api = useApi()
const route = useRoute()
const teamStore = useTeamStore()
const auth = useAuthStore()

const visible = ref(false)
const selectedTask = ref(null)
const taskModal = ref(false)
const editModal = ref(false)
const deleteModal = ref(false)
const evaluationModal = ref(false)

const teamId = Number(route.params.id)

const {canManageTeams, canEvaluate,} = usePermissions()

const form = reactive({
    title: '',
    description: '',
    due_date: null
})

const editForm = reactive({
    title: '',
    description: '',
    status: '',
    due_date: '',
    assignee_id: null
})

const evaluationForm = reactive({
    score: 5,
    comment: ''
})

const columns = [
    {
        title: 'Название',
        dataIndex: 'title',
        key: 'title'
    },
    {
        title: 'Статус',
        dataIndex: 'status',
        key: 'status'
    },
    {
        title: 'Дедлайн',
        dataIndex: 'due_date',
        key: 'due_date'
    },
    {
        title: 'Исполнитель',
        dataIndex: 'assignee_id',
        key: 'assignee_id'
    },
]

function openTask(task) {
    selectedTask.value = task
    taskModal.value = true
}

function openEdit() {
    editForm.title = selectedTask.value.title
    editForm.description = selectedTask.value.description
    editForm.status = selectedTask.value.status
    editForm.due_date = selectedTask.value.due_date
    editForm.assignee_id = selectedTask.value.assignee_id

    editModal.value = true
}

function openDelete() {
    deleteModal.value = true
}

async function updateTask() {
    const updatedTask = await teamStore.updateTask(
        teamId,
        selectedTask.value.id,
        editForm
    )

    selectedTask.value = updatedTask

    editModal.value = false
}

async function deleteTask() {
    await teamStore.deleteTask(
        teamId,
        selectedTask.value.id
    )

    selectedTask.value = null
    deleteModal.value = false
    taskModal.value = false
}

function openEvaluation() {
    if (selectedTask.value.evaluation) {
        evaluationForm.score = selectedTask.value.evaluation.score
        evaluationForm.comment = selectedTask.value.evaluation.comment || ''
    } else {
        evaluationForm.score = 5
        evaluationForm.comment = ''
    }

    evaluationModal.value = true
}

async function saveEvaluation() {
    const taskId = selectedTask.value.id

    const method = selectedTask.value.evaluation ? 'PATCH' : 'POST'

    const evaluation = await api(`/tasks/${taskId}/evaluation`, {
        method,
        body: {
            score: evaluationForm.score,
            comment: evaluationForm.comment || null
        }
    })

    selectedTask.value.evaluation = evaluation

    const index = teamStore.tasks.findIndex(
        task => task.id === taskId
    )

    if (index !== -1) {
        teamStore.tasks[index].evaluation = evaluation
    }

    evaluationModal.value = false
}

async function submit() {
    const teamId = Number(route.params.id)

    await teamStore.createTask(
        teamId,
        {
            title: form.title,
            description: form.description,
            due_date: form.due_date?.toISOString()
        }
    )

    visible.value = false

    form.title = ''
    form.description = ''
    form.due_date = null
}

function getAssigneeUsername(id: number) {
    return teamStore.members.find(
        member => member.id === id
    )?.username ?? 'Unknown'
}
</script>

<template>
    <div class="tasks-header">
        <a-typography-title :level="3">
            Tasks
        </a-typography-title>

        <a-button
                v-if="canManageTeams"
                type="primary"
                shape="circle"
                @click="visible = true"
        >
            +
        </a-button>
    </div>

    <a-table
            :columns="columns"
            :data-source="teamStore.tasks"
            row-key="id"
            :custom-row="record => ({
                onClick: () => openTask(record)
            })"
    >
        <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'assignee_id'">
                {{ getAssigneeUsername(record.assignee_id) }}
            </template>

            <template v-else-if="column.key === 'status'">
                <a-tag v-if="record.status === 'done'" color="green">
                    Done
                </a-tag>

                <a-tag v-else-if="record.status === 'in_progress'" color="blue">
                    Progress
                </a-tag>

                <a-tag v-else>
                    Open
                </a-tag>
            </template>
        </template>
    </a-table>

    <a-modal
            v-model:open="visible"
            title="Create task"
            @ok="submit"
    >
        <a-form layout="vertical">
            <a-form-item label="Title">
                <a-input v-model:value="form.title"/>
            </a-form-item>

            <a-form-item label="Description">
                <a-textarea v-model:value="form.description"/>
            </a-form-item>

            <a-form-item label="Due date">
                <a-date-picker
                        v-model:value="form.due_date"
                        show-time
                        format="YYYY-MM-DD HH:mm"
                        placeholder="Выберите дату"
                        style="width:100%"
                />
            </a-form-item>

        </a-form>
    </a-modal>

    <a-modal v-model:open="taskModal" :footer="null" width="90%" centered>
        <div v-if="selectedTask" class="task-modal">
            <div class="task-main">
                <a-typography-title :level="3">
                    {{ selectedTask.title }}
                </a-typography-title>
                <a-divider/>
                <a-typography-title :level="5">
                    Description
                </a-typography-title>
                <p>{{ selectedTask.description }}</p>
                <a-divider/>
                <a-typography-title :level="5">
                    Comments
                </a-typography-title>
                <a-card>
                    <TaskComments :task-id="selectedTask.id"/>
                </a-card>
            </div>
            <div v-if="canManageTeams" class="task-actions">
                <a-button @click="openEdit">
                    Изменить
                </a-button>
                <a-button danger @click="openDelete">
                    Удалить
                </a-button>
            </div>
            <div class="task-sidebar">
                <a-card title="Task info">
                    <a-descriptions :column="1" size="small">
                        <a-descriptions-item label="Status">
                            <a-tag>{{ selectedTask.status }}</a-tag>
                        </a-descriptions-item>
                        <a-descriptions-item label="Creator">
                            -
                        </a-descriptions-item>
                        <a-descriptions-item label="Assignee">
                            {{ getAssigneeUsername(selectedTask.assignee_id) }}
                        </a-descriptions-item>
                        <a-descriptions-item label="Deadline">
                            {{ selectedTask.due_date }}
                        </a-descriptions-item>
                    </a-descriptions>
                </a-card>
                <a-card title="Evaluation">
                    <template v-if="selectedTask.evaluation">
                        <div class="stars">
                            <span
                                    v-for="star in 5"
                                    :key="star"
                                    class="star"
                            >
                                {{ star <= selectedTask.evaluation.score ? '★' : '☆' }}
                            </span>
                        </div>
                        <p> {{ selectedTask.evaluation.comment || 'Без комментария' }} </p>

                        <a-button
                                v-if="canEvaluate"
                                type="link"
                                @click="openEvaluation"
                        >
                            Изменить
                        </a-button>
                    </template>

                    <template v-else>
                        <a-button
                                v-if="canEvaluate"
                                type="primary"
                                size="small"
                                @click="openEvaluation"
                        >
                            Добавить оценку
                        </a-button>

                        <a-empty v-else description="Оценки пока нет"/>
                    </template>
                </a-card>
            </div>
        </div>
    </a-modal>

    <a-modal v-model:open="editModal" title="Edit task" @ok="updateTask">
        <a-form layout="vertical">
            <a-form-item label="Title">
                <a-input v-model:value="editForm.title"/>
            </a-form-item>
            <a-form-item label="Description">
                <a-textarea v-model:value="editForm.description"/>
            </a-form-item>
            <a-form-item label="Status">
                <a-select v-model:value="editForm.status">
                    <a-select-option value="open">
                        Open
                    </a-select-option>
                    <a-select-option value="in_progress">
                        Progress
                    </a-select-option>
                    <a-select-option value="done">
                        Done
                    </a-select-option>
                </a-select>
            </a-form-item>
            <a-form-item label="Deadline">
                <a-input v-model:value="editForm.due_date"/>
            </a-form-item>
            <a-form-item label="Assignee">
                <a-select v-model:value="editForm.assignee_id">
                    <a-select-option
                            v-for="member in teamStore.members"
                            :key="member.id"
                            :value="member.id"
                    >
                        {{ member.username }}
                    </a-select-option>
                </a-select>
            </a-form-item>
        </a-form>
    </a-modal>

    <a-modal
            v-model:open="deleteModal"
            title="Delete task?"
            ok-text="Delete"
            cancel-text="Cancel"
            @ok="deleteTask"
    >
        Вы уверены, что хотите удалить задачу?
    </a-modal>

    <a-modal
            v-model:open="evaluationModal"
            title="Evaluation"
            @ok="saveEvaluation"
    >
        <a-form layout="vertical">
            <a-form-item label="Score">
                <div class="stars">
                    <span
                            v-for="star in 5"
                            :key="star"
                            class="star"
                            @click="evaluationForm.score=star"
                    >
                        {{ star <= evaluationForm.score ? '★' : '☆' }}
                    </span>
                </div>
            </a-form-item>

            <a-form-item label="Comment">
                <a-textarea
                        v-model:value="evaluationForm.comment"
                        :maxlength="255"
                />
            </a-form-item>
        </a-form>
    </a-modal>
</template>

<style scoped>
.tasks-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.task-modal {
    display: flex;
    gap: 24px;
    min-height: 600px;
}

.task-main {
    flex: 7;
    overflow: auto;
}

.task-sidebar {
    flex: 3;
}

.task-sidebar .ant-card {
    width: 100%;
}

.evaluation-card {
    margin-top: 16px;
}

.task-actions {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
}

.stars {
    display: flex;
    gap: 4px;
}

.star {
    font-size: 28px;
    cursor: pointer;
    color: #faad14;
}
</style>