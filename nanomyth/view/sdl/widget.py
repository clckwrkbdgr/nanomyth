"""
SDL-based engine organize display output as a set of separate widgets.
"""
import pygame
from ...math import Point

class ImageWidget:
	""" Displays full image.
	"""
	def __init__(self, image, topleft):
		""" Creates widget to display given image
		starting from topleft position.
		"""
		self.topleft = Point(topleft)
		self.image = image
	def draw(self, engine):
		image = self.image
		if isinstance(self.image, str):
			image = engine.get_image(self.image)
		engine.render_texture(image.get_texture(), self.topleft)

class TileMapWidget:
	""" Displays a map of tiles
	"""
	def __init__(self, tilemap, topleft):
		""" Creates widget to display given Matrix of tiles
		starting from topleft position.
		Tiles are either Images or image names in engine's image list.
		"""
		self.topleft = Point(topleft)
		self.tilemap = tilemap
	def draw(self, engine):
		for pos in self.tilemap:
			image = engine.get_image(self.tilemap.cell(pos))
			tile_size = image.get_size()
			image_pos = Point(pos.x * tile_size.width, pos.y * tile_size.height)
			engine.render_texture(image.get_texture(), self.topleft + image_pos)

class TextLineWidget:
	""" Displays single-line text using pixel font. """
	def __init__(self, font, topleft, text=""):
		""" Creates widget with Font object at specified position.
		Optional initial text can be provided; it can be changed at any moment using set_text().
		"""
		self.topleft = Point(topleft)
		self.font = font
		self.text = text
	def set_text(self, new_text):
		self.text = new_text
	def draw(self, engine):
		image_pos = Point()
		for pos, letter in enumerate(self.text):
			image = self.font.get_letter_image(letter)
			engine.render_texture(image.get_texture(), self.topleft + image_pos)
			tile_size = image.get_size()
			image_pos.x += tile_size.width

class LevelMapWidget:
	""" Displays a game.Map class.
	"""
	def __init__(self, level_map, topleft):
		""" Creates widget to display given Map (of Tile objects)
		starting from topleft position.
		"""
		self.topleft = Point(topleft)
		self.level_map = level_map
	def draw(self, engine):
		for pos, tile in self.level_map.iter_tiles():
			for image_name in tile.get_images():
				image = engine.get_image(image_name)
				tile_size = image.get_size()
				image_pos = Point(pos.x * tile_size.width, pos.y * tile_size.height)
				engine.render_texture(image.get_texture(), self.topleft + image_pos)
