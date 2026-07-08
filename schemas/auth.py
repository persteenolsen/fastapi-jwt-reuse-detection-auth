from pydantic import BaseModel


class RefreshRequest(BaseModel):
    refreshToken: str


class LogoutRequest(BaseModel):
    refresh_token: str