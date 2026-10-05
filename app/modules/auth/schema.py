from pydantic import BaseModel, EmailStr, Field, field_validator

class UserRegisterSchema(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100, example="John Doe")
    email: EmailStr = Field(..., example="john.doe@example.com")
    phone_number: str = Field(..., min_length=10, max_length=15, example="1234567890")
    password: str = Field(..., min_length=6, max_length=255, example="password123")
    dob: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", example="1990-01-01")  # Format: YYYY-MM-DD


