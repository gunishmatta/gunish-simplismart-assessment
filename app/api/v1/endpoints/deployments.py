from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core import deps
from app.core.scheduling.preemption_factory import PreemptionSchedulingFactory
from app.models.cluster import Cluster
from app.schemas.deployment import DeploymentCreate, Deployment
from app.models.user import User
from app.service.deployment_service import DeploymentService

router = APIRouter()

@router.post("/", response_model=Deployment)
def create_deployment(
    *,
    db: Session = Depends(deps.get_db),
    deployment_in: DeploymentCreate,
    current_user: User = Depends(deps.get_current_user),
    preemption_strategy: str = "priority"
):
    """
    TODO: Implement deployment creation and scheduling
    """
    deployment_service = DeploymentService(db, current_user)
    deployment = deployment_service.handle_deployment(deployment_in, preemption_strategy, deployment_in.cluster_id)
    return deployment

@router.get("/", response_model=List[Deployment])
def list_deployments(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    TODO: Implement deployment listing
    """
    clusters = db.query(Cluster).filter(Cluster.organization_id == current_user.organization_id).all()

    if not clusters:
        raise HTTPException(
            status_code=404,
            detail="No clusters found for the user's organization."
        )

    deployments = db.query(Deployment).filter(Deployment.cluster_id.in_([cluster.id for cluster in clusters])).all()

    if not deployments:
        raise HTTPException(
            status_code=404,
            detail="No deployments found for the user's organization."
        )

    return deployments
