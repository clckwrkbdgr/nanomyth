import pygame
from ...math import Point, Size

class Image:
	def __init__(self, filename):
		self._texture = pygame.image.load(str(filename))
	def get_texture(self):
		return self._texture

class TileSetImage:
	def __init__(self, filename, size):
		self._texture = pygame.image.load(str(filename))
		self.size = Size(size)
		self.tile_size = Size(
				self._texture.get_width() / self.size.width,
				self._texture.get_height() / self.size.height,
				)
	def get_tile(self, pos):
		pos = Point(pos)
		return TileImage(self, pos)
	def get_texture(self):
		return self._texture

class TileImage:
	def __init__(self, tileset, pos):
		self.tileset = tileset
		self.pos = Point(pos)
	def get_texture(self):
		return self.tileset.get_texture().subsurface(pygame.Rect(
			self.pos.x * self.tileset.tile_size.width,
			self.pos.y * self.tileset.tile_size.height,
			self.tileset.tile_size.width,
			self.tileset.tile_size.height,
			))
