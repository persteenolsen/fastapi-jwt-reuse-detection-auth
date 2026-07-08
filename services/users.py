from fastapi import Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from models.refresh_token import RefreshToken
from security.auth import (
    decode_token_payload,
    verify_password,
    verify_token,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    hash_refresh_token
)

from db.database import get_db
from models.user import User

from schemas.user import UserCreate as UserCreateSchema

from pydantic import BaseModel

import os

from datetime import datetime, timedelta, timezone

# 07-07-2026 - Outcommented because it is present later in the file
# class RefreshRequest(BaseModel):
#    refreshToken: str


REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def logout(
    refresh_token: str = Body(...),
    db: Session = Depends(get_db)
):
    token_hash = hash_refresh_token(refresh_token)

    db_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash
    ).first()

    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refresh token not found",
        )

    if db_token.revoked_at is not None:
        return {"message": "Already logged out"}

    db_token.revoked_at = datetime.utcnow()

    db.commit()

    return {"message": "Successfully logged out"}

# 07-07-2026 - Using the line below to prevent error
# Note: The db:session must be used here and a general rule is that it 
# should be used in all functions that are called from routes/user.py
# async def logout_all(username: str, db: Session = Depends(get_db)):
async def logout_all(username: str, db: Session):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    tokens = db.query(RefreshToken).filter(
        RefreshToken.user_id == user.id,
        RefreshToken.revoked_at == None
    ).all()

    for token in tokens:
        token.revoked_at = datetime.utcnow()

    db.commit()

    return {"message": "Logged out from all sessions"}

# =========================
# PROJECT 2 - REFRESH TOKEN REUSE DETECTION
# =========================
def revoke_refresh_token_family(
    db: Session,
    token_jti: str
):
    """
    Revoke all active refresh tokens for the user who owns the
    supplied refresh token.

    This is triggered when a previously rotated refresh token is
    presented again, indicating possible token theft or replay.
    """

    current_token = db.query(RefreshToken).filter(
        RefreshToken.jti == token_jti
    ).first()

    if current_token is None:
        return

    now = datetime.utcnow()

    active_tokens = db.query(RefreshToken).filter(
        RefreshToken.user_id == current_token.user_id,
        RefreshToken.revoked_at.is_(None)
    ).all()

    for token in active_tokens:
        token.revoked_at = now

    db.commit()

async def cleanup_refresh_tokens(db: Session = Depends(get_db)):
    """
    06-07-2026 - Cleanup job for refresh tokens.

    Removes:
    - revoked tokens older than 7 days
    - expired tokens older than 7 days
    """

    cutoff = datetime.utcnow() - timedelta(days=7)

    tokens_to_delete = db.query(RefreshToken).filter(
        (RefreshToken.revoked_at != None)
        & (RefreshToken.revoked_at < cutoff)
    ).all()

    expired_tokens_to_delete = db.query(RefreshToken).filter(
        RefreshToken.expires_at < cutoff
    ).all()

    all_tokens = set(tokens_to_delete + expired_tokens_to_delete)

    deleted_count = len(all_tokens)

    for token in all_tokens:
        db.delete(token)

    db.commit()

    return {
        "message": "Cleanup completed",
        "deleted_tokens": deleted_count
    }


def do_register_user(
    user: UserCreateSchema,
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(
        User.username == user.username
    ).first()

    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )

    hashed_password = get_password_hash(user.password)

    new_user = User(
        username=user.username,
        name=user.name,
        email=user.email,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def get_access_token_for_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.username == form_data.username
    ).first()

    if not user or not verify_password(
        form_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.username}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


def get_tokens_for_login_spa(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.username == form_data.username
    ).first()

    if not user or not verify_password(
        form_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token(
        {"sub": user.username}
    )

    refresh_token = create_refresh_token(
        {"sub": user.username}
    )

    refresh_token_hash = hash_refresh_token(refresh_token)

    payload = decode_token_payload(refresh_token)

    db_token = RefreshToken(
        user_id=user.id,
        jti=payload["jti"],
        token_hash=refresh_token_hash,
        expires_at=datetime.utcnow()
        + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES),
        revoked_at=None,
        replaced_by_jti=None,
        parent_jti=None
    )

    db.add(db_token)
    db.commit()

    return {
        "jwtToken": access_token,
        "refreshToken": refresh_token,
        "token_type": "bearer",
        "username": user.username
    }

# =========================
# REQUEST MODEL
# =========================
# 07-07-2026 - Could be outcommented because it is problerly not used anywhere
class RefreshRequest(BaseModel):
    refreshToken: str

# =========================
# REFRESH ROTATION ENDPOINT
# =========================
async def get_tokens_and_type(
    refreshToken: str = Body(...),
    db: Session = Depends(get_db)
):
    # 1. Decode JWT
    payload = decode_token_payload(refreshToken)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    username = payload.get("sub")

    if not username:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token payload"
        )

    # 2. Hash token
    token_hash = hash_refresh_token(refreshToken)

    # 3. Find DB record
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash
    ).first()

    if not db_token:
        raise HTTPException(
            status_code=401,
            detail="Refresh token not found"
        )

    # =====================================
    # PROJECT 2 - Refresh Token Reuse Detection
    # =====================================

    if db_token.revoked_at is not None:

        # Token has already been rotated once
        if db_token.replaced_by_jti is not None:

            revoke_refresh_token_family(
                db,
                db_token.jti
            )

            raise HTTPException(
                status_code=401,
                detail="Refresh token reuse detected"
            )

        raise HTTPException(
            status_code=401,
            detail="Refresh token revoked"
        )

    # Database expiration validation
    if db_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=401,
            detail="Refresh token expired"
        )

    # 4. Create new access token
    new_access = create_access_token(
        {
            "sub": username
        }
    )

    # 5. Create new refresh token
    new_refresh = create_refresh_token(
        {
            "sub": username
        }
    )

    new_payload = decode_token_payload(new_refresh)

    # Safety check
    if not new_payload:
        raise HTTPException(
            status_code=500,
            detail="Failed to create refresh token"
        )

    # 6. Rotate old token
    db_token.revoked_at = datetime.utcnow()
    db_token.replaced_by_jti = new_payload["jti"]

    # 7. Store new refresh token
    new_db_token = RefreshToken(
        user_id=db_token.user_id,
        jti=new_payload["jti"],
        token_hash=hash_refresh_token(new_refresh),
        expires_at=datetime.utcnow()
        + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES),
        revoked_at=None,
        replaced_by_jti=None,
        parent_jti=db_token.jti
    )

    db.add(new_db_token)
    db.commit()

    return {
        "jwtToken": new_access,
        "refreshToken": new_refresh,
        "token_type": "bearer",
        "username": username
    }

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    username = verify_token(
        token,
        expected_type="access"
    )

    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials! Try to Autorize ...",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(
        User.username == username
    ).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


def get_current_username(
    token: str = Depends(oauth2_scheme)
):
    username = verify_token(
        token,
        expected_type="access"
    )

    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The JWT Token is not valid or has expired! Try to Autorize ...",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return username


def get_all_users(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    username = verify_token(
        token,
        expected_type="access"
    )

    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials! Try to Autorize ...",
            headers={"WWW-Authenticate": "Bearer"},
        )

    users = db.query(User).all()

    if users is None:
        raise HTTPException(
            status_code=404,
            detail="No Users found"
        )

    return users