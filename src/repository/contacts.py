from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from src.database.models import Contact, User
from src.schemas.schemas import ContactSchema


async def get_contacts(skip: int, limit: int, db: AsyncSession, user: User) -> [Contact]:
    query = select(Contact).where(Contact.user_id == user.id).offset(skip).limit(limit)
    res = await db.execute(query)
    return res.scalars().all()


async def search_contacts(user: User, db: AsyncSession,
                          name: str = None,
                          surname: str = None,
                          email: str = None,
                          ) -> [Contact]:

    params = {}
    if name:
        params['name'] = name
    if surname:
        params['surname'] = surname
    if email:
        params['email'] = email

    query = select(Contact).where(Contact.user_id == user.id).filter_by(**params)
    res = await db.execute(query)
    return res.scalars().all()


async def get_contact(user: User, contact_id: int, db: AsyncSession) -> Contact:
    query = select(Contact).where(and_(Contact.user_id == user.id, Contact.id == contact_id))
    res = await db.execute(query)
    return res.scalars().first()


async def create_contact(user: User, contact: ContactSchema, db: AsyncSession) -> Contact:
    contact = Contact(**contact.dict(), user_id=user.id)
    db.add(contact)
    # await db.flush()
    await db.commit()
    await db.refresh(contact)

    return contact


async def update_contact(user: User, contact_id: int, contact: ContactSchema, db: AsyncSession) -> Contact | None:
    # contact_db = await db.get(Contact, contact_id)
    query = select(Contact).where(and_(Contact.user_id == user.id, Contact.id == contact_id))
    res = await db.execute(query)
    contact_db = res.scalars().first()
    if contact_db:
        dump = contact.model_dump(exclude_unset=True)
        for key in dump:
            setattr(contact_db, key, dump[key])

        await db.commit()
        await db.refresh(contact_db)

    return contact_db


async def delete_contact(user: User, contact_id: int, db: AsyncSession) -> Contact | None:
    # contact = await db.get(Contact, contact_id)
    query = select(Contact).where(and_(Contact.user_id == user.id, Contact.id == contact_id))
    res = await db.execute(query)
    contact = res.scalars().first()
    if contact:
        await db.delete(contact)
        await db.flush()
        await db.commit()

    return contact
