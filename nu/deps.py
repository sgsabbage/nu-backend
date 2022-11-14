import datetime
from typing import AsyncGenerator, Optional

from fastapi import Cookie, Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nu.core.config import settings
from nu.core.models import Player
from nu.db.session import SessionLocal


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def get_player(
    cookie: str = Cookie(None, alias=settings.API_COOKIE_KEY),
) -> Optional[Player]:
    if not cookie:
        return None
    try:
        payload = jwt.decode(
            cookie,
            settings.SECRET_KEY,
            algorithms=settings.JWT_ALGORITHM,
            options={
                "require_iat": True,
                "require_sub": True,
                "require_exp": True,
                "require_jti": True,
            },
        )
    except JWTError:
        return None

    if payload["exp"] < datetime.datetime.now().timestamp():
        return None
    async with SessionLocal.begin() as session:
        result = await session.execute(
            select(Player).filter(Player.id == payload["sub"])
        )

    return result.scalar_one_or_none()


async def require_player(player: Player = Depends(get_player)) -> Player:
    if player is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    return player
