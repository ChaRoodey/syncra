export type UserRole = 'user' | 'manager' | 'admin'


export interface User {
  id: number
  username: string
  email: string
  role: UserRole
}


export interface LoginPayload {
  username: string
  password: string
}


export interface RegisterPayload extends LoginPayload {
  email: string
  first_name: string
  last_name: string
}