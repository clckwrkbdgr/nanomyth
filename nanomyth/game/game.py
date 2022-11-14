from .world import World

class Game:
	""" Main game object.
	The root of everything.
	"""
	def __init__(self):
		self.world = World()
		self.trigger_actions = {}
		self._on_change_map = None
	def on_change_map(self, callback):
		""" Sets handler for the event of changing current map,
		e.g. moving between maps or loading new world.
		"""
		self._on_change_map = callback
	def get_world(self):
		""" Returns world object.
		As it can be completely replaced upon loading from savefile,
		this is the only valid access. Direct acces to field .world is discouraged.
		"""
		return self.world
	def load_world(self, new_world):
		""" Replaces World object with a new one.
		Used for loading savegames etc.
		"""
		self.world = new_world
		if self._on_change_map:
			self._on_change_map(self.world.get_current_map())
	def save_to_file(self, savefile, force=False):
		""" Saves game state to the file using Savefile instance.
		Returns True if was saved successfully, False if savefile already exists.
		With force=True overwrites existing savefile.
		"""
		if savefile.exists() and not force:
			return False
		savefile.save(self.world)
		return True
	def load_from_file(self, savefile):
		""" Loads game state from the file using Savefile instance.
		"""
		new_world = savefile.load()
		if not new_world: # pragma: no cover -- should not reach here in properly developed game.
			return False
		self.load_world(new_world)
		return True
	def register_trigger_action(self, action_name, action_callback):
		""" Register actual callback function under a name,
		so it can be referred later, e.g. when loading TMX map.
		"""
		self.trigger_actions[action_name] = action_callback
	def get_trigger_action(self, action_name):
		""" Returns previously registered trigger callback by name. """
		return self.trigger_actions[action_name]

	def shift_player(self, shift):
		""" Moves player character on the current map by given shift.
		See details in Map.shift_player.
		"""
		self.world.shift_player(shift,
				trigger_registry=self.get_trigger_action,
				on_change_map=self._on_change_map)
