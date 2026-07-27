export type TaskStatus =
    | 'open'
    | 'in_progress'
    | 'done'


export interface Task {
    id: number
    team_id: number
    assignee_id: number

    title: string
    description: string

    due_date: string
    status: TaskStatus

    created_at: string
}


export interface TaskCreate {
    title: string
    description: string
    due_date: string
}