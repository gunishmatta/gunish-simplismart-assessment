from typing import Any, Dict, List, Type

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.scheduling.preemption_strategy import PreemptionStrategy
from app.models.cluster import Cluster
from app.models.deployment import Deployment
from app.schemas.deployment import DeploymentCreate


class PriorityPreemptionStrategy(PreemptionStrategy):
	"""
	Preempt deployments based on priority. Lower priority deployments will be
	preempted first to free up resources for higher priority deployments.
	"""

	def preempt(self, db: Session, cluster: Type[Cluster], deployment_in: DeploymentCreate) -> Dict[str, Any]:
		"""
		Preempt deployments based on priority to make room for a higher priority deployment.

		Returns a schedule indicating which deployments to preempt and the remaining resources.
		"""
		low_priority_deployments = db.query(Deployment).filter(
			Deployment.cluster_id == cluster.id,
			Deployment.status == "Running"
		).order_by(Deployment.priority.asc()).all()

		schedule = {
			"preempted_deployments": [],
			"remaining_resources": {
				"cpu": cluster.cpu_available,
				"ram": cluster.ram_available,
				"gpu": cluster.gpu_available
			},
			"deployment_in": deployment_in
		}

		for deployment in low_priority_deployments:
			if (schedule["remaining_resources"]["cpu"] + deployment.cpu_required >= deployment_in.cpu_required and
					schedule["remaining_resources"]["ram"] + deployment.ram_required >= deployment_in.ram_required and
					schedule["remaining_resources"]["gpu"] + deployment.gpu_required >= deployment_in.gpu_required):
				schedule["preempted_deployments"].append(deployment)
				schedule["remaining_resources"]["cpu"] += deployment.cpu_required
				schedule["remaining_resources"]["ram"] += deployment.ram_required
				schedule["remaining_resources"]["gpu"] += deployment.gpu_required

				deployment.status = "Preempted"
				break

		if not schedule["preempted_deployments"]:
			raise HTTPException(status_code=400, detail="Unable to find deployable resources for the request.")

		return schedule
