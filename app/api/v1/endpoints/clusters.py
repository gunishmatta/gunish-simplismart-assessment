from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core import deps
from app.models.cluster import Cluster
from app.models.user import User
from app.schemas.clusterresponse import ClusterCreate, ClusterResponse

router = APIRouter()

@router.post("/", response_model=ClusterResponse)
def create_cluster(
    *,
    db: Session = Depends(deps.get_db),
    cluster_in: ClusterCreate,
    current_user: User = Depends(deps.get_current_user)
):
    """
    TODO: Implement cluster creation
    """
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User must belong to an organization to create a cluster.")

    cluster = Cluster(
        name=cluster_in.name,
        organization_id=current_user.organization_id,
        cpu_limit=cluster_in.cpu_limit,
        ram_limit=cluster_in.ram_limit,
        gpu_limit=cluster_in.gpu_limit,
        cpu_available=cluster_in.cpu_limit,
        ram_available=cluster_in.ram_limit,
        gpu_available=cluster_in.gpu_limit
    )

    db.add(cluster)
    db.commit()
    db.refresh(cluster)

    return cluster

@router.get("/", response_model=List[ClusterResponse])
def list_clusters(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    TODO: Implement cluster listing
    """
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User must belong to an organization to view clusters.")

    clusters = db.query(Cluster).filter(Cluster.organization_id == current_user.organization_id).all()

    return clusters
