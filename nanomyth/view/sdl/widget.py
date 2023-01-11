"""
SDL-based engine organize display output as a set of separate widgets.
"""
import pygame
from ...utils.meta import Delegate
from ...math import Point, Size, Rect, Matrix
from ..utils import math
from ..utils.ui import TextWrapper, Scroller, SelectionList
from ...utils.meta import typed
from ._base import Engine
from ...game.map import Map

class WidgetAtPos:
	def __init__(self, topleft, widget):
		self.topleft = Point(topleft)
		self.widget = widget

class Widget:
	""" Base interface for widgets.
	"""
	def get_size(self, engine): # pragma: no cover
		""" Should return Size object that covers widgets area.
		Engine is passed for operations that may require it to determine size.
		"""
		raise NotImplementedError(str(type(self)))
	def draw(self, engine, topleft): # pragma: no cover
		""" Called by engine to draw widget
		in given topleft position.

		Use engine .render_* functions to draw.
		"""
		raise NotImplementedError(str(type(self)))

class Image(Widget):
	""" Displays full image.
	"""
	def __init__(self, image):
		""" Creates widget to display image.
		"""
		self._image = image
	@typed(Engine)
	def get_size(self, engine):
		return self._image.get_size()
	@typed(Engine, Point)
	def draw(self, engine, topleft):
		image = self._image
		if isinstance(self._image, str):
			image = engine.get_image(self._image)
		engine.render_texture(image.get_texture(), topleft)

class AbstractGrid(Widget):
	""" Base class for widgets that display a grid of image tiles.

	Does not support scrolling in any direction.
	"""
	def get_grid_size(self, engine): # pragma: no cover
		""" Should return maximum Size of grid. """
		raise NotImplementedError(str(type(self)))
	def iter_tiles(self, engine): # pragma: no cover
		""" Should yield pairs (Point, Image).
		First item is a position within grid.
		Real coordinates will be calculated automatically.
		"""
		raise NotImplementedError(str(type(self)))
	@typed(Engine)
	def get_size(self, engine):
		""" Returns bounding pixel size of the grid.
		Determines size of a single tile by picking first item from iter_tiles().
		"""
		_, image = next(self.iter_tiles(engine))
		tile_size = image.get_size()
		grid_size = self.get_grid_size(engine)
		return Size(
				grid_size.width * tile_size.width,
				grid_size.height * tile_size.height,
				)
	@typed(Engine, Point)
	def draw(self, engine, topleft):
		for pos, image in self.iter_tiles(engine):
			tile_size = image.get_size()
			image_pos = Point(pos.x * tile_size.width, pos.y * tile_size.height)
			engine.render_texture(image.get_texture(), topleft + image_pos)

class TileMap(AbstractGrid):
	""" Displays a Map of arbitrary tiles
	"""
	def __init__(self, tilemap):
		""" Creates widget to display given Matrix of tiles.
		Tiles are either Images or image names in engine's image list.
		"""
		self._tilemap = tilemap
	@typed(Engine)
	def get_grid_size(self, engine):
		return self._tilemap.size
	@typed(Engine)
	def iter_tiles(self, engine):
		for pos in self._tilemap:
			yield pos, engine.get_image(self._tilemap.cell(pos))

class Panel(TileMap):
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

class ImageRowSet(Widget):
	""" Displays a vertical set of horizontal left-aligned sequences of images. """
	def _iter_image_rows(self): # pragma: no cover
		""" Should yield image rows from top to bottom.
		Each image row should yield Image objects from left to right.
		"""
		raise NotImplementedError(str(type(self)))
	def _empty_line_height(self): # pragma: no cover
		""" Should return default height for lines with no elements. """
		raise NotImplementedError(str(type(self)))
	def __iter_row_items(self, row):
		for image in row:
			yield image, image.get_size()
	@typed(Engine)
	def get_size(self, engine):
		""" Returns total bounding size of the row set. """
		result = Size(0, 0)
		for image, image_rect in self.__iter_items():
			result.width = max(result.width, image_rect.right)
			result.height = max(result.height, image_rect.bottom)
		return result
	@typed(Engine, Point)
	def draw(self, engine, topleft):
		for image, image_rect in self.__iter_items():
			engine.render_texture(image.get_texture(), topleft + image_rect.topleft)
	def __iter_items(self):
		image_pos = Point()
		for row in self._iter_image_rows():
			row_height = 0
			for image, tile_size in self.__iter_row_items(row):
				yield image, Rect(image_pos, tile_size)
				image_pos.x += tile_size.width
				row_height = max(row_height, tile_size.height)
			image_pos.x = 0
			image_pos.y += row_height or self._empty_line_height()

