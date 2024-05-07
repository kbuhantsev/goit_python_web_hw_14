from unittest.mock import Mock

import pytest
from sqlalchemy import select

from src.database.models import User
from tests.conftest import TestingSession


def test_signup(client, user, mock_ratelimiter, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("/api/auth/signup", json=user)

    assert response.status_code == 201, response.text
    data = response.json()
    print(data)


def test_singup_twice(client, user, mock_ratelimiter):
    response = client.post("/api/auth/signup", json=user)

    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Account already exists"


def test_not_confirmed_user(client, user, mock_ratelimiter):
    print("test_not_confirmed_user", user)
    response = client.post(
        "/api/auth/login",
        data={"username": user.get("email"), "password": user.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email not confirmed"


@pytest.mark.asyncio
async def test_login(client, user, mock_ratelimiter):
    async with TestingSession() as session:
        exsisting_user = await session.execute(
            select(User).where(User.name == user["name"])
        )
        exsisting_user = exsisting_user.scalar_one_or_none()
        if exsisting_user:
            exsisting_user.confirmed = True
            await session.commit()

    response = client.post(
        "/api/auth/login",
        data={"username": user.get("email"), "password": user.get("password")},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["access_token"]
    assert data["refresh_token"]
    assert data["token_type"]


def test_login_wrong_password(client, user, mock_ratelimiter):
    response = client.post(
        "/api/auth/login/",
        data={"username": user.get("email"), "password": "password"},
    )

    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid password"


def test_login_wrong_email(client, user, mock_ratelimiter):
    response = client.post(
        "/api/auth/login/", data={"username": "wrong", "password": user["password"]}
    )

    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid email"


def test_validation_error(client, user, mock_ratelimiter):
    response = client.post("/api/auth/login/", data={"password": user.get("password")})

    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data
