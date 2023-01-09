""" Global game world.
"""
from .map import Map, Portalling
from .quest import Quest
from .actor import NPC, Player, Direction
from ..math import Point
from ..utils.meta import typed

class World:
	""" World of maps.
	"""
	def __init__(self):
		""" Creates empty world.
		Add maps via add_map() and set_current_map()
		"""
		self._maps = {}
		self._current_map = None
		self._quests = {}
	@typed(str, Map)
	def add_map(self, map_name, level_map):
		""" Adds new map under given name.
		If there were not maps, sets this one as current.
		"""
		if not self._maps:
			self._current_map = map_name
		self._maps[map_name] = level_map
		return level_map
	@typed(str)
	def get_map(self, map_name):
		""" Returns Map object registered under given name. """
		return self._maps[map_name]
	@typed(str)
	def set_current_map(self, map_name):
		""" Sets current map by name. """
		self._current_map = map_name
	def get_current_map(self):
		""" Returns current map object. """
		return self._maps[self._current_map]
	@typed(Quest)
	def add_quest(self, quest):
		""" Registers new quest under its ID. """
		self._quests[quest.id] = quest
	@typed(str)
	def get_quest(self, quest_name):
		""" Returns quest by ID. """
		return self._quests[quest_name]
	def get_active_quests(self):
		""" Returns list of all the active quests. """
		return [quest for quest in self._quests.values() if quest.is_active()]
	@typed((NPC, Player), Map, (Point, tuple, list), source_map=Map)
	def transfer_actor(self, actor, dest_map, dest_pos, source_map=None):
		""" Transfer actor from one map to another and place at specified position.
		If source_map is not specified, current map is used.
		"""
		if not source_map:
			source_map = self.get_current_map()
		source_map.remove_actor(actor)
		dest_map.add_actor(dest_pos, actor)
	@typed((Point, tuple, list, Direction))
	def shift_player(self, shift, trigger_registry=None, on_change_map=None): # TODO typing for remaining args.
		""" Moves player character on the current map by given shift.
		See details in Map.shift_player.
		May move actors across the map or perform other global-world actions.
		If on_change_map is supplied, it is a callable that accepts Map object
		and is called when current map is changed.
		"""
		try:
			self.get_current_map().shift_player(shift, trigger_registry=trigger_registry, quest_registry=self.get_quest)
		except Portalling as p:
			dest_map_name, entrance_pos = p.portal.get_dest()
			dest_map = self.get_map(dest_map_name)
			self.transfer_actor(p.actor, dest_map, entrance_pos)
			self.set_current_map(dest_map_name)
			if on_change_map:
				on_change_map(self.get_current_map())