class TextLine(ImageRowSet):
	""" Displays single-line text using pixel font. """
	def __init__(self, font, text=""):
		""" Creates widget to display single text line with Font object.
		Optional initial text can be provided; it can be changed at any moment using set_text().
		"""
		self._font = font
		self._text = text
	def _empty_line_height(self):
		return self._font.get_letter_image(' ').get_size().height
	def _iter_image_rows(self):
		yield (self._font.get_letter_image(letter) for letter in self._text)
	@typed(str)
	def set_text(self, new_text):
		self._text = new_text

class LevelMap(AbstractGrid):
	""" Displays level map using static camera (viewport is not moving).

	WARNING: As camera is static, map should fit within the screen,
	outside tiles are accessible but will not be displayed!
	"""
	def __init__(self, level_map):
		""" Creates widget to display given Map (of Tile objects).
		"""
		self._level_map = level_map
	@typed(Map)
	def set_map(self, new_level_map):
		""" Switches displayed level map. """
		self._level_map = new_level_map
	@typed(Engine)
	def get_grid_size(self, engine):
		return self._level_map.get_size()
	@typed(Engine)
	def iter_tiles(self, engine):
		for pos, tile in self._level_map.iter_tiles():
			for image_name in tile.get_images():
				yield pos, engine.get_image(image_name)
		for pos, item in self._level_map.iter_items():
			yield pos, engine.get_image(item.get_sprite())
		for pos, actor in self._level_map.iter_actors():
			yield pos, engine.get_image(actor.get_sprite())

class Compound(Widget):
	""" Compound container widget that may display several sub-widgets at the same time. """
	def __init__(self):
		""" Creates empty container.
		Fill it with add_widget().
		"""
		self._widgets = []
	@typed(Widget, topleft=(Point, tuple, list))
	def add_widget(self, widget, topleft=None):
		""" Adds new widget.
		If topleft is specified, it is treated as relative shift from the topleft corner of the container itself.
		If any dimension of position is negative, it is counting back from the other side (bottom/right) instead,
		considering _full_ size of the compound widget.
		Widgets will be displayed in the order of adding,
		i.e. to make some widget background add it as the very first one.
		"""
		self._widgets.append(WidgetAtPos(Point(topleft or (0, 0)), widget))
	@typed(Engine)
	def get_size(self, engine):
		""" Size of the bounding area for all widgets. """
		result = Size(0, 0)
		for item in self._widgets:
			if item.topleft.x < 0 or item.topleft.y < 0: # pragma: no cover -- TODO cannot correctly auto-adjust size with negative placements yet.
				continue
			widget_size = item.widget.get_size(engine) + item.topleft
			result.width = max(result.width, widget_size.width)
			result.height = max(result.height, widget_size.height)
		return result
	@typed(Engine, Point)
	def draw(self, engine, topleft):
		full_size = self.get_size(engine)
		for item in self._widgets:
			pos = item.topleft
			if pos.x < 0 or pos.y < 0:
				if pos.x < 0:
					pos.x = full_size.width + pos.x
				if pos.y < 0:
					pos.y = full_size.height + pos.y
			item.widget.draw(engine, topleft + pos)

class Switch(Widget):
	""" Compound widget that display different sub-widgets depending on controllable inner state.
	"""
	def __init__(self):
		""" Creates empty widget.
		Fill it with states using add_widget()
		"""
		self._states = {}
		self._current = None
	@typed(any, Widget)
	def add_widget(self, state, widget):
		""" Adds new state with widget. """
		self._states[state] = widget
	def set_state(self, state):
		""" Sets current state. """
		self._current = state
	@typed(Engine)
	def get_size(self, engine):
		""" Returns max size of sub-widgets.
		"""
		widget_sizes = [_.get_size(engine) for _ in self._states.values()]
		return Size(
				max(_.width for _ in widget_sizes),
				max(_.height for _ in widget_sizes),
				)
	@typed(Engine, Point)
	def draw(self, engine, topleft):
		current_widget = self._states[self._current]
		current_widget.draw(engine, topleft)

class Button(Switch):
	""" Switch widget with two states: normal and highlighted (selected).
	States can be any widgets.
	Also supports optional custom action callback (usually to be performed on "selection" event).
	It's up to the parent context to detect selection and perform action.
	"""
	def __init__(self, normal, highlighted, action=None):
		""" Creates button widget with two states (widgets).
		"""
		super().__init__()
		self.add_widget(False, normal)
		self.add_widget(True, highlighted)
		self.set_state(False)
		self._action = action
	def get_action(self):
		""" Returns attached action callback. """
		return self._action
	def make_highlighted(self, value):
		""" Makes current item highlighted. """
		self.set_state(bool(value))

