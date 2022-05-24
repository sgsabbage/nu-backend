import uuid
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response
from jose import jwt
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from nu.core.config import settings
from nu.deps import get_session
from nu.models import Player

router = APIRouter()


class LoginSchema(BaseModel):
    username: str
    password: str


@router.post("/login")
async def root(
    login: LoginSchema, response: Response, session: AsyncSession = Depends(get_session)
) -> Any:

    result = await session.execute(
        select(Player)
        .options(selectinload(Player.characters))
        .filter(Player.username == login.username)
    )

    player = result.scalar_one_or_none()

    if player is None or not player.password == login.password:
        raise HTTPException(status_code=403)

    payload = {
        "sub": str(player.id),
        "iat": datetime.now(),
        "exp": datetime.now() + timedelta(seconds=settings.TOKEN_EXPIRY_SECONDS),
        "jti": str(uuid.uuid4()),
    }

    response.set_cookie(
        key=settings.API_COOKIE_KEY,
        httponly=True,
        samesite="lax",
        secure=False,
        value=jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256"),
    )

    return {}
