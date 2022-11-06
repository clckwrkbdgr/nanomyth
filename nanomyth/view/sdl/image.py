"""
Various set of classes that represents images (tiles, sprites, UI etc).
"""
import pygame
from ...math import Point, Size

class Image:
	""" Basic image to be displayed in full size.
	"""
	def __init__(self, filename):
		""" Creates image from given file. """
		self._texture = pygame.image.load(str(filename))
	def get_size(self):
		""" Full image size. """
		return Size(
				self._texture.get_width(),
				self._texture.get_height(),
				)
	def get_texture(self):
		return self._texture

class TileSetImage(Image):
	""" Image that contains a tile set (usually a table of smaller images of the same size).
	"""
	def __init__(self, filename, size):
		""" Creates image tile set from given file.
		Treats it as a table of given size.
		"""
		super().__init__(filename)
		self.size = Size(size)
		self.tile_size = Size(
				self._texture.get_width() / self.size.width,
				self._texture.get_height() / self.size.height,
				)
	def get_tile(self, pos):
		""" Returns TileImage for specified position in tile table. """
		pos = Point(pos)
		return TileImage(self, pos)
	def get_texture(self):
		return self._texture

class TileImage:
	""" Single tile from a tile set. """
	def __init__(self, tileset, pos):
		""" Creates a tile from given tile set and a position in table. """
		self.tileset = tileset
		self.pos = Point(pos)
	def get_size(self):
		""" Returns size of a single tile. """
		return self.tileset.tile_size
	def get_texture(self):
		return self.tileset.get_texture().subsurface(pygame.Rect(
			self.pos.x * self.tileset.tile_size.width,
			self.pos.y * self.tileset.tile_size.height,
			self.tileset.tile_size.width,
			self.tileset.tile_size.height,
			))
