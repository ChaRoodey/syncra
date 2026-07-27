from enum import StrEnum


class UserRole(StrEnum):
    USER = "user"
    MANAGER = "manager"
    ADMIN = "admin"


class TaskStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class MeetingStatus(StrEnum):
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
