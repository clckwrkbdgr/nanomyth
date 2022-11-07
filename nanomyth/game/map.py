from ..math import Matrix, Point
from . import actor

class Terrain:
	""" Represents single map tile of terrain.
	"""
	def __init__(self, images):
		""" Creates tile with specified images.
		If there are more than one images, they are drawn in the given order.
		E.g. ['basic grass', 'tree']
		"""
		self.images = images
	def get_images(self):
		""" Returns list of images for the terrail tile. """
		return self.images

class ActorOnMap:
	def __init__(self, pos, actor):
		self.pos = Point(pos)
		self.actor = actor

class Map:
	""" 5x5 level map.
	"""
	def __init__(self):
		self.tiles = Matrix((5, 5), Terrain([]))
		self.actors = []
	def set_tile(self, pos, tile):
		self.tiles.set_cell(pos, tile)
	def get_tile(self, pos):
		return self.tiles.cell(pos)
	def add_actor(self, pos, actor):
		""" Places actor on specified position. """
		self.actors.append(ActorOnMap(pos, actor))
	def shift_player(self, shift):
		""" Moves player character by given shift. """
		player = next(_ for _ in self.actors if isinstance(_.actor, actor.Player))
		new_pos = player.pos + shift
		if not self.tiles.valid(new_pos):
			return
		player.pos = new_pos
	def iter_tiles(self):
		""" Iterates over tiles.
		Yields pairs (pos, tile).
		"""
		return ((pos, self.tiles.cell(pos)) for pos in self.tiles)
	def iter_actors(self):
		""" Iterate over placed actors (characters, monsters).
		Yields pairs (pos, actor).
		"""
		return ((_.pos, _.actor) for _ in self.actors)
