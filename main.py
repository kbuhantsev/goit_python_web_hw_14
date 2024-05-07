import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.database.db import get_db

from src.routes.contacts import router as contacts_router
from src.routes.tests import router as tests_router
from src.routes.auth import router as auth_router
from src.routes.users import router as users_router

from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

import redis.asyncio as redis
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    r = await redis.Redis(host='localhost', port=6379, db=0, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(r)
    yield
    await FastAPILimiter.close()


app = FastAPI(lifespan=lifespan)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contacts_router, prefix='/api')
app.include_router(auth_router, prefix='/api')
app.include_router(users_router, prefix='/api')
#
app.include_router(tests_router, prefix='/api')


@app.get("/", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
def root():
    return {"message": "Contacts API"}


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        # Make request
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
