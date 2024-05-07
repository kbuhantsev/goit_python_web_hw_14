from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from src.database.models import Contact, User
from src.schemas.schemas import ContactSchema


async def get_contacts(skip: int, limit: int, db: AsyncSession, user: User) -> [Contact]:
    """
    Get all users contacts

    :param skip:
    :param limit:
    :param db:
    :param user:
    :return: contacts
    :rtype: [Contact]
    """
    query = select(Contact).where(Contact.user_id == user.id).offset(skip).limit(limit)
    res = await db.execute(query)
    return res.scalars().all()


async def search_contacts(user: User, db: AsyncSession,
                          name: str = None,
                          surname: str = None,
                          email: str = None,
                          ) -> [Contact]:
    """
    Search users contacts

    :param user:
    :param db:
    :param name:
    :param surname:
    :param email:
    :return: contacts
    :rtype: [Contact]
    """
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
    """
    Get contact by id

    :param user:
    :param contact_id:
    :param db:
    :return: contact
    :rtype: Contact
    """
    query = select(Contact).where(and_(Contact.user_id == user.id, Contact.id == contact_id))
    res = await db.execute(query)
    return res.scalars().first()


async def create_contact(user: User, contact: ContactSchema, db: AsyncSession) -> Contact:
    """
    Create new contact

    :param user:
    :param contact:
    :param db:
    :return: contact
    :rtype: Contact
    """
    contact = Contact(**contact.model_dump(exclude_unset=True), user_id=user.id)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)

    return contact


async def update_contact(user: User, contact_id: int, contact: ContactSchema, db: AsyncSession) -> Contact | None:
    """
    Update contact by id

    :param user:
    :param contact_id:
    :param contact:
    :param db:
    :return: contact
    :rtype: Contact
    """
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
    """
    Delete contact by id

    :param user:
    :param contact_id:
    :param db:
    :return: contact
    :rtype: Contact
    """
    query = select(Contact).where(and_(Contact.user_id == user.id, Contact.id == contact_id))
    res = await db.execute(query)
    contact = res.scalars().first()
    if contact:
        await db.delete(contact)
        await db.flush()
        await db.commit()

    return contact
