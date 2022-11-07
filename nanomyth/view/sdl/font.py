"""
Text-related functionality.
"""
import itertools
import pygame
from ...math import Point, Rect
from .image import ImageRegion

class FixedWidthFont:
	""" Pixel font with fixed width (monospace) glyphs.

	Should be loaded from font grid tileset where every letter has the same size.
	"""
	def __init__(self, tileset, letter_mapping):
		""" Creates font from tileset using given letter mapping.
		Letter mapping is a string of letters that should match unwrapped grid (row by row) starting from the topleft corner.
		Letter mapping could be shorter than overall size of the font tileset grid - unused tiles will be ignored.
		"""
		self.tileset = tileset
		tile_grid = itertools.chain.from_iterable((Point(x, y) for x in range(tileset.size.width)) for y in range(tileset.size.height))
		self.letter_mapping = dict(zip(letter_mapping, tile_grid))
	def get_letter_image(self, letter):
		""" Returns sub-image for given letter. """
		assert len(letter) == 1
		return self.tileset.get_tile(self.letter_mapping[letter])

class ProportionalFont:
	""" Pixel font with proportional glyphs.
	Glyphs are squeezed horizontally from both sides to pack text more densily by skipping empty (transparent) columns in each grid tile.

	Should be loaded from font grid tileset where every letter has the same size.
	"""
	def __init__(self, tileset, letter_mapping, space_width=None, transparent_color=0):
		""" Creates font from tileset using given letter mapping.
		Letter mapping is a string of letters that should match unwrapped grid (row by row) starting from the topleft corner.
		Letter mapping could be shorter than overall size of the font tileset grid - unused tiles will be ignored.

		Space width is a min width for a completely empty tile (which normally represents space character, ' ').
		If not specified, full tile width is used.

		Uses given transparent color value to consider pixels "empty".
		By default is 0 (fully transparent pixel).
		"""
		self.tileset = tileset
		tile_grid = itertools.chain.from_iterable((Point(x, y) for x in range(tileset.size.width)) for y in range(tileset.size.height))
		self.letter_mapping = dict(zip(letter_mapping, tile_grid))
		self.bound_rects = {}
		with pygame.PixelArray(self.tileset.get_texture()) as pixels:
			for letter in self.letter_mapping.keys():
				letter_image = self.tileset.get_tile(self.letter_mapping[letter])
				letter_rect = letter_image.get_rect()

				actual_left = None
				for x in range(letter_rect.left, letter_rect.right + 1):
					all_transparent = all(pixels[x, y] == transparent_color for y in range(letter_rect.top, letter_rect.bottom + 1))
					if not all_transparent:
						actual_left = x
						break
				actual_right = None
				for x in reversed(range(letter_rect.left, letter_rect.right + 1)):
					all_transparent = all(pixels[x, y] == transparent_color for y in range(letter_rect.top, letter_rect.bottom + 1))
					if not all_transparent:
						actual_right = x
						break
				if actual_left is None or actual_right is None:
					actual_left = letter_rect.left
					actual_right = letter_rect.left + (space_width or letter_rect.width) - 1
				left_bound = actual_left - letter_rect.left
				right_bound = actual_right - letter_rect.left
				self.bound_rects[letter] = Rect((left_bound, 0), (right_bound - left_bound + 1, letter_rect.height))
	def get_letter_image(self, letter):
		""" Returns sub-image for given letter. """
		assert len(letter) == 1
		return ImageRegion(self.tileset.get_tile(self.letter_mapping[letter]), self.bound_rects[letter])
