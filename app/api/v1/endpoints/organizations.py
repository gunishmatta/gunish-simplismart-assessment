import secrets
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core import deps
from app.models.organization import Organization
from app.models.user import User
from app.schemas.organizationresponse import (OrganizationCreate,
                                              OrganizationResponse)

router = APIRouter()


@router.post("/", response_model=OrganizationResponse)
def create_organization(
        *,
        db: Session = Depends(deps.get_db),
        organization_in: OrganizationCreate,
        current_user: User = Depends(deps.get_current_user)
):
    """
    Create a new organization.
    """
    name = organization_in.name
    existing_org = db.query(Organization).filter(Organization.name == name).first()

    if existing_org:
        raise HTTPException(status_code=400, detail="Organization with this name already exists.")
    invite_code = secrets.token_urlsafe(8)
    organization = Organization(name=name,invite_code=invite_code)
    db.add(organization)
    db.commit()
    db.refresh(organization)

    # Ensure you're returning a valid OrganizationResponse object
    return organization


@router.post("/{invite_code}/join")
def join_organization(
    *,
    db: Session = Depends(deps.get_db),
    invite_code: str,
    current_user: User = Depends(deps.get_current_user)
):
    """
    TODO: Implement organization joining logic
    """
    organization = db.query(Organization).filter(Organization.invite_code == invite_code).first()

    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    if current_user.organization_id is not None:
        raise HTTPException(status_code=400, detail="User is already a member of an organization")

    current_user.organization_id = organization.id
    db.commit()
    db.refresh(current_user)
    return organization
