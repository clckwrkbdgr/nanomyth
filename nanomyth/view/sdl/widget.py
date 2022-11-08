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
	""" Displays level map using static camera (viewport is not moving).

	WARNING: As camera is static, map should fit within the screen,
	outside tiles are accessible but will not be displayed!
	"""
	def __init__(self, level_map, topleft):
		""" Creates widget to display given Map (of Tile objects)
		starting from topleft position.
		"""
		self.topleft = Point(topleft)
		self.level_map = level_map
	def set_map(self, new_level_map):
		""" Switches displayed level map. """
		self.level_map = new_level_map
	def draw(self, engine):
		for pos, tile in self.level_map.iter_tiles():
			for image_name in tile.get_images():
				image = engine.get_image(image_name)
				tile_size = image.get_size()
				image_pos = Point(pos.x * tile_size.width, pos.y * tile_size.height)
				engine.render_texture(image.get_texture(), self.topleft + image_pos)
		for pos, actor in self.level_map.iter_actors():
			image = engine.get_image(actor.get_sprite())
			tile_size = image.get_size()
			image_pos = Point(pos.x * tile_size.width, pos.y * tile_size.height)
			engine.render_texture(image.get_texture(), self.topleft + image_pos)

class MenuItem:
	""" Menu item with text caption and two modes (normal/highlighted). """
	def __init__(self, topleft, button, caption, button_highlighted=None, caption_highlighted=None, caption_shift=None):
		""" Creates selectable menu item widget.

		Draws button using giving Widget (e.g. ImageWidget or TileMapWidget)
		and overpaints with given caption widget (usually a TextLine).
		Button and caption have additional "highlighted" variant which is used if menu item is highlighted via .make_highlighted(True)

		Both captions and buttons can be None, missing widgets are simply skipped.

		Buttons and captions are forced to the topleft position of the menu item.
		If caption_shift (of Point or tuple type) is provided, caption in shifted relative to the topleft posision (and button widget).
		"""
		self.topleft = Point(topleft)
		self.button = button
		if self.button:
			self.button.topleft = self.topleft
		self.button_highlighted = button_highlighted or self.button
		if self.button_highlighted:
			self.button_highlighted.topleft = self.topleft
		caption_shift = Point(caption_shift or (0, 0))
		self.caption = caption
		if self.caption:
			self.caption.topleft = self.topleft + caption_shift
		self.caption_highlighted = caption_highlighted or self.caption
		if self.caption_highlighted:
			self.caption_highlighted.topleft = self.topleft + caption_shift
		self.highlighted = False
	def make_highlighted(self, value):
		""" Makes current item highlighted. """
		self.highlighted = bool(value)
	def draw(self, engine):
		button = self.button_highlighted if self.highlighted else self.button
		caption = self.caption_highlighted if self.highlighted else self.caption
		if button:
			button.draw(engine)
		if caption:
			caption.draw(engine)
