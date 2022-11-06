from ..math import Matrix

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

class Map:
	""" 5x5 level map.
	"""
	def __init__(self):
		self.tiles = Matrix((5, 5), Terrain([]))
	def set_tile(self, pos, tile):
		self.tiles.set_cell(pos, tile)
	def get_tile(self, pos):
		return self.tiles.cell(pos)
	def iter_tiles(self):
		""" Iterates over tiles.
		Yields pairs (pos, tile).
		"""
		return ((pos, self.tiles.cell(pos)) for pos in self.tiles)
