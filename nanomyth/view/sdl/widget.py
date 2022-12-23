"""
SDL-based engine organize display output as a set of separate widgets.
"""
import pygame
from ...math import Point, Size, Matrix
from ..utils import math
from ..utils.ui import TextWrapper, Scroller

class Widget:
	""" Base interface for widgets.
	"""
	def get_size(self, engine): # pragma: no cover
		""" Should return Size object that covers widgets area.
		Engine is passed for operations that may require it to determine size.
		"""
		raise NotImplementedError()
	def draw(self, engine, topleft): # pragma: no cover
		""" Called by engine to draw widget
		in given topleft position.

		Use engine .render_* functions to draw.
		"""
		raise NotImplementedError()

class ImageWidget(Widget):
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

class TileMapWidget(Widget):
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

class PanelWidget(TileMapWidget):
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
		super().__init__(math.tiled_panel(tilemap, size))

class TextLineWidget(Widget):
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

class LevelMapWidget(Widget):
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

class HighlightableWidget(Widget):
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

class MenuItem(Widget):
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

class SDLTextWrapper(TextWrapper):
	def __init__(self, *args, font=None, **kwargs):
		self.font = font
		super().__init__(*args, **kwargs)
	def get_letter_size(self, letter):
		return self.font.get_letter_image(letter).get_size()

class BaseMultilineTextWidget(Widget):
	""" Base abstract class for multiline text widgets.
	"""
	def __init__(self, font, size, text=""):
		""" Creates widget to display text with Font object.
		Text will auto-wrap to fit into width and may adjust height.
		"""
		self.font = font
		self.size = Size(size)
		self.textlines = None
	def get_size(self, engine):
		return self.size
	def set_text(self, new_text):
		wrapper = SDLTextWrapper(new_text, self.size.width, font=self.font)
		self.textlines = wrapper.lines
		return wrapper
	def get_visible_text_lines(self): # pragma: no cover
		""" Should return set of text lines that fit into the current viewport. """
		raise NotImplementedError()
	def draw(self, engine, topleft):
		font_height = self.font.get_letter_image('W').get_size().height
		for row, textline in enumerate(self.get_visible_text_lines()):
			image_pos = Point(0, row * font_height)
			for pos, letter in enumerate(textline):
				image = self.font.get_letter_image(letter)
				engine.render_texture(image.get_texture(), topleft + image_pos)
				tile_size = image.get_size()
				image_pos.x += tile_size.width

class MultilineTextWidget(BaseMultilineTextWidget):
	""" Displays multiline text using pixel font.
	Widget will auto-adjust height to the whole text.
	"""
	def __init__(self, font, size, text=""):
		""" Creates widget to display text with Font object.
		Text will auto-wrap to fit into width and may adjust height.
		Optional initial text can be provided; it can be changed at any moment using set_text().
		"""
		super().__init__(font, size)
		self.set_text(text)
	def set_text(self, new_text):
		wrapper = super().set_text(new_text)
		self.size.height = wrapper.total_height
	def get_visible_text_lines(self):
		""" Returns set of text lines that fit into the current viewport. """
		return self.textlines

class MultilineScrollableTextWidget(BaseMultilineTextWidget):
	""" Displays multiline text using pixel font
	with option to scroll if text is larger than the screen can fit.

	Scrolling functionality (get/set top line etc) can be accessed
	via field .scroller (see nanomyth.view.utils.Scroller).
	"""
	def __init__(self, font, size, text=""):
		""" Creates widget to display text with Font object.
		Text will fit into given size, auto-wrapped with option to scroll.
		Optional initial text can be provided; it can be changed at any moment using set_text().
		"""
		super().__init__(font, size)
		self.scroller = Scroller(
				total_items=1,
				viewport_height=self.size.height,
				item_height=self.font.get_letter_image('W').get_size().height,
				)
		self.set_text(text)
	def set_text(self, new_text):
		wrapper = super().set_text(new_text)
		self.scroller.set_total_items(len(self.textlines))
	def get_top_line(self):
		""" Returns current topmost line. """
		return self.scroller.get_top_item()
	def set_top_line(self, new_top_line):
		""" Set topmost line to display.
		It should be in range [0; total_lines - number_of_lines_that_fit_the_screen].
		"""
		self.scroller.set_top_item(new_top_line)
	def can_scroll_up(self):
		""" Returns True if there are line higher than current viewport can display
		and it can be scrolled up.
		"""
		return self.scroller.can_scroll_up()
	def can_scroll_down(self):
		""" Returns True if there are line lower than current viewport can display
		and it can be scrolled down.
		"""
		return self.scroller.can_scroll_down()
	def get_visible_text_lines(self):
		""" Returns set of text lines that fit into the current viewport. """
		return self.textlines[self.scroller.get_visible_slice()]
