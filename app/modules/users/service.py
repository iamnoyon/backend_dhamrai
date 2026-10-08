import os
import logging
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.utils.hash import hash_password
from .model import User, UserRole

load_dotenv()  # Load environment variables from .env file

logger = logging.getLogger("User::Service")


# Create the superadmin user if there is none yet
def create_superadmin(db: Session):
    if db.query(User).filter(User.role == UserRole.SUPERADMIN).first() is not None:
        return

    email = os.getenv("SUPERADMIN_EMAIL")
    password = os.getenv("SUPERADMIN_PASSWORD")
    if not email or not password:
        logger.warning("SUPERADMIN_EMAIL or SUPERADMIN_PASSWORD not set, superadmin not created")
        return

    phone_number = os.getenv("SUPERADMIN_PHONE", "00000000000")
    if db.query(User).filter((User.email == email) | (User.phone_number == phone_number)).first() is not None:
        logger.warning(f"A user with email {email} or phone {phone_number} already exists, superadmin not created")
        return

    superadmin = User(
        full_name = os.getenv("SUPERADMIN_NAME", "Super Admin"),
        email = email,
        phone_number = phone_number,
        password = hash_password(password),
        dob = "1970-01-01",
        role = UserRole.SUPERADMIN
    )
    db.add(superadmin)
    db.commit()

    logger.info(f"Superadmin created: {email}")
