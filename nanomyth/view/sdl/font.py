"""
Text-related functionality.
"""
import itertools
import pygame
from ...math import Point, Rect
from .image import ImageRegion
from .. import utils
from ...utils.meta import typed

class AbstractFont:
	""" Abstract base for every Font class. """
	@typed(str)
	def get_letter_image(self, letter): # pragma: no cover
		""" Should return sub-image for given letter. """
		raise NotImplementedError()

class TilesetFont(AbstractFont):
	""" Abstract base for pixel fonts built on a tileset of pixel glyphs.
	"""
	def __init__(self, tileset, letter_mapping):
		""" Creates font from tileset using given letter mapping.
		Letter mapping is a string of letters that should match unwrapped grid (row by row) starting from the topleft corner.
		Letter mapping could be shorter than overall size of the font tileset grid - unused tiles will be ignored.
		"""
		self._tileset = tileset
		tile_grid = itertools.chain.from_iterable((Point(x, y) for x in range(tileset.size.width)) for y in range(tileset.size.height))
		self._letter_mapping = dict(zip(letter_mapping, tile_grid))

class FixedWidthFont(TilesetFont):
	""" Pixel font with fixed width (monospace) glyphs.

	Should be loaded from font grid tileset where every letter has the same size.
	"""
	@typed(str)
	def get_letter_image(self, letter):
		""" Returns sub-image for given letter. """
		assert len(letter) == 1
		return self._tileset.get_tile(self._letter_mapping[letter])

class ProportionalFont(TilesetFont):
	""" Pixel font with proportional glyphs.
	Glyphs are squeezed horizontally from both sides to pack text more densily by skipping empty (transparent) columns in each grid tile.

	Should be loaded from font grid tileset where every letter has the same size.
	"""
	def __init__(self, tileset, letter_mapping, space_width=None, transparent_color=0):
		""" Creates font from tileset using given letter mapping (see TilesetFont for details).

		Space width is a min width for a completely empty tile (which normally represents space character, ' ').
		If not specified, full tile width is used.

		Uses given transparent color value to consider pixels "empty".
		By default is 0 (fully transparent pixel).
		"""
		super().__init__(tileset, letter_mapping)
		self._bound_rects = {}
		with pygame.PixelArray(self._tileset.get_texture()) as pixels:
			for letter in self._letter_mapping.keys():
				letter_image = self._tileset.get_tile(self._letter_mapping[letter])
				letter_rect = letter_image.get_rect()
				self._bound_rects[letter] = utils.graphics.get_bounding_rect(letter_rect, lambda p: (pixels[p.x, p.y] == transparent_color), space_width=space_width)
	@typed(str)
	def get_letter_image(self, letter):
		""" Returns sub-image for given letter. """
		assert len(letter) == 1
		return ImageRegion(self._tileset, self._bound_rects[letter])
