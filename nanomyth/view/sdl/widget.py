"""
SDL-based engine organize display output as a set of separate widgets.
"""
import pygame
from ...math import Point, Size, Matrix

class ImageWidget:
	""" Displays full image.
	"""
	def __init__(self, image):
		""" Creates widget to display image.
		"""
		self.image = image
	def draw(self, engine, topleft):
		image = self.image
		if isinstance(self.image, str):
			image = engine.get_image(self.image)
		engine.render_texture(image.get_texture(), topleft)

class TileMapWidget:
	""" Displays a map of tiles
	"""
	def __init__(self, tilemap):
		""" Creates widget to display given Matrix of tiles.
		Tiles are either Images or image names in engine's image list.
		"""
		self.tilemap = tilemap
	def get_size(self, engine):
		""" Returns bounding size of the tile grid. """
		tile_size = engine.get_image(self.tilemap.cell((0, 0))).get_size()
		return Size(
				self.tilemap.width * tile_size.width, 
				self.tilemap.height * tile_size.height,
				)
	def draw(self, engine, topleft):
		for pos in self.tilemap:
			image = engine.get_image(self.tilemap.cell(pos))
			tile_size = image.get_size()
			image_pos = Point(pos.x * tile_size.width, pos.y * tile_size.height)
			engine.render_texture(image.get_texture(), topleft + image_pos)

class PanelWidget:
	""" Draws panel made from tiles.
	"""
	def __init__(self, tilemap, size):
		""" Creates widget using tiles from given mapping.
		Tilemap should be a Matrix of 3x3 that covers every possible part:
		+ - + : Top-left and top-right corners, and plain top tile.
		| . | : Left and right tiles, plus middle/center tile that fills the insides.
		+ _ + : Bottom-left and bottom-right corners, and plain bottom tile.

		Size must be >= 2x2 so at least corners will be used.
		If passed size is less, it is automatically adjusted so it will be no less than 2x2.
		"""
		assert tilemap.size == Size(3, 3)
		size = Size(size)
		self.size = Size(max(size.width, 2), max(size.height, 2))
		panel_tiles = []
		for row_index in range(size.height):
			tilemap_y = 0 if row_index == 0 else (2 if row_index == size.height - 1 else 1)
			panel_tiles.append([tilemap.cell((0 if col_index == 0 else (2 if col_index == size.width - 1 else 1), tilemap_y))
				for col_index in range(size.width)
				])
		panel_tiles = Matrix.from_iterable(panel_tiles)
		self.tilemap_widget = TileMapWidget(panel_tiles)
	def get_size(self, engine):
		""" Returns bounding size of the panel. """
		return self.tilemap_widget.get_size(engine)
	def draw(self, engine, topleft):
		self.tilemap_widget.draw(engine, topleft)

class TextLineWidget:
	""" Displays single-line text using pixel font. """
	def __init__(self, font, text=""):
		""" Creates widget to display single text line with Font object.
		Optional initial text can be provided; it can be changed at any moment using set_text().
		"""
		self.font = font
		self.text = text
	def set_text(self, new_text):
		self.text = new_text
	def draw(self, engine, topleft):
		image_pos = Point()
		for pos, letter in enumerate(self.text):
			image = self.font.get_letter_image(letter)
			engine.render_texture(image.get_texture(), topleft + image_pos)
			tile_size = image.get_size()
			image_pos.x += tile_size.width

class LevelMapWidget:
	""" Displays level map using static camera (viewport is not moving).

	WARNING: As camera is static, map should fit within the screen,
	outside tiles are accessible but will not be displayed!
	"""
	def __init__(self, level_map):
		""" Creates widget to display given Map (of Tile objects).
		"""
		self.level_map = level_map
	def set_map(self, new_level_map):
		""" Switches displayed level map. """
		self.level_map = new_level_map
	def draw(self, engine, topleft):
		for pos, tile in self.level_map.iter_tiles():
			for image_name in tile.get_images():
				image = engine.get_image(image_name)
				tile_size = image.get_size()
				image_pos = Point(pos.x * tile_size.width, pos.y * tile_size.height)
				engine.render_texture(image.get_texture(), topleft + image_pos)
		for pos, actor in self.level_map.iter_actors():
			image = engine.get_image(actor.get_sprite())
			tile_size = image.get_size()
			image_pos = Point(pos.x * tile_size.width, pos.y * tile_size.height)
			engine.render_texture(image.get_texture(), topleft + image_pos)

