import logging
import time
import uuid
import secrets
from typing import Optional

from open_webui.internal.db import Base, get_db
from pydantic import BaseModel
from sqlalchemy import BigInteger, Boolean, Column, String, Text

log = logging.getLogger(__name__)

####################
# DB MODEL
####################


class PasswordResetToken(Base):
    __tablename__ = "password_reset_token"

    id = Column(String, primary_key=True, unique=True)
    user_id = Column(String, nullable=False)
    token_hash = Column(Text, nullable=False)  # Store hashed token for security
    expires_at = Column(BigInteger, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(BigInteger, nullable=False)


class PasswordResetTokenModel(BaseModel):
    id: str
    user_id: str
    token_hash: str
    expires_at: int
    used: bool = False
    created_at: int


####################
# Forms
####################


class ForgotPasswordForm(BaseModel):
    email: str


class ResetPasswordForm(BaseModel):
    token: str
    new_password: str


class VerifyResetTokenForm(BaseModel):
    token: str


####################
# Table Operations
####################


class PasswordResetTokensTable:
    def create_reset_token(
        self, user_id: str, token_hash: str, expires_at: int
    ) -> Optional[PasswordResetTokenModel]:
        with get_db() as db:
            try:
                # Invalidate any existing tokens for this user
                db.query(PasswordResetToken).filter_by(
                    user_id=user_id, used=False
                ).update({"used": True})

                id = str(uuid.uuid4())
                token_record = PasswordResetTokenModel(
                    id=id,
                    user_id=user_id,
                    token_hash=token_hash,
                    expires_at=expires_at,
                    used=False,
                    created_at=int(time.time()),
                )

                result = PasswordResetToken(**token_record.model_dump())
                db.add(result)
                db.commit()
                db.refresh(result)

                return PasswordResetTokenModel.model_validate(result)
            except Exception as e:
                log.error(f"Error creating password reset token: {e}")
                return None

    def get_valid_token(self, token_hash: str) -> Optional[PasswordResetTokenModel]:
        """Get a valid (not used, not expired) token by its hash"""
        with get_db() as db:
            try:
                current_time = int(time.time())
                result = (
                    db.query(PasswordResetToken)
                    .filter_by(token_hash=token_hash, used=False)
                    .filter(PasswordResetToken.expires_at > current_time)
                    .first()
                )

                if result:
                    return PasswordResetTokenModel.model_validate(result)
                return None
            except Exception as e:
                log.error(f"Error getting password reset token: {e}")
                return None

    def mark_token_as_used(self, token_id: str) -> bool:
        """Mark a token as used after successful password reset"""
        with get_db() as db:
            try:
                result = (
                    db.query(PasswordResetToken)
                    .filter_by(id=token_id)
                    .update({"used": True})
                )
                db.commit()
                return result == 1
            except Exception as e:
                log.error(f"Error marking token as used: {e}")
                return False

    def delete_expired_tokens(self) -> int:
        """Clean up expired tokens"""
        with get_db() as db:
            try:
                current_time = int(time.time())
                result = (
                    db.query(PasswordResetToken)
                    .filter(PasswordResetToken.expires_at < current_time)
                    .delete()
                )
                db.commit()
                return result
            except Exception as e:
                log.error(f"Error deleting expired tokens: {e}")
                return 0

    def delete_user_tokens(self, user_id: str) -> bool:
        """Delete all tokens for a user"""
        with get_db() as db:
            try:
                db.query(PasswordResetToken).filter_by(user_id=user_id).delete()
                db.commit()
                return True
            except Exception as e:
                log.error(f"Error deleting user tokens: {e}")
                return False


PasswordResetTokens = PasswordResetTokensTable()


def generate_reset_token() -> str:
    """Generate a secure random token for password reset"""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """Hash a token for secure storage"""
    import hashlib

    return hashlib.sha256(token.encode()).hexdigest()
