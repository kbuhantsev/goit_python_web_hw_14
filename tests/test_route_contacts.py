from unittest.mock import Mock
import pytest_asyncio
from sqlalchemy import select

from tests.conftest import TestingSession

from src.database.models import User


@pytest_asyncio.fixture()
async def token(client, user, mock_ratelimiter, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("/api/auth/signup", json=user)

    async with TestingSession() as session:
        existing_user = await session.execute(
            select(User).where(User.name == user["name"])
        )
        existing_user = existing_user.scalar_one_or_none()
        if existing_user:
            existing_user.confirmed = True
            await session.commit()

    response = client.post(
        "/api/auth/login",
        data={"username": user.get("email"), "password": user.get("password")},
    )

    data = response.json()
    return data.get("access_token")


def test_create_contact(client, contact, token, mock_ratelimiter):
    response = client.post(
        "/api/contacts/", json=contact, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["name"] == contact["name"]
    assert data["surname"] == contact["surname"]


def test_get_contacts(client, token, mock_ratelimiter):
    response = client.get(
        "/api/contacts/", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200, response.text

    print(response.json())
    print(response.status_code)

    data = response.json()
    assert len(data) == 1


def test_get_contact(client, token, contact, mock_ratelimiter):
    response = client.get(
        f"/api/contacts/{contact['id']}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == contact["name"]


def test_contact_not_found(client, token, mock_ratelimiter):
    response = client.get(
        "/api/contacts/999", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found!"


def test_update_contact(client, token, contact, mock_ratelimiter):
    contact["name"] = "Updated first name"
    response = client.put(
        f"/api/contacts/{contact['id']}",
        json=contact,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Updated first name"


def test_delete_contact(client, token, contact, mock_ratelimiter):
    response = client.delete(
        f"/api/contacts/{contact['id']}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200, response.text


def test_delete_contact_not_found(client, token, contact, mock_ratelimiter):
    response = client.delete(
        f"/api/contacts/999", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404, response.text
