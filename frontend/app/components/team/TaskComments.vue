<script setup lang="ts">
const props = defineProps<{
    taskId: number
}>()

const auth = useAuthStore()
const api = useApi()

const comments = ref([])
const text = ref('')
const editingId = ref<number | null>(null)
const editText = ref('')
const focused = ref(false)

async function fetchComments() {
    comments.value = await api(`/tasks/${props.taskId}/comments`)
}

async function createComment() {
    if (!text.value.trim())
        return

    const comment = await api(`/tasks/${props.taskId}/comments`, {
        method: 'POST',
        body: {text: text.value}
    })

    comments.value.push(comment)
    text.value = ''
    focused.value = false
}

function startEdit(comment) {
    editingId.value = comment.id
    editText.value = comment.text
}

async function updateComment(id: number) {
    const comment = await api(`/tasks/${props.taskId}/comments/${id}`, {
        method: 'PATCH',
        body: {
            text: editText.value
        }
    })

    const index = comments.value.findIndex(c => c.id === id)

    if (index !== -1)
        comments.value[index] = comment

    editingId.value = null
}

async function deleteComment(id: number) {
    await api(`/tasks/${props.taskId}/comments/${id}`, {
        method: 'DELETE'
    })

    comments.value = comments.value.filter(c => c.id !== id)
}

function isOwner(comment) {
    return comment.author_id === auth.user?.id
}

onMounted(fetchComments)
</script>

<template>
    <div class="comments">
        <div class="comment-input">
            <div class="input-wrapper">
                <a-textarea
                        v-model:value="text"
                        placeholder="Написать комментарий..."
                        :auto-size="focused ? {minRows:3,maxRows:5}:{minRows:1,maxRows:1}"
                        :maxlength="255"
                        @focus="focused=true"
                />
                <transition name="slide">
                    <a-button
                            v-if="text.trim()"
                            class="send-button"
                            type="primary"
                            @click="createComment"
                    >
                        →
                    </a-button>
                </transition>
            </div>
        </div>

        <a-divider/>

        <a-list :data-source="comments">
            <template #renderItem="{item}">
                <a-list-item>
                    <div class="comment-wrapper">
                        <div class="comment-card">
                            {{ item.text }}
                        </div>

                        <div v-if="isOwner(item)" class="comment-actions">
                            <a-button
                                    type="link"
                                    size="small"
                                    @click="startEdit(item)"
                            >
                                Изменить
                            </a-button>

                            <a-button
                                    type="link"
                                    danger
                                    size="small"
                                    @click="deleteComment(item.id)"
                            >
                                Удалить
                            </a-button>
                        </div>
                    </div>
                </a-list-item>
            </template>
        </a-list>

    </div>
</template>
<style scoped>
.comment-input {
    margin-bottom:16px;
}

.input-wrapper {
    display:flex;
    align-items:stretch;
    gap:8px;
}

.input-wrapper textarea {
    border-radius:10px;
}

.send-button {
    width:44px;
    height:auto;
    padding:0;
    font-size:20px;
    display:flex;
    align-items:center;
    justify-content:center;
    border-radius:10px;
}

.comment-wrapper {
    width:100%;
}

.comment-card {
    border:1px solid #d9d9d9;
    border-radius:12px;
    padding:12px 16px;
}

.comment-actions {
    display:flex;
    gap:4px;
    margin-top:4px;
}

.slide-enter-active,
.slide-leave-active {
    transition:all .2s ease;
}

.slide-enter-from,
.slide-leave-to {
    opacity:0;
    transform:translateX(-10px);
}
</style>