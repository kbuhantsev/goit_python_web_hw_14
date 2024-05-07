import unittest
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas.schemas import UserSchema
from src.repository.users import (
    create_user,
    get_user_by_email,
    update_token,
    confirmed_email,
    update_avatar,
)


class TestUsersRepository(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.session = AsyncMock(spec=AsyncSession)

    async def test_create_user(self):
        body = UserSchema(
            name="test", email="test@example.com", password="testtest"
        )
        result = await create_user(body=body, db=self.session)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.email, body.email)

    async def test_get_user_by_email(self):
        user = User(
            id=1,
            name="test",
            email="test@example.com",
            password="testtest",
            avatar=None,
            confirmed=True,
        )
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mocked_user
        result = await get_user_by_email(email="test@example.com", db=self.session)
        self.assertEqual(result, user)

    async def test_update_token(self):
        user = User()
        result = await update_token(
            user=user, token="test_update_token", db=self.session
        )
        self.assertEqual(result, None)
        self.assertEqual(user.refresh_token, "test_update_token")

    async def test_confirmed_email(self):
        user = User(
            id=1,
            name="test",
            email="test@example.com",
            password="testtest",
            avatar=None,
            confirmed=False,
        )
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mocked_user
        result = await confirmed_email(email="test@example.com", db=self.session)
        self.assertEqual(result, None)
        self.assertEqual(user.confirmed, True)

    async def test_update_avatar(self):
        user = User(
            id=1,
            name="test",
            email="test@example.com",
            password="testtest",
            avatar=None,
            confirmed=True,
        )
        result = await update_avatar(email=user.email, url="test_url", db=self.session)
        self.assertEqual(result.avatar, "test_url")
