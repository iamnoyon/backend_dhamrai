from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class CandidateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, example="A")
    image: Optional[str] = Field(None, max_length=500, example="https://example.com/a.png")


class FeatureCreateSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, example="Baisakanda UP Chairman Election 2026")
    is_union_based: bool = Field(..., example=True)
    union_id: Optional[int] = Field(None, example=2)
    candidates: list[CandidateSchema] = Field(..., min_length=1)

    @field_validator("title", mode="before")
    @classmethod
    def strip_title(cls, v):
        return v.strip() if isinstance(v, str) else v

    @model_validator(mode="after")
    def check_union(self):
        if self.is_union_based and self.union_id is None:
            raise ValueError("union_id is required when is_union_based is true")
        if not self.is_union_based and self.union_id is not None:
            raise ValueError("union_id must be null when is_union_based is false")

        names = [c.name.strip().lower() for c in self.candidates]
        if len(names) != len(set(names)):
            raise ValueError("duplicate candidate name in candidates")
        return self


class FeatureResultSchema(BaseModel):
    feature_id: int = Field(..., example=2)
    union_id: int = Field(..., example=2)
    ward_code: Optional[str] = Field(None, min_length=1, max_length=20, example="BD3026141431")  # null for a union without wards (paurashava)
    candidate_name: str = Field(..., min_length=1, max_length=100, example="A")
    value: int = Field(..., ge=0, example=400)


class CandidateUpdateSchema(CandidateSchema):
    id: Optional[str] = Field(None, max_length=10, example="a")  # null for a new candidate


class WardVoterSchema(BaseModel):
    ward_id: Optional[int] = Field(None, example=4)  # null for a union without wards (paurashava)
    union_id: int = Field(..., example=2)
    total_number: int = Field(..., ge=0, example=1000)


class FeatureUpdateSchema(BaseModel):
    candidates: Optional[list[CandidateUpdateSchema]] = Field(None, min_length=1)
    wards: Optional[list[WardVoterSchema]] = None

    @model_validator(mode="after")
    def check_candidates(self):
        if self.candidates is not None:
            names = [c.name.strip().lower() for c in self.candidates]
            if len(names) != len(set(names)):
                raise ValueError("duplicate candidate name in candidates")
            ids = [c.id for c in self.candidates if c.id is not None]
            if len(ids) != len(set(ids)):
                raise ValueError("duplicate candidate id in candidates")
        return self
