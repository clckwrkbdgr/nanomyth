class Trigger:
	""" Provides means to trigger user-defined event.
	Once player steps on it, event is triggered and attached action is taken.
	"""
	def __init__(self, trigger_name):
		""" Creates trigger with given name,
		which will be executed when trigger is activated.
		"""
		self.trigger_name = trigger_name
	def activate(self, trigger_registry, *params):
		""" Activates trigger by name using given trigger registry.
		Registry should be a callable that accepts trigger name and returns actual callback.
		"""
		if self.trigger_name:
			trigger_registry(self.trigger_name)(*params)

