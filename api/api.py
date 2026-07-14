from fastapi import FastAPI

# Import the database engine
from db.database import engine

import models

from fastapi.middleware.cors import CORSMiddleware

# Import the routes from routes/user.py
from routes.user import router_auth as router_auth_jwt

# Import the routes from routes/simple.py
from routes.simple import router_simple as router_simple_one

# 14-06-2026 - Learned that Alembic is handling the migration
# Run the database migrations to create tables from the models
# models.user.Base.metadata.create_all(bind=engine)

# Initialize the FastAPI app
app = FastAPI(
    title="FastAPI Authentication Using JWT, Refresh Token Rotation and Refresh Token Reuse Detection",
    description="14-07-2026 -  FastAPI authentication service using JWT, Refresh Token Rotation, Refresh Token Reuse Detection  with PostgreSQL for data persistence and Alembic for database migrations. Demo credentials: testuser / admin",
    version="0.0.2",
    contact={
        "name": "Per Olsen",
        "url": "https://persteenolsen.netlify.app",
    },
)

# Set up CORS middleware
origins = [
    # Not sure if this is needed, but adding just in case
    "https://fastapi-jwt-reuse-detection-auth.vercel.app",
    # The domain name of the Vue 3 SPA Client
    "https://vue.fastapi.jwt.reuse.detection.auth.persteenolsen.com",
    # Allow my local Vue SPA
    "http://localhost:3000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routes from routes/user.py
app.include_router(router_auth_jwt)

# Include the routes from routes/simple.py
app.include_router(router_simple_one)
