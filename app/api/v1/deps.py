# from fastapi import Depends
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from app.db.repository import BulletinRepository
# from app.db.session import get_db_session
# from app.services.bulletin_service import BulletinService
# from app.services.cache_service import CacheService, cache_service
#
#
# async def get_repository(session: AsyncSession = Depends(get_db_session)) -> BulletinRepository:
#     return BulletinRepository(session)
#
#
# def get_cache_service() -> CacheService:
#     return cache_service
#
#
# async def get_service(
#         repo: BulletinRepository = Depends(get_repository),
#         cache: CacheService = Depends(get_cache_service)
# ) -> BulletinService:
#     return BulletinService(repo, cache)
# from typing import AsyncGenerator
#
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from app.db.engine import Session
#
#
# async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
#     async with Session() as session:
#         yield session