class ButtonGroup(Widget):
	""" Vertical button group. """
	add_button = Delegate('_buttons', SelectionList.append)
	select = Delegate('_buttons', SelectionList.select)
	select_prev = Delegate('_buttons', SelectionList.select_prev)
	select_next = Delegate('_buttons', SelectionList.select_next)

	def __init__(self):
		self._buttons = SelectionList(on_selection=lambda item, value: item.make_highlighted(value))
		self._spacing = 0
	@typed(int)
	def set_spacing(self, height):
		""" Sets padding space between menu buttons.
		Default is 0.
		"""
		self._spacing = height
	def get_selected_action(self):
		""" Returns action property of the selected button,
		or None if nothing is selected.
		"""
		return self._buttons.get_selected_item().get_action() if self._buttons.has_selection() else None
	@typed(Engine)
	def get_size(self, engine):
		""" Returns total bounding size of the button group. """
		result = Size(0, self._spacing * (len(self._buttons) - 1))
		for button in self._buttons:
			button_size = button.get_size(engine)
			result.width = max(result.width, button_size.width)
			result.height += button_size.height
		return result
	@typed(Engine, Point)
	def draw(self, engine, topleft):
		button_pos = Point(0, 0)
		for button in self._buttons:
			button.draw(engine, topleft + button_pos)
			button_size = button.get_size(engine)
			button_pos.y += button_size.height + self._spacing

class SDLTextWrapper(TextWrapper):
	def __init__(self, *args, font=None, **kwargs):
		self._font = font
		super().__init__(*args, **kwargs)
	@typed(str)
	def get_letter_size(self, letter):
		return self._font.get_letter_image(letter).get_size()

class BaseMultilineText(ImageRowSet):
	""" Base abstract class for multiline text widgets.
	"""
	def __init__(self, font, size, text=""):
		""" Creates widget to display text with Font object.
		Text will auto-wrap to fit into width and may adjust height.
		"""
		self._font = font
		self._size = Size(size)
		self._textlines = None
	@typed(str)
	def set_text(self, new_text):
		wrapper = SDLTextWrapper(new_text, self._size.width, font=self._font)
		self._textlines = wrapper.lines
		return wrapper
	def get_visible_text_lines(self): # pragma: no cover
		""" Should return set of text lines that fit into the current viewport. """
		raise NotImplementedError(str(type(self)))
	def _iter_image_rows(self):
		for textline in self.get_visible_text_lines():
			yield (self._font.get_letter_image(letter) for letter in textline)
	def _empty_line_height(self):
		return self._font.get_letter_image(' ').get_size().height

class MultilineText(BaseMultilineText):
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
	@typed(str)
	def set_text(self, new_text):
		wrapper = super().set_text(new_text)
		self._size.height = wrapper.total_height
	def get_visible_text_lines(self):
		""" Returns set of text lines that fit into the current viewport. """
		return self._textlines

class MultilineScrollableText(BaseMultilineText):
	""" Displays multiline text using pixel font
	with option to scroll if text is larger than the screen can fit.

	Scrolling functionality (get/set top line etc) can be accessed
	via field .scroller (see nanomyth.view.utils.Scroller).
	"""
	get_top_line = Delegate('_scroller', Scroller.get_top_item)
	set_top_line = Delegate('_scroller', Scroller.set_top_item)
	can_scroll_up = Delegate('_scroller', Scroller.can_scroll_up)
	can_scroll_down = Delegate('_scroller', Scroller.can_scroll_down)

	def __init__(self, font, size, text=""):
		""" Creates widget to display text with Font object.
		Text will fit into given size, auto-wrapped with option to scroll.
		Optional initial text can be provided; it can be changed at any moment using set_text().
		"""
		super().__init__(font, size)
		self._scroller = Scroller(
				total_items=1,
				viewport_height=self._size.height,
				item_height=self._font.get_letter_image('W').get_size().height,
				)
		self.set_text(text)
	@typed(str)
	def set_text(self, new_text):
		wrapper = super().set_text(new_text)
		self._scroller.set_total_items(len(self._textlines))
	def get_visible_text_lines(self):
		""" Returns set of text lines that fit into the current viewport. """
		return self._textlines[self._scroller.get_visible_slice()]
