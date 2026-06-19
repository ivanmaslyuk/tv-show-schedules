from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SignupRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)


class ShowBase(BaseModel):
    title: str
    release_date: date


class ShowCreate(ShowBase):
    pass


class ShowUpdate(ShowBase):
    pass


class ShowResponse(ShowBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class SeasonBase(BaseModel):
    number: int
    show_id: int
    release_date: date


class SeasonCreate(SeasonBase):
    pass


class SeasonUpdate(SeasonBase):
    pass


class SeasonResponse(SeasonBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class EpisodeBase(BaseModel):
    title: str
    number: int
    season_id: int
    release_date: date


class EpisodeCreate(EpisodeBase):
    pass


class EpisodeUpdate(EpisodeBase):
    pass


class EpisodeResponse(EpisodeBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ViewResponse(BaseModel):
    id: int
    user_id: int
    episode_id: int
    viewed_at: datetime
    model_config = ConfigDict(from_attributes=True)

