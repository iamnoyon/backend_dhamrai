import logging
from sqlalchemy.orm import Session
from app.core.mail import send_email
from app.modules.users.model import User, UserRole, UserStatus
from fastapi import HTTPException, status
from app.utils.hash import hash_password, verify_password
from app.core.security import create_access_token, JWT_EXPIRE_MINUTES

# Configure logging
logger = logging.getLogger("Auth::Service")

# Service function for user registration
async def user_register_service(req, db: Session):
    # Check if the user already exists
    existing_user = db.query(User).filter(User.email == req.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )

    # Create a new user
    hash = hash_password(req.password)  # Hash the password before storing
    new_user = User(
        full_name = req.full_name,
        email = req.email,
        password = hash,
        phone_number = req.phone_number,
        dob = req.dob
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"New user registered: {new_user.email}")

    # Send a welcome email to the new user (non-blocking for registration)
    try:
        await send_email(new_user.email)
        logger.info(f"Welcome email sent to: {new_user.email}")
    except Exception:
        logger.exception(f"Failed to send welcome email to: {new_user.email}")
    
    return {"message": "User registered successfully", "user": new_user}

# Service function for superadmin login, returns a jwt access token
async def login_service(req, db: Session):
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password"
    )

    user = db.query(User).filter(User.email == req.email).first()
    if user is None or not verify_password(req.password, user.password):
        raise invalid

    # Only an active superadmin can log in
    if user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can log in"
        )
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User is {user.status}"
        )

    logger.info(f"Superadmin logged in: {user.email}")

    return {
        "success": True,
        "message": "Login successful",
        "data": {
            "access_token": create_access_token(user),
            "token_type": "bearer",
            "expires_in": JWT_EXPIRE_MINUTES * 60,
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role,
            },
        },
    }
