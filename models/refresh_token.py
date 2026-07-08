from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship

from db.database import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # 06-07-2026 - Unique identifier stored inside the JWT
    jti = Column(String, nullable=False, unique=True, index=True)

    # 06-07-2026 - SHA-256 hash of the refresh token
    token_hash = Column(String, nullable=False, unique=True, index=True)

    expires_at = Column(DateTime(timezone=True), nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    # Null means the token is still active
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    # Used later for refresh token reuse detection
    replaced_by_jti = Column(String, nullable=True)

    # Used later for token family revocation
    parent_jti = Column(String, nullable=True)

    user = relationship(
        "User",
        back_populates="refresh_tokens",
    )

    __table_args__ = (
        Index(
            "ix_refresh_tokens_user_expires",
            "user_id",
            "expires_at",
        ),
        Index(
            "ix_refresh_tokens_user_revoked",
            "user_id",
            "revoked_at",
        ),
    )