from typing import Type

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.scheduling.preemption_factory import PreemptionSchedulingFactory
from app.models.cluster import Cluster
from app.models.deployment import Deployment, DeploymentStatus
from app.schemas.deploymentresponse import DeploymentCreate


class DeploymentService:

    def __init__(self, db: Session, current_user):
        self.db = db
        self.current_user = current_user

    def get_cluster(self, cluster_id: int):
        """Fetch the cluster from the database."""
        cluster = self.db.query(Cluster).filter(Cluster.id == cluster_id).first()
        if not cluster:
            raise HTTPException(status_code=404, detail=f"Cluster with id {cluster_id} not found.")
        return cluster

    def check_user_permission(self, cluster: Type[Cluster]):
        """Ensure the user belongs to the same organization as the cluster."""
        if cluster.organization_id != self.current_user.organization_id:
            raise HTTPException(status_code=403, detail="User does not belong to the organization of the selected cluster.")

    def get_preemption_schedule(self, preemption_strategy: str, cluster: Type[Cluster], deployment_in: DeploymentCreate):
        """Get the preemption schedule based on the selected strategy."""
        strategy = PreemptionSchedulingFactory.get_preemption_strategy(preemption_strategy)
        return strategy.preempt(db=self.db, cluster=cluster, deployment_in=deployment_in)

    def apply_preemption(self, schedule: dict, cluster: Type[Cluster]):
        """Preempt low priority deployments and update cluster resources."""
        for preempted_deployment in schedule["preempted_deployments"]:
            preempted_deployment.status = "Preempted"
            cluster.cpu_available += preempted_deployment.cpu_required
            cluster.ram_available += preempted_deployment.ram_required
            cluster.gpu_available += preempted_deployment.gpu_required
            self.db.commit()

    def create_new_deployment(self, deployment_in: DeploymentCreate, cluster) -> Deployment:
        """Create and return a new deployment."""
        deployment = Deployment(
            name=deployment_in.name,
            cpu_required=deployment_in.cpu_required,
            ram_required=deployment_in.ram_required,
            gpu_required=deployment_in.gpu_required,
            cluster_id=cluster.id,
            status=DeploymentStatus.PENDING.name,
            priority=deployment_in.priority,
            docker_image=deployment_in.docker_image
        )

        self.db.add(deployment)
        self.db.commit()
        self.db.refresh(deployment)
        return deployment

    def update_cluster_resources(self, deployment: Deployment, cluster: Type[Cluster]):
        """Update the cluster's available resources after a new deployment."""
        cluster.cpu_available -= deployment.cpu_required
        cluster.ram_available -= deployment.ram_required
        cluster.gpu_available -= deployment.gpu_required

    def handle_deployment(self, deployment_in: DeploymentCreate, preemption_strategy: str, cluster_id: int):
        """Main method to handle the entire deployment process."""
        cluster = self.get_cluster(cluster_id)
        self.check_user_permission(cluster)

        schedule = self.get_preemption_schedule(preemption_strategy, cluster, deployment_in)
        self.apply_preemption(schedule, cluster)

        deployment = self.create_new_deployment(deployment_in, cluster)
        self.update_cluster_resources(deployment, cluster)

        self.db.add(deployment)
        self.db.commit()
        self.db.refresh(deployment)

        return deployment
