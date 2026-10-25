from pydantic import BaseModel, ConfigDict


class AuthBase(BaseModel):
    pass


class AuthCreate(AuthBase):
    pass


class AuthUpdate(AuthBase):
    pass


class AuthRead(AuthBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
