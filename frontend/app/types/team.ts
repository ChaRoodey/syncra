import type {
    User
} from '~/types/auth'

export interface Team {
    id: number
    name: string
    invite_code: string
}

export interface TeamMember extends User {}
