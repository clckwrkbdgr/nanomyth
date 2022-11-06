from ..math import Matrix

class Terrain:
	def __init__(self, images):
		self.images = images
	def get_images(self):
		return self.images

class Map:
	def __init__(self):
		self.tiles = Matrix((5, 5), Terrain([]))
	def set_tile(self, pos, tile):
		self.tiles.set_cell(pos, tile)
	def get_tile(self, pos):
		return self.tiles.cell(pos)
	def iter_tiles(self):
		return [(pos, self.tiles.cell(pos)) for pos in self.tiles]
