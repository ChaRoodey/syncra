from datetime import datetime

from app.repositories.meeting import MeetingRepository
from app.repositories.task import TaskRepository
from app.schemas.calendar import CalendarSchema


class CalendarService:
    def __init__(
        self,
        task_repo: TaskRepository,
        meeting_repo: MeetingRepository,
    ):
        self.task_repo = task_repo
        self.meeting_repo = meeting_repo

    async def get_calendar(
        self, user_id: int, start: datetime, end: datetime
    ) -> list[CalendarSchema]:
        tasks = await self.task_repo.get_all_tasks_by_assignee_id(user_id, start, end)
        meetings = await self.meeting_repo.get_all_meetings_by_participant_id(
            user_id, start, end
        )

        data = []

        for meeting in meetings:
            data.append(
                CalendarSchema(
                    id=meeting.id,
                    team_id=meeting.team_id,
                    type="meeting",
                    title=meeting.title,
                    starts_at=meeting.starts_at,
                    ends_at=meeting.ends_at,
                )
            )

        for task in tasks:
            data.append(
                CalendarSchema(
                    id=task.id,
                    team_id=task.team_id,
                    type="task",
                    title=task.title,
                    starts_at=None,
                    ends_at=task.due_date,
                )
            )

        data.sort(
            key=lambda event: event.starts_at if event.starts_at else event.ends_at
        )

        return data
