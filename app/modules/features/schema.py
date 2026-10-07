from typing import Optional
from pydantic import BaseModel, Field, model_validator


class FeatureWardSchema(BaseModel):
    union_id: int = Field(..., example=2)
    ward_no: int = Field(..., ge=1, example=1)
    total_voter: int = Field(..., ge=0, example=1000)


class CandidateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, example="A")
    image: Optional[str] = Field(None, max_length=500, example="https://example.com/a.png")


class FeatureCreateSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, example="Baisakanda UP Chairman Election 2026")
    is_union_based: bool = Field(..., example=True)
    union_id: Optional[int] = Field(None, example=2)
    wards: list[FeatureWardSchema] = Field(..., min_length=1)
    candidates: list[CandidateSchema] = Field(..., min_length=1)

    @model_validator(mode="after")
    def check_union_and_wards(self):
        if self.is_union_based:
            if self.union_id is None:
                raise ValueError("union_id is required when is_union_based is true")
            if any(w.union_id != self.union_id for w in self.wards):
                raise ValueError("all wards must belong to the feature's union_id")
        elif self.union_id is not None:
            raise ValueError("union_id must be null when is_union_based is false")

        keys = [(w.union_id, w.ward_no) for w in self.wards]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate ward (union_id, ward_no) in wards")

        names = [c.name.strip().lower() for c in self.candidates]
        if len(names) != len(set(names)):
            raise ValueError("duplicate candidate name in candidates")
        return self


class FeatureResultSchema(BaseModel):
    feature_id: int = Field(..., example=2)
    union_id: int = Field(..., example=2)
    ward_code: str = Field(..., min_length=1, max_length=20, example="BD3026141431")
    candidate_name: str = Field(..., min_length=1, max_length=100, example="A")
    value: int = Field(..., ge=0, example=400)
