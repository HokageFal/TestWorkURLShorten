from typing import Optional
from pydantic import BaseModel, HttpUrl, field_validator


class ShortenRequest(BaseModel):
    url: HttpUrl
    custom_code: Optional[str] = None

    @field_validator("url")
    @classmethod
    def validate_url(cls, v):
        url_str = str(v)
        if not url_str.startswith(("http://", "https://")):
            raise ValueError("URL должен начинаться с http:// или https://")
        return v

    @field_validator("custom_code")
    @classmethod
    def validate_custom_code(cls, v):
        if v is not None:
            if len(v) < 3 or len(v) > 20:
                raise ValueError("Длина кода должна быть от 3 до 20 символов")
            if not v.isalnum():
                raise ValueError("Код может содержать только буквы и цифры")
        return v


class ShortenResponse(BaseModel):
    short_url: str
    original_url: str
    short_code: str


class URLInfo(BaseModel):
    original_url: str
    short_code: str
    created_at: str


class URLStats(BaseModel):
    original_url: str
    short_code: str
    created_at: str
    id: int
