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


class SeasonWrite(BaseModel):
    number: int
    release_date: date


class SeasonCreate(SeasonWrite):
    pass


class SeasonUpdate(SeasonWrite):
    pass


class SeasonResponse(SeasonWrite):
    id: int
    show_id: int
    model_config = ConfigDict(from_attributes=True)


class EpisodeWrite(BaseModel):
    title: str
    number: int
    release_date: date


class EpisodeCreate(EpisodeWrite):
    pass


class EpisodeUpdate(EpisodeWrite):
    pass


class EpisodeResponse(EpisodeWrite):
    id: int
    season_id: int
    model_config = ConfigDict(from_attributes=True)


class ViewStateResponse(BaseModel):
    viewed: bool
    viewed_at: datetime | None = None