class MenuItem:
	""" Menu item with text caption and two modes (normal/highlighted). """
	def __init__(self, button, caption, button_highlighted=None, caption_highlighted=None, caption_shift=None):
		""" Creates selectable menu item widget.

		Draws button using giving Widget (e.g. ImageWidget or TileMapWidget)
		and overpaints with given caption widget (usually a TextLine).
		Button and caption have additional "highlighted" variant which is used if menu item is highlighted via .make_highlighted(True)

		Both captions and buttons can be None, missing widgets are simply skipped.

		Buttons and captions are forced to the topleft position of the menu item.
		If caption_shift (of Point or tuple type) is provided, caption in shifted relative to the topleft posision (and button widget).
		"""
		self.button = button
		self.button_highlighted = button_highlighted or self.button
		self.caption_shift = Point(caption_shift or (0, 0))
		self.caption = caption
		self.caption_highlighted = caption_highlighted or self.caption
		self.highlighted = False
	def make_highlighted(self, value):
		""" Makes current item highlighted. """
		self.highlighted = bool(value)
	def draw(self, engine, topleft):
		button = self.button_highlighted if self.highlighted else self.button
		caption = self.caption_highlighted if self.highlighted else self.caption
		if button:
			button.draw(engine, topleft)
		if caption:
			caption.draw(engine, topleft + self.caption_shift)

class MultilineTextWidget:
	""" Displays multiline text using pixel font
	with option to scroll if text is larger than the screen can fit.
	"""
	def __init__(self, font, size, text=""):
		""" Creates widget to display text with Font object.
		Text will fit into given size, auto-wrapped with option to scroll.
		Optional initial text can be provided; it can be changed at any moment using set_text().
		"""
		self.font = font
		self.size = size
		self.textlines = None
		self.set_text(text)
		self.top_line = 0
	def set_text(self, new_text):
		self.textlines = []
		for line in new_text.splitlines():
			line_width = []
			current_line = ''
			for letter in line:
				letter_width = self.font.get_letter_image(letter).get_size().width
				if sum(line_width) + letter_width > self.size.width:
					if ' ' in current_line:
						last_space_pos = current_line.rfind(' ')
						self.textlines.append(current_line[:last_space_pos].rstrip())
						current_line = current_line[last_space_pos+1:]
						line_width = line_width[last_space_pos+1:]
					else:
						self.textlines.append(current_line)
						current_line = ''
						line_width = []
						continue
				current_line += letter
				line_width.append(letter_width)
			self.textlines.append(current_line)
	def _number_of_lines_that_fit_the_screen(self):
		font_height = self.font.get_letter_image('W').get_size().height
		return self.size.height // font_height
	def get_top_line(self):
		""" Returns current topmost line. """
		return self.top_line
	def set_top_line(self, new_top_line):
		""" Set topmost line to display.
		It should be in range [0; total_lines - number_of_lines_that_fit_the_screen].
		"""
		new_top_line = max(0, new_top_line)
		new_top_line = min(new_top_line, len(self.textlines) - self._number_of_lines_that_fit_the_screen())
		self.top_line = new_top_line
	def can_scroll_up(self):
		""" Returns True if there are line higher than current viewport can display
		and it can be scrolled up.
		"""
		return self.top_line > 0
	def can_scroll_down(self):
		""" Returns True if there are line lower than current viewport can display
		and it can be scrolled down.
		"""
		return self.top_line + self._number_of_lines_that_fit_the_screen() < len(self.textlines)
	def get_visible_text_lines(self):
		""" Returns set of text lines that fit into the current viewport. """
		return self.textlines[self.top_line:self.top_line + self._number_of_lines_that_fit_the_screen()]
	def draw(self, engine, topleft):
		font_height = self.font.get_letter_image('W').get_size().height
		for row, textline in enumerate(self.get_visible_text_lines()):
			image_pos = Point(0, row * font_height)
			for pos, letter in enumerate(textline):
				image = self.font.get_letter_image(letter)
				engine.render_texture(image.get_texture(), topleft + image_pos)
				tile_size = image.get_size()
				image_pos.x += tile_size.width
