from pydantic import BaseModel

# Token schema for authentication tokens for OpenAPI Authorize button
class Token(BaseModel):
    access_token: str
    token_type: str

# 29-12-2025 - Added TokenSPA schema for Single Page Applications
class TokenSPA(BaseModel):
    access_token: str
    token_type: str
    username: str

# 25-01-2026 - Added BothTokensSPA schema for Single Page Applications
class BothTokensSPA(BaseModel):
    jwtToken: str
    refreshToken: str
    token_type: str
    username: str