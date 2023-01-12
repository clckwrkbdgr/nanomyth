from ..utils.meta import typed

class Trigger:
	""" Provides means to trigger user-defined event.
	Once player steps on it, event is triggered and attached action is taken.
	"""
	@typed(str)
	def __init__(self, trigger_name):
		""" Creates trigger with given name,
		which will be executed when trigger is activated.
		"""
		self._trigger_name = trigger_name
	def activate(self, trigger_registry, *params): # TODO not typed.
		""" Activates trigger by name using given trigger registry.
		Registry should be a callable that accepts trigger name and returns actual callback.
		"""
		if self._trigger_name:
			trigger_registry(self._trigger_name)(*params)
