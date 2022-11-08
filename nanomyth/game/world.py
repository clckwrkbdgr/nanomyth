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
	def add_map(self, map_name, level_map):
		""" Adds new map under given name.
		If there were not maps, sets this one as current.
		"""
		if not self.maps:
			self.current_map = map_name
		self.maps[map_name] = level_map
		return level_map
	def set_current_map(self, map_name):
		""" Sets current map by name. """
		self.current_map = map_name
	def get_current_map(self):
		""" Returns current map object. """
		return self.maps[self.current_map]
	def shift_player(self, shift):
		try:
			self.get_current_map().shift_player(shift)
		except Portalling as p:
			self.set_current_map(p.portal.dest_map)
			self.get_current_map().add_actor(
					p.portal.entrance_pos,
					p.player,
					)
