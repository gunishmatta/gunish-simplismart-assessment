from typing import Type

from app.core.scheduling.preemption_strategy import PreemptionStrategy
from app.core.scheduling.priority_preemption import PriorityPreemptionStrategy


class PreemptionSchedulingFactory:

	@staticmethod
	def get_preemption_strategy(strategy_type: str) -> PriorityPreemptionStrategy:
		"""
		Factory function to return the appropriate preemption strategy class.

		Args:
			strategy_type: The type of preemption strategy (e.g., "priority", "resource", "time").

		Returns:
			PreemptionStrategy class.
		"""
		strategies = {
			"priority": PriorityPreemptionStrategy,
		}
		strategy_class = strategies.get(strategy_type, PriorityPreemptionStrategy)
		return strategy_class()
