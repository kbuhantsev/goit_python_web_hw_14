import unittest
from unittest.mock import MagicMock, AsyncMock

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, Contact
from src.repository.contacts import get_contacts, create_contact, update_contact, delete_contact
from src.schemas.schemas import ContactSchema


class TestContactsRepository(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.user = User(
            id=1,
            name="unittest",
            email="unittest@gmail.com",
            password="superpassword",
            avatar=None,
            confirmed=True,
        )

    async def test_create_contact(self):
        body = ContactSchema(
            name="name",
            surname="surname",
            email="name_surname@example.com",
            phone="+380000000000",
            date_of_birth="2022-07-07",
        )
        result = await create_contact(user=self.user, contact=body, db=self.session)
        print("result", result)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.surname, body.surname)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.date_of_birth, body.date_of_birth)

    async def test_update_contact(self) -> None:
        contact = Contact(
            id=1,
            name="test",
            surname="test",
            email="test@example.com",
            phone="+380000000000",
            date_of_birth="2022-07-07",
            user_id=self.user.id,
        )
        body = ContactSchema(
            name="test",
            surname="test",
            email="test@example.com",
            phone="+380111111111",
            date_of_birth="2022-07-07",
        )
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await update_contact(self.user, contact.id, body, self.session)
        self.assertEqual(result.phone, body.phone)

    async def test_delete_existing_contact(self) -> None:
        contact = Contact(
            id=1,
            name="test",
            surname="test",
            email="test@example.com",
            phone="+380000000000",
            date_of_birth="2022-07-07",
            user_id=self.user.id,
        )
        mocked_contact = MagicMock()
        mocked_contact.scalars.return_value.first.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await delete_contact(self.user, contact.id, self.session)
        self.assertEqual(result, contact)

    async def test_get_contacts(self) -> None:
        limit = 10
        offset = 0
        contacts = [
            Contact(
                id=1,
                name="test",
                surname="test",
                email="test@example.com",
                phone="+380000000000",
                date_of_birth="2022-07-07",
                user_id=self.user.id,
            ),
            Contact(
                id=2,
                name="test_2",
                surname="test_2",
                email="test_2@example.com",
                phone="+380000000000",
                date_of_birth="2021-05-06",
                user_id=self.user.id,
            ),
            Contact(
                id=3,
                name="test_3",
                surname="test_3",
                email="test_3@example.com",
                phone="+380000000000",
                date_of_birth="2021-05-06",
                user_id=self.user.id,
            ),
            Contact(
                id=4,
                name="test_4",
                surname="test_4",
                email="test_4@example.com",
                phone="+380000000000",
                date_of_birth="2021-05-06",
                user_id=None,
            )
        ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts(
            skip=offset, limit=limit, db=self.session, user=self.user
        )
        print(result)
        self.assertEqual(result, contacts)


if __name__ == '__main__':
    unittest.main()
