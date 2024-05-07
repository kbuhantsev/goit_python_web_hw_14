from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from libgravatar import Gravatar

from src.database.models import User
from src.schemas.schemas import UserSchema


async def get_user_by_email(email: str, db: AsyncSession):
    """
    Get user by email

    :param email:
    :param db:
    :return: user
    :rtype: User
    """
    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    return user


async def create_user(body: UserSchema, db: AsyncSession):
    """
    Create new user

    :param body:
    :param db:
    :return: user
    :rtype: User
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.model_dump(exclude_defaults=True))
    new_user.avatar = avatar
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession):
    """
    Update user token

    :param user:
    :param token:
    :param db:
    :return:
    :rtype:
    """
    user.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    Confirmed email

    :param email:
    :param db:
    :return:
    :rtype:
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()
    await db.refresh(user)


async def update_avatar(email, url: str, db: AsyncSession) -> User:
    """
    Update user avatar

    :param email:
    :param url:
    :param db:
    :return: user
    :rtype: User
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user
