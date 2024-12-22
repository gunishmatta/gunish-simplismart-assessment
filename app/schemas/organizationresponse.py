from typing import Optional

from pydantic import BaseModel


class OrganizationBase(BaseModel):
    name: str

    class Config:
        from_attributes = True


class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(OrganizationBase):
    pass

class OrganizationResponse(OrganizationBase):
    id: int
    invite_code: str

    class Config:
        from_attributes = True

