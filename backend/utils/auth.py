"""
JWT Authentication Module

Phase 8-2: Security Hardening
- Strengthened token validation
- Algorithm confusion prevention
- Token revocation support
- Comprehensive security checks
"""

import jwt
import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

# ✅ SECURITY: Load secret from environment or fail
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY or JWT_SECRET_KEY == "default-secret-key":
    logger.warning("⚠️ JWT_SECRET_KEY not set or using default! This is insecure in production.")
    # For development/testing only
    if os.getenv("ENV", "development") != "production":
        JWT_SECRET_KEY = "dev-secret-key-change-in-production"
    else:
        raise ValueError("JWT_SECRET_KEY must be set in production!")

JWT_ALGORITHM = "HS256"  # ✅ SECURITY: Only HS256 algorithm allowed
JWT_EXPIRATION_HOURS = 24
JWT_REFRESH_EXPIRATION_DAYS = 7

# Token revocation blacklist (in production, use Redis)
TOKEN_BLACKLIST = set()


def create_access_token(
    user_id: str,
    username: str,
    additional_claims: Optional[dict] = None
) -> str:
    """
    Create JWT access token with security best practices

    Args:
        user_id: Unique user identifier
        username: Username
        additional_claims: Optional additional claims to include

    Returns:
        JWT token string
    """
    now = datetime.utcnow()

    payload = {
        "user_id": user_id,
        "username": username,
        "iat": now,  # ✅ SECURITY: Issued-at timestamp
        "exp": now + timedelta(hours=JWT_EXPIRATION_HOURS),
        "type": "access",  # ✅ SECURITY: Token type
    }

    # Add additional claims if provided
    if additional_claims:
        payload.update(additional_claims)

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def verify_token(token: str) -> str:
    """
    Verify JWT token with comprehensive security checks

    Phase 8-2: Enhanced validation
    - Signature verification
    - Expiration check
    - Algorithm whitelist
    - Issued-at validation
    - Token revocation check

    Args:
        token: JWT token to verify

    Returns:
        user_id if valid

    Raises:
        HTTPException: If token is invalid
    """
    try:
        # ✅ SECURITY: Decode with explicit options
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],  # ✅ SECURITY: Explicit algorithm whitelist
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "require_exp": True,
                "require_iat": True,
            }
        )

        # ✅ SECURITY: Validate required fields
        user_id = payload.get("user_id")
        if user_id is None:
            logger.warning("Token missing user_id claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user_id"
            )

        # ✅ SECURITY: Check token type
        token_type = payload.get("type", "access")
        if token_type != "access":
            logger.warning(f"Invalid token type: {token_type}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        # ✅ SECURITY: Check if token is revoked (blacklisted)
        if is_token_revoked(token):
            logger.warning(f"Revoked token used for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )

        # ✅ SECURITY: Validate issued-at is not in the future
        iat = payload.get("iat")
        if iat and datetime.fromtimestamp(iat, timezone.utc) > datetime.now(timezone.utc):
            logger.warning("Token issued in the future")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: future issued-at time"
            )

        return user_id

    except HTTPException:
        raise
    except jwt.ExpiredSignatureError:
        logger.info("Token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidAlgorithmError:
        logger.error("Invalid JWT algorithm used")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token algorithm"
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed"
        )


def revoke_token(token: str) -> bool:
    """
    Add token to revocation blacklist

    In production, use Redis with TTL

    Args:
        token: Token to revoke

    Returns:
        True if successful
    """
    TOKEN_BLACKLIST.add(token)
    logger.info(f"Token revoked: {token[:20]}...")
    return True


def is_token_revoked(token: str) -> bool:
    """
    Check if token is in revocation blacklist

    Args:
        token: Token to check

    Returns:
        True if revoked, False otherwise
    """
    return token in TOKEN_BLACKLIST

def create_demo_token() -> str:
    """Create demo token for hackathon testing"""
    return create_access_token("demo-user", "demo")
