""" Global game world.
"""
from .map import Portalling

class World:
	""" World of maps.
	"""
	def __init__(self):
		""" Creates empty world.
		Add maps via add_map() and set_current_map()
		"""
		self.maps = {}
		self.current_map = None
		self.quests = {}
	def add_map(self, map_name, level_map):
		""" Adds new map under given name.
		If there were not maps, sets this one as current.
		"""
		if not self.maps:
			self.current_map = map_name
		self.maps[map_name] = level_map
		return level_map
	def get_map(self, map_name):
		""" Returns Map object registered under given name. """
		return self.maps[map_name]
	def set_current_map(self, map_name):
		""" Sets current map by name. """
		self.current_map = map_name
	def get_current_map(self):
		""" Returns current map object. """
		return self.maps[self.current_map]
	def add_quest(self, quest):
		""" Registers new quest under its ID. """
		self.quests[quest.id] = quest
	def get_quest(self, quest_name):
		""" Returns quest by ID. """
		return self.quests[quest_name]
	def get_active_quests(self):
		""" Returns list of all the active quests. """
		return [quest for quest in self.quests.values() if quest.is_active()]
	def shift_player(self, shift, trigger_registry=None, on_change_map=None):
		""" Moves player character on the current map by given shift.
		See details in Map.shift_player.
		May move actors across the map or perform other global-world actions.
		If on_change_map is supplied, it is a callable that accepts Map object
		and is called when current map is changed.
		"""
		try:
			self.get_current_map().shift_player(shift, trigger_registry=trigger_registry, quest_registry=self.get_quest)
		except Portalling as p:
			self.set_current_map(p.portal.dest_map)
			self.get_current_map().add_actor(
					p.portal.entrance_pos,
					p.player,
					)
			if on_change_map:
				on_change_map(self.get_current_map())
