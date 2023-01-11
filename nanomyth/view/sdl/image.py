"""
Various set of classes that represents images (tiles, sprites, UI etc).
"""
import os
from pathlib import Path
import pygame
from ...math import Point, Size, Rect
from ...utils.meta import typed, fieldproperty

class AbstractImage:
	def get_size(self): # pragma: no cover
		""" Should return full size of the image. """
		raise NotImplementedError()
	def get_texture(self): # pragma: no cover
		""" Should return SDL Surface object. """
		raise NotImplementedError()

class Image(AbstractImage):
	""" Basic image to be displayed in full size.
	"""
	filename = fieldproperty('_filename', 'Path to the image file.')

	def __init__(self, filename):
		""" Creates image from given file. """
		self._filename = Path(filename).resolve()
		self._texture = pygame.image.load(str(filename))
	def get_size(self):
		""" Full image size. """
		return Size(
				self._texture.get_width(),
				self._texture.get_height(),
				)
	@typed((Rect, tuple, list))
	def get_region(self, rect):
		""" Returns sub-image of given region. """
		return ImageRegion(self, Rect(rect))
	def get_texture(self):
		return self._texture

class ImageRegion(AbstractImage):
	""" Part of the bigger image.
	"""
	def __init__(self, image, rect):
		""" Creates image region.
		"""
		self._image = image
		self._rect = rect
	def get_size(self):
		""" Size of the region. """
		return self._rect.size
	def get_texture(self):
		return self._image.get_texture().subsurface(pygame.Rect(
			self._rect.left,
			self._rect.top,
			self._rect.width,
			self._rect.height,
			))

class TileSetImage(Image):
	""" Image that contains a tile set (usually a table of smaller images of the same size).
	"""
	size = fieldproperty('_size', 'Dimensions of the tile table.')
	tile_size = fieldproperty('_tile_size', 'Size of a single tile.')

	def __init__(self, filename, size):
		""" Creates image tile set from given file.
		Treats it as a table of given size.
		"""
		super().__init__(filename)
		self._size = Size(size)
		self._tile_size = Size(
				self._texture.get_width() // self._size.width,
				self._texture.get_height() // self._size.height,
				)
	@typed((Point, tuple, list))
	def get_tile(self, pos):
		""" Returns TileImage for specified position in tile table. """
		pos = Point(pos)
		return TileImage(self, pos)
	def get_texture(self):
		return self._texture

class TileImage(AbstractImage):
	""" Single tile from a tile set. """
	def __init__(self, tileset, pos):
		""" Creates a tile from given tile set and a position in table. """
		self._tileset = tileset
		self._pos = Point(pos)
	def get_size(self):
		""" Returns size of a single tile. """
		return self._tileset.tile_size
	def get_rect(self):
		return Rect((
			self._pos.x * self._tileset.tile_size.width,
			self._pos.y * self._tileset.tile_size.height,
			), self._tileset.tile_size)
	def get_texture(self):
		return self._tileset.get_texture().subsurface(pygame.Rect(*(self.get_rect())))
