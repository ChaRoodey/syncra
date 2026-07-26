from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    calendar,
    task_comments,
    task_evaluations,
    team_meetings,
    team_tasks,
    teams,
    users,
)

router = APIRouter(
    prefix="/api/v1",
)

router.include_router(auth.router)
router.include_router(users.router)
router.include_router(task_comments.router_comments)
router.include_router(task_evaluations.router)
router.include_router(team_tasks.router_tasks)
router.include_router(team_meetings.router_meeting)
router.include_router(calendar.router)
router.include_router(teams.router)
