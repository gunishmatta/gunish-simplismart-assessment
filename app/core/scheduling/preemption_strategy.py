from abc import ABC, abstractmethod
from typing import Any, Dict

from sqlalchemy.orm import Session

from app.models.cluster import Cluster
from app.schemas.deploymentresponse import DeploymentCreate


class PreemptionStrategy(ABC):
	"""
	Abstract base class for preemption strategies. Different algorithms can inherit
	from this class and implement the `preempt` method.
	"""

	@abstractmethod
	def preempt(self, db: Session, cluster: Cluster, deployment_in: DeploymentCreate)-> Dict[str, Any]:
		"""
		Preempt lower priority deployments to make room for the new deployment.

		Args:
			db: The database session.
			cluster: The cluster where the deployment is to be scheduled.
			deployment_in: The new deployment to be scheduled.

		Raises:
			HTTPException: If no resources are available after preemption.
		"""
		pass
