from fastapi import APIRouter, Depends, Body, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

# Import the get_current_username and get_current_user functions from services/users.py
from db.database import get_db
from services.users import (
    get_current_username,
    get_current_user,
    get_all_users,
    do_register_user,
)
from services.users import (
    get_access_token_for_login,
    get_tokens_for_login_spa,
    get_tokens_and_type,
)

# With the below import statement we import the User model and reference the username of a User by:
# User.username
from models.user import User

# To Avoid confusion / conflict with the names of Models we import the schemas Objects as:
# UserSchema, UserCreateSchema and TokenSchema
from schemas.user import User as UserSchema
from schemas.token import Token as TokenSchema
from schemas.token import TokenSPA as TokenSchemaSPA

from schemas.token import BothTokensSPA as BothTokensSchemaSPA

from services.users import logout, logout_all
from services.users import cleanup_refresh_tokens
from sqlalchemy.orm import Session

from models.refresh_token import RefreshToken
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import Depends

router_auth = APIRouter()


# 07-07-2026 - Admin endpoint to purge all refresh tokens from the database
@router_auth.post("/admin/purge-refresh-tokens", tags=["admin"])
def purge_refresh_tokens(
    db: Session = Depends(get_db), username: str = Depends(get_current_username)
):
    if username != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    deleted_count = db.query(RefreshToken).delete()

    db.commit()

    return {
        "message": "All refresh tokens purged",
        "deleted_tokens": deleted_count,
        "executed_by": username,
        "timestamp": datetime.utcnow(),
    }


# 06-07-2026 - Admin endpoint to cleanup expired refresh tokens from the database
@router_auth.post("/cleanup-tokens", tags=["admin"])
async def cleanup_tokens(db: Session = Depends(get_db)):
    return await cleanup_refresh_tokens(db)


# 06-07-2026 - Logout endpoint for all users
@router_auth.post("/logout-all", tags=["user"])
async def logout_everywhere(
    username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
):
    return await logout_all(username, db)


# 06-07-2026 - Logout endpoint for SPA applications
@router_auth.post("/logout", tags=["user"])
async def logout_user(response=Depends(logout)):
    return response


# Public route that returns access token and type if User credentials are valid
# Note: User Registration Endpoint disabled for Production
# @router_auth.post("/register", response_model=UserSchema, tags=["user"])
def register_user(new_user=Depends(do_register_user)):
    return new_user


# Public route that returns access token and type if User credentials are valid
# 27-12-2025 - The endpoint needs to be /token for using the OpenAPI Autorize button
# Note: The db session and form_data dependencies are handled inside the service function
@router_auth.post("/token", response_model=TokenSchema, tags=["user"])
def login_for_access_token(token_and_type=Depends(get_access_token_for_login)):
    return token_and_type


# Public route that returns access token, type and username if User credentials are valid
# 26-01-2026 - Added endpoint for Single Page Applications
# Note: The db session and form_data dependencies are handled inside the service function
@router_auth.post("/tokens-spa", response_model=BothTokensSchemaSPA, tags=["user"])
def login_for_tokens_spa(tokens_type_username=Depends(get_tokens_for_login_spa)):
    return tokens_type_username


# 26-01-2026 - Refresh Token endpoint for SPA applications
# Returns access token + refresh token + type + username if Refresh Token is valid
# 28-01-2026 - To improve security we could check if the User, extrated from the Refresh Token (sub),
# still exists in the Database
# @router_auth.post("/refresh-token-spa", response_model=BothTokensSchemaSPA, tags=["user"])
# async def refresh_token_spa(refreshToken: str = Body(...)) -> dict:
#    return await get_tokens_and_type(refreshToken)


@router_auth.post("/refresh-token-spa")
async def refresh_token(refreshToken: str = Body(...), db: Session = Depends(get_db)):
    return await get_tokens_and_type(refreshToken, db)


# Protected route that returns the current user's information
# Validation: 401 is returned if token is invalid and 404 if user not found
@router_auth.get("/users/me", response_model=UserSchema, tags=["user"])
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


# Protected route that returns a message and the current user's Username using token directly
# Validation: 401 is returned if token is invalid
@router_auth.get("/protected-route", tags=["user"])
def secure_endpoint(username: str = Depends(get_current_username)):
    return {
        "message": f"Hello {username}, you are authorized for this protected route!"
    }


# Protected route that returns all Users from the Database if the token is valid
# Validation: 401 is returned if token is invalid and 404 if no users found
@router_auth.get("/get-all-users", response_model=list[UserSchema], tags=["user"])
def secure_endpoint(users: str = Depends(get_all_users)):
    return users
