"""
SDL-based engine organize display output as a set of separate widgets.
"""
import pygame
from ...math import Point, Size, Matrix
from ..utils import math

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
		panel_tiles = math.tiled_panel(tilemap, size)
		self.size = panel_tiles.size
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
	def get_size(self, engine):
		""" Returns bounding size of the text line. """
		height = self.font.get_letter_image('W').get_size().height
		width = 0
		for pos, letter in enumerate(self.text):
			image = self.font.get_letter_image(letter)
			tile_size = image.get_size()
			width += tile_size.width
		return Size(width, height)
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
	def _render_tile(self, engine, image_name, pos, topleft):
		image = engine.get_image(image_name)
		tile_size = image.get_size()
		image_pos = Point(pos.x * tile_size.width, pos.y * tile_size.height)
		engine.render_texture(image.get_texture(), topleft + image_pos)
	def draw(self, engine, topleft):
		for pos, tile in self.level_map.iter_tiles():
			for image_name in tile.get_images():
				self._render_tile(engine, image_name, pos, topleft)
		for pos, actor in self.level_map.iter_actors():
			self._render_tile(engine, actor.get_sprite(), pos, topleft)

class HighlightableWidget:
	""" Compound widget with two states: normal and highlighted (selected).
	States can be any widgets.
	Also supports custom action callback (usually performed on "selection" event).
	It's up to the parent context to detect selection and perform action.
	"""
	def __init__(self, normal, highlighted, action=None):
		""" Creates highlightable item widget from two states (widgets).
		"""
		self.widget_normal = normal
		self.widget_highlighted = highlighted
		self.action = action
		self.highlighted = False
	def get_size(self, engine):
		""" Returns max size of the two sub-widgets.
		"""
		normal_size = self.widget_normal.get_size(engine)
		highlighted_size = self.widget_highlighted.get_size(engine)
		return Size(
				max(normal_size.width, highlighted_size.width),
				max(normal_size.height, highlighted_size.height),
				)
	def make_highlighted(self, value):
		""" Makes current item highlighted. """
		self.highlighted = bool(value)
	def draw(self, engine, topleft):
		if self.highlighted:
			self.widget_highlighted.draw(engine, topleft)
		else:
			self.widget_normal.draw(engine, topleft)

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
	def __init__(self, font, size, text="", autoheight=False):
		""" Creates widget to display text with Font object.
		Text will fit into given size, auto-wrapped with option to scroll.
		If autoheight=True, widget auto-expands the height to fit the whole text, scrolling is not available.
		Optional initial text can be provided; it can be changed at any moment using set_text().
		"""
		self.font = font
		self.size = Size(size)
		self.autoheight = autoheight
		self.textlines = None
		self.set_text(text)
		self.top_line = 0
	def get_size(self, engine):
		return self.size
	def set_text(self, new_text):
		self.textlines = []
		total_height = 0
		for line in new_text.splitlines():
			line_width = []
			line_height = 0
			current_line = ''
			for letter in line:
				letter_size = self.font.get_letter_image(letter).get_size()
				letter_width = letter_size.width
				line_height = max(line_height, letter_size.height)
				if sum(line_width) + letter_width > self.size.width:
					last_space_pos = current_line.rfind(' ')
					last_space_pos = last_space_pos if last_space_pos > -1 else len(current_line)
					total_height += line_height
					line_height = 0
					self.textlines.append(current_line[:last_space_pos].rstrip())
					current_line = current_line[last_space_pos+1:]
					line_width = line_width[last_space_pos+1:]
				current_line += letter
				line_width.append(letter_width)
			total_height += line_height
			self.textlines.append(current_line)
		if self.autoheight:
			self.size.height = total_height
	def _number_of_lines_that_fit_the_screen(self):
		if self.autoheight:
			return len(self.textlines)
		font_height = self.font.get_letter_image('W').get_size().height
		return self.size.height // font_height
	def get_top_line(self):
		""" Returns current topmost line. """
		return self.top_line
	def set_top_line(self, new_top_line):
		""" Set topmost line to display.
		It should be in range [0; total_lines - number_of_lines_that_fit_the_screen].
		"""
		if self.autoheight: # pragma: no cover -- should not reach here actually.
			return
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
