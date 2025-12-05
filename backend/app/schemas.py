from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, Field, field_validator


class ShortenRequest(BaseModel):
    url: AnyHttpUrl = Field(..., description="The destination URL to shorten")
    custom_code: str | None = Field(default=None, min_length=4, max_length=16)

    @field_validator('custom_code', mode='before')
    @classmethod
    def validate_custom_code(cls, v):
        """Convert empty strings to None and validate format if provided."""
        if v == "" or v is None:
            return None
        if isinstance(v, str):
            v = v.strip()
            if v == "":
                return None
            if len(v) < 4:
                raise ValueError("Custom code must be at least 4 characters long")
            if len(v) > 16:
                raise ValueError("Custom code must be at most 16 characters long")
            # Only allow alphanumeric characters (letters and digits)
            if not v.isalnum():
                raise ValueError("Custom code can only contain letters and numbers")
        return v


class ShortenResponse(BaseModel):
    code: str
    short_url: AnyHttpUrl
    created_at: datetime


class ShortURLRecord(BaseModel):
    id: int
    code: str
    target_url: AnyHttpUrl
    created_at: datetime

    class Config:
        from_attributes = True
