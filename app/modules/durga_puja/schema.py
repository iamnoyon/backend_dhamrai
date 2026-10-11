import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class VillageSchema(BaseModel):
    village_name: str = Field(..., min_length=1, max_length=100, example="A")
    mondir_name: str = Field(..., min_length=1, max_length=150, example="a")
    phone: str = Field(..., example="01712345678")

    @field_validator("village_name", "mondir_name", mode="before")
    @classmethod
    def strip_name(cls, v):
        return v.strip() if isinstance(v, str) else v

    # Phone may come as a number, it is stored as a string so a leading 0 is not lost
    @field_validator("phone", mode="before")
    @classmethod
    def check_phone(cls, v):
        if isinstance(v, int) and not isinstance(v, bool):
            v = str(v)
        if not isinstance(v, str) or not re.fullmatch(r"\+?\d{6,15}", v.strip()):
            raise ValueError("phone must be 6 to 15 digits, optionally starting with +")
        return v.strip()


class DurgaPujaCreateSchema(BaseModel):
    feature_id: int = Field(..., example=1)
    union_id: int = Field(..., example=1)
    ward_code: Optional[str] = Field(None, max_length=20, example="BD3026141091")  # null for a paurashava union
    villages: list[VillageSchema] = Field(..., min_length=1)

    # An empty ward code is the same as null
    @field_validator("ward_code", mode="before")
    @classmethod
    def blank_ward_code(cls, v):
        if isinstance(v, str):
            v = v.strip()
            return v or None
        return v

    # The same mondir can not be twice in the same village
    @model_validator(mode="after")
    def check_duplicates(self):
        seen = set()
        for v in self.villages:
            key = (v.village_name.lower(), v.mondir_name.lower())
            if key in seen:
                raise ValueError(f"Duplicate mondir '{v.mondir_name}' in village '{v.village_name}'")
            seen.add(key)
        return self
