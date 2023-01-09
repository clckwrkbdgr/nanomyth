from .world import World
from .savegame import Savefile
from ..math import Point
from .actor import Direction
from ..utils.meta import typed

class Game:
	""" Main game object.
	The root of everything.
	"""
	def __init__(self):
		self._world = World()
		self._trigger_actions = {}
		self._on_change_map = None
	def on_change_map(self, callback): # TODO typed(callback type)
		""" Sets handler for the event of changing current map,
		e.g. moving between maps or loading new world.
		"""
		self._on_change_map = callback
	def get_world(self):
		""" Returns world object.
		As it can be completely replaced upon loading from savefile,
		this is the only valid access. Direct acces to field .world is discouraged.
		"""
		return self._world
	@typed(World)
	def load_world(self, new_world):
		""" Replaces World object with a new one.
		Used for loading savegames etc.
		"""
		self._world = new_world
		if self._on_change_map:
			self._on_change_map(self._world.get_current_map())
	@typed(Savefile)
	def save_to_file(self, savefile, force=False):
		""" Saves game state to the file using Savefile instance.
		Returns True if was saved successfully, False if savefile already exists.
		With force=True overwrites existing savefile.
		"""
		if savefile.exists() and not force:
			return False
		savefile.save(self._world)
		return True
	@typed(Savefile)
	def load_from_file(self, savefile):
		""" Loads game state from the file using Savefile instance.
		"""
		new_world = savefile.load()
		if not new_world: # pragma: no cover -- should not reach here in properly developed game.
			return False
		self.load_world(new_world)
		return True
	@typed(str)
	def register_trigger_action(self, action_name, action_callback): # TODO typed(callback type)
		""" Register actual callback function under a name,
		so it can be referred later, e.g. when loading TMX map.
		"""
		self._trigger_actions[action_name] = action_callback
	@typed(str)
	def get_trigger_action(self, action_name):
		""" Returns previously registered trigger callback by name. """
		return self._trigger_actions[action_name]

	@typed((Point, tuple, list, Direction))
	def shift_player(self, shift):
		""" Moves player character on the current map by given shift.
		See details in Map.shift_player.
		"""
		self._world.shift_player(shift,
				trigger_registry=self.get_trigger_action,
				on_change_map=self._on_change_map)
