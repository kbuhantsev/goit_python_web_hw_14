from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User
from src.schemas.schemas import ContactSchema, ContactSchemaResponse
from src.repository import contacts as contacts_repo
from src.services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=["contacts"])


@router.get("/",
            response_model=List[ContactSchemaResponse],
            description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_contacts(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)):
    contacts = await contacts_repo.get_contacts(skip, limit, db, current_user)
    return contacts


@router.get("/search",
            response_model=List[ContactSchemaResponse],
            description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))]
            )
async def search_contacts(name: str = None,
                          surname: str = None,
                          email: str = None,
                          db: AsyncSession = Depends(get_db),
                          current_user: User = Depends(auth_service.get_current_user)):
    tags = await contacts_repo.search_contacts(current_user, db, name, surname, email)
    return tags


@router.get("/{contact_id}",
            response_model=ContactSchemaResponse,
            description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_contact_by_id(
        contact_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)):
    contact = await contacts_repo.get_contact(current_user, contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Сontact not found!")
    return contact


@router.post("/",
             response_model=ContactSchemaResponse,
             description='No more than 10 requests per minute',
             dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def create_contact(
        body: ContactSchema,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)):
    contact = await contacts_repo.create_contact(current_user, body, db)
    print(contact)
    return contact


@router.put("/{contact_id}",
            response_model=ContactSchemaResponse,
            description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def put_contact(
        body: ContactSchema,
        contact_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)):
    contact = await contacts_repo.update_contact(current_user, contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Сontact not found!")
    return contact


@router.delete("/{contact_id}", response_model=ContactSchemaResponse)
async def delete_contact(
        contact_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)):
    contact = await contacts_repo.delete_contact(current_user, contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Сontact not found!")
    return contact
