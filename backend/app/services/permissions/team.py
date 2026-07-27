from fastapi import HTTPException, status

from app.models.team import TeamModel
from app.repositories.team import TeamRepository


class TeamPermissionService:
    def __init__(self, team_repo: TeamRepository):
        self.team_repo = team_repo

    async def require_membership(self, team_id: int, user_id: int) -> None:
        if not await self.team_repo.is_member(team_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User are not a team member",
            )

    async def require_team(self, team_id: int) -> TeamModel | None:
        team = await self.team_repo.get_by_id(team_id)

        if team is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found",
            )

        return team
