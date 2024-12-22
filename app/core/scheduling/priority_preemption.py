from typing import Any, Dict, List, Type

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.scheduling.preemption_strategy import PreemptionStrategy
from app.models.cluster import Cluster
from app.models.deployment import Deployment
from app.schemas.deploymentresponse import DeploymentCreate


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
		if (cluster.cpu_available >= deployment_in.cpu_required and
				cluster.ram_available >= deployment_in.ram_required and
				cluster.gpu_available >= deployment_in.gpu_required):
			return {
				"preempted_deployments": [],
				"remaining_resources": {
					"cpu": cluster.cpu_available - deployment_in.cpu_required,
					"ram": cluster.ram_available - deployment_in.ram_required,
					"gpu": cluster.gpu_available - deployment_in.gpu_required
				},
				"deployment_in": deployment_in
			}

		# Preemption logic
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

		epsilon = 1e-6  # Tolerance for floating-point comparisons

		for deployment in low_priority_deployments:
			new_cpu = schedule["remaining_resources"]["cpu"] + deployment.cpu_required
			new_ram = schedule["remaining_resources"]["ram"] + deployment.ram_required
			new_gpu = schedule["remaining_resources"]["gpu"] + deployment.gpu_required

			if (new_cpu + epsilon >= deployment_in.cpu_required and
					new_ram + epsilon >= deployment_in.ram_required and
					new_gpu + epsilon >= deployment_in.gpu_required):
				schedule["preempted_deployments"].append(deployment)
				schedule["remaining_resources"]["cpu"] = new_cpu
				schedule["remaining_resources"]["ram"] = new_ram
				schedule["remaining_resources"]["gpu"] = new_gpu

				deployment.status = "Preempted"
				db.commit()
				break

		if not schedule["preempted_deployments"]:
			raise HTTPException(
				status_code=400,
				detail=(
					f"Unable to find deployable resources for the request. "
					f"Requested: CPU={deployment_in.cpu_required}, RAM={deployment_in.ram_required}, GPU={deployment_in.gpu_required}. "
					f"Available: CPU={cluster.cpu_available}, RAM={cluster.ram_available}, GPU={cluster.gpu_available}."
				)
			)

		return schedule