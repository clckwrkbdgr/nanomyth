"""
Game is a set of different contexts (main menu, map, inventory screen etc),
which are organized in a stack and can be switched back and forth.
Main context operations are performed by the SDLEngine itself.
"""
import pygame
from .widget import WidgetAtPos, LevelMap, TextLine, Image, Button, MultilineText, MultilineScrollableText, ButtonGroup, Compound
from ...utils.meta import Delegate
from ..utils.ui import Scroller, SelectionList
from ...game.actor import Direction
from ...game import game
from ...math import Point, Size, Rect
from ...utils.meta import typed, fieldproperty
from ._base import Engine
from .widget import Widget, Button
from .font import Font
from .image import BaseImage

class Context:
	""" Basic game context.
	Context handles some arbitrary game entities
	and defines how they are drawn (via corresponding Widget objects in method draw())
	and how they are react to the control events (pressed keys etc, method update()).
	"""
	class Finished(Exception):
		""" Raise this when context is finished. """
		pass

	transparent = fieldproperty('_transparent', 'True if context if transparent and underlying contexts may be visible.')

	def __init__(self, transparent=False):
		""" Creates empty context.
		Widgets can be added later via add_widget.

		Setting transparent = True makes it draw underlying context (if any).
		Useful for context that does not cover the whole screen, like message boxes.
		"""
		self._transparent = transparent
		self._widgets = []
		self._key_bindings = {}
		self._pending_context = None
	def set_pending_context(self, new_context): # TODO cannot be typed because it's its own class, maybe shouldn't do this here?
		""" Sets pending context.
		It will be swtiched immediately after controls are back to this context.
		See SDLEngine.run() for details.
		"""
		self._pending_context = new_context
	@typed((Point, tuple, list), Widget)
	def add_widget(self, topleft, widget):
		""" Adds new widget. """
		self._widgets.append(WidgetAtPos(topleft, widget))
	def bind_key(self, key_name, action): # TODO callable typing
		""" Registers custom handler for key name.
		Actions should be a function with no arguments
		that returns new context or None, or raises an Exception.
		"""
		self._key_bindings[key_name] = action
	@typed(str)
	def update(self, control_name): # pragma: no cover
		""" Processes control events.
		`control_name` is the name of a pressed key.

		Default implementation does nothing except processing custom key bindings.
		Custom implementations should call this basic implementation if they allow custom key bindings.
		"""
		if control_name in self._key_bindings:
			return self._key_bindings[control_name]()
	def perform_action(self, action): # TODO callable typing.
		""" Programmatically perform action.
		Action should be an action-like object (see Menu docstring).
		"""
		import types
		if isinstance(action, Exception) or action is Exception or (isinstance(action, type) and issubclass(action, Exception)):
			raise action()
		elif callable(action):
			return action()
		return action # Treat as a new context.
	def _get_widgets_to_draw(self, engine):
		""" Override this function to change widgets to draw.
		Widgets are drawn in the given order, from bottom to top.
		"""
		return self._widgets
	@typed(Engine)
	def draw(self, engine):
		""" Draws all widgets. """
		for _ in self._get_widgets_to_draw(engine):
			_.obj.draw(engine, _.pos)

class Game(Context):
	""" Context for the main game screen: level map, player character etc.
	Controls player character via keyboard.

	Any other widgets (e.g. UI) can be added via usual .add_widget()
	"""
	@typed(game.Game)
	def __init__(self, game):
		""" Creates visual context for the game object.
		"""
		super().__init__()
		self._game = game
		self._game.on_change_map(self._update_map_widget)
		self._map_widget = LevelMap(self._game.get_world().get_current_map())
		self.add_widget((0, 0), self._map_widget)
	def _update_map_widget(self, current_map):
		self._map_widget.set_map(current_map)
	def get_game(self):
		""" Returns game object. """
		return self._game
	@typed(str)
	def update(self, control_name):
		""" Controls player character: <Up>, <Down>, <Left>, <Right>
		<ESC>: Exit to the previous context.
		"""
		if control_name == 'escape':
			raise self.Finished()
		elif control_name == 'up':
			self._game.shift_player(Direction.UP)
		elif control_name == 'down':
			self._game.shift_player(Direction.DOWN)
		elif control_name == 'left':
			self._game.shift_player(Direction.LEFT)
		elif control_name == 'right':
			self._game.shift_player(Direction.RIGHT)
		return super().update(control_name)

class Menu(Context):
	""" Game context for menu screens.

	Operates on set of Button widgets with option to pick one and perform its action.
	Available action options:
	- Exception object or type, e.g. Context.Finished - to close current context and go back.
	- Context object - to switch to the new context.
	- Callable - should take no argument and return action-like object.
	- Default is None - no action should be taken.

	As this class is a Context, any other widgets (e.g. background image or title text) can be added via usual .add_widget()
	"""
	set_button_spacing = Delegate('_items', ButtonGroup.set_spacing)
	add_menu_item = Delegate('_items', ButtonGroup.add_button)
	select_item = Delegate('_items', ButtonGroup.select)

	def __init__(self, on_escape=None): # TODO typed action callable.
		""" Creates menu context.
		Items can be added later via .add_menu_item().

		If on_escape is specified, it should be an action-like object (see Menu docstring)
		and it will performed when <ESC> is pressed.
		Default value is raise Context.Finished
		"""
		super().__init__()
		self._items = ButtonGroup()
		self._background = None
		self._caption = None
		self._on_escape = on_escape or self.Finished
		self._button_group_topleft = Point(0, 0)
	def _get_widgets_to_draw(self, engine):
		widgets = []
		if self._background:
			widgets.append(WidgetAtPos((0, 0), self._background))
		widgets.append(WidgetAtPos(self._button_group_topleft, self._items))
		if self._caption:
			widgets.append(self._caption)
		widgets.extend(self._widgets)
		return widgets
	@typed((Point, tuple, list), Widget)
	def set_caption(self, pos, caption_widget):
		""" Adds caption widget. """
		self._caption = WidgetAtPos(Point(pos), caption_widget)
	@typed((BaseImage, str))
	def set_background(self, image):
		""" Set background image.
		Can be either some Image widget, or name of the image in global image list -
		in this case image is locked to the topleft corner to fill the screen.
		"""
		if isinstance(image, str):
			image = Image(image)
		self._background = image
	@typed((Point, tuple, list))
	def set_button_group_topleft(self, pos):
		""" Sets topleft position of menu buttons group.
		Default is (0, 0)
		"""
		self._button_group_topleft = Point(pos)
	@typed(str)
	def update(self, control_name):
		""" Controls:
		- <Up>: select previous item.
		- <Down>: select next item.
		- <Enter>: pick currently selected item.
		- <ESC>: optional "escape" action, if specified (see on_escape).
		"""
		if control_name == 'escape':
			if self._on_escape:
				return self.perform_action(self._on_escape)
		elif control_name == 'up':
			self._items.select_prev()
		elif control_name == 'down':
			self._items.select_next()
		elif control_name == 'return':
			selected_action = self._items.get_selected_action()
			if selected_action:
				return self.perform_action(selected_action)
		return super().update(control_name)

class MessageBox(Context):
	""" Displays message and requires answer or confirmation.
	"""
	add_button = Delegate('_panel', Compound.add_widget)

	@typed(str, Font, Widget, Engine, text_shift=(Point, tuple, list, None))
	def __init__(self, text, font, panel_widget, engine, text_shift=None, on_ok=None, on_cancel=None): # TODO typed actions callables
		""" Creates message box with given text and font (required).
		Panel widget will be draw under the text
		and will be aligned to the center of the screen.
		Text will start from the topleft corner of the panel
		plus optional text_shift.

		Optional on_ok and on_cancel events can be passed.
		Both should be callable with no arguments.
		They will be called upon corresponding user reaction.
		"""
		super().__init__(transparent=True)
		self._on_ok = on_ok
		self._on_cancel = on_cancel

		self._panel = Compound()
		self._panel.add_widget(panel_widget)

		_panel_size = panel_widget.get_size(engine)
		window_size = engine.get_window_size()
		_panel_topleft = Point(
				(window_size.width - _panel_size.width) // 2,
				(window_size.height - _panel_size.height) // 2,
				)
		self.add_widget(_panel_topleft, self._panel)

		self._panel.add_widget(panel_widget)
		self._panel.add_widget(TextLine(font, text), (text_shift or Point(0, 0)))
	@typed(str)
	def update(self, control_name):
		""" Controls:
		- <Enter>, <Space>: OK
		- <Escape>: Cancel
		"""
		if control_name == 'escape':
			if self._on_cancel:
				self._on_cancel()
			raise self.Finished()
		elif control_name in ['space', 'return']:
			if self._on_ok:
				self._on_ok()
			raise self.Finished()
		return super().update(control_name)

class ScrollableContext(Context):
	""" Base class for context that allow scrolling.
	Supports two buttons: scrolling up and down.
	Derived classes should support:
	- methods can_scroll_up() and can_scroll_down()
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._button_up = None
		self._button_down = None
	def _get_panel_widget(self): # pragma: no cover
		""" Should return the main panel widget
		where scroll buttons will be added.
		"""
		raise NotImplementedError()
	@typed((Point, tuple, list), Button)
	def set_scroll_up_button(self, pos, button_widget):
		""" Adds button for scrolling up.
		It should be of Button class so it can be highlighted when scrolling up is available
		and display as normal (inactive) when it's not.
		Position is relative to the view rect topleft corner.
		If any dimension of position is negative, it is counting back from the other side (bottom/right).
		"""
		self._button_up = button_widget
		self._button_up.make_highlighted(self.can_scroll_up())
		self._get_panel_widget().add_widget(button_widget, pos)
	@typed((Point, tuple, list), Button)
	def set_scroll_down_button(self, pos, button_widget):
		""" Adds button for scrolling down.
		It should be of Button class so it can be highlighted when scrolling down is available
		and display as normal (inactive) when it's not.
		Position is relative to the view rect topleft corner.
		If any dimension of position is negative, it is counting back from the other side (bottom/right).
		"""
		self._button_down = button_widget
		self._button_down.make_highlighted(self.can_scroll_down())
		self._get_panel_widget().add_widget(button_widget, pos)
	def _update_scroll_buttons(self):
		if self._button_up:
			self._button_up.make_highlighted(self.can_scroll_up())
		if self._button_down:
			self._button_down.make_highlighted(self.can_scroll_down())
	@typed(str)
	def update(self, control_name):
		""" Updates highlighted status for scroll buttons. """
		self._update_scroll_buttons()
		return super().update(control_name)

class TextScreen(ScrollableContext):
	""" Displays multiline (scrollablle) text screen.
	"""
	can_scroll_up = Delegate('_text_widget', MultilineScrollableText.can_scroll_up)
	can_scroll_down = Delegate('_text_widget', MultilineScrollableText.can_scroll_down)
	add_button = Delegate('_panel', Compound.add_widget)

	@typed(str, Font, Widget, Engine, text_rect=(Rect, tuple, list, None))
	def __init__(self, text, font, panel_widget, engine, text_rect=None):
		""" Creates text screen with given text and font (required).
		Panel widget will be draw under the text and should fit the whole screen.
		Text will fit into given text_rect with automatic wrapping and automatic scrolling.
		"""
		super().__init__(transparent=False)
		self._panel = Compound()
		self._panel.add_widget(panel_widget)
		self.add_widget((0, 0), self._panel)

		window_size = engine.get_window_size()
		self._text_rect = Rect(text_rect or (0, 0, window_size.width, window_size.height))
		self._text_widget = MultilineScrollableText(font, self._text_rect.size, text)
		self._panel.add_widget(self._text_widget, self._text_rect.topleft)
	def _get_panel_widget(self):
		return self._panel
	@typed(str)
	def update(self, control_name):
		""" Controls:
		- <Enter>, <Space>, <Escape>: close dialog.
		- <Up>: scroll text up.
		- <Down>: scroll text down.
		"""
		if control_name in ['escape', 'space', 'return']:
			raise self.Finished()
		if control_name == 'up':
			self._text_widget.set_top_line(self._text_widget.get_top_line() - 1)
		elif control_name == 'down':
			self._text_widget.set_top_line(self._text_widget.get_top_line() + 1)
		return super().update(control_name)

class ItemList(ScrollableContext):
	""" Displays list of items with option to scroll up/down.
	Each item is a standalone widget of any type.
	"""
	can_scroll_up = Delegate('_scroller', Scroller.can_scroll_up)
	can_scroll_down = Delegate('_scroller', Scroller.can_scroll_down)
	add_button = Delegate('_panel', Compound.add_widget)

	@typed(Engine, Widget, list, caption_widget=(Widget, None), view_rect=(Rect, tuple, list, None))
	def __init__(self, engine, background_widget, items, caption_widget=None, view_rect=None):
		""" Creates item list screen.
		Requires background widget (of any type) and list of items.
		Each item is a standalone widget of any type.
		Can be navigated, items can be selected and action can be performed on selected item.
		Items will fit into given optional view_rect (defaults to the whole screen).
		If total item set is larger than the given view_rect, list becomes scrollable.
		Scroll buttons can be added manually using set_scroll_up_button()/set_scroll_down_button().

		Optional caption widget will be placed at the top of the list (always shown).
		"""
		super().__init__(transparent=False)
		self._panel = Compound()
		self._panel.add_widget(background_widget)

		window_size = engine.get_window_size()
		self._view_rect = Rect(view_rect or (0, 0, window_size.width, window_size.height))
		self._caption_widget = caption_widget
		self._caption_height = self._caption_widget.get_size(engine).height if self._caption_widget else 0

		self._items = SelectionList(items, on_selection=lambda item, value: item.make_highlighted(value))
		self._items.select(self._items.get_next_selected_index())
		self._item_heights = [item.get_size(engine).height for item in self._items]

		self._scroller = Scroller(
				total_items=len(self._items),
				viewport_height=self._view_rect.height,
				item_height=lambda i: self._item_heights[i],
				)

		self.add_widget((0, 0), self._panel)
	def _get_panel_widget(self):
		return self._panel
	@typed(int)
	def select_item(self, selected_index):
		""" Selects item by index.
		Highlights corresponding widget.
		"""
		self._items.select(selected_index)
		self._scroller.ensure_item_visible(selected_index)
	def _get_widgets_to_draw(self, engine):
		widgets = []
		widgets.extend(self._widgets)

		top_pos = self._view_rect.top
		if self._caption_widget:
			widgets.append(WidgetAtPos((
				self._view_rect.left,
				top_pos,
				), self._caption_widget))
			top_pos += self._caption_height
		for item_index in self._scroller.get_visible_range():
			widgets.append(WidgetAtPos((
				self._view_rect.left,
				top_pos,
				), self._items[item_index]))
			top_pos += self._item_heights[item_index]
		return widgets
	@typed(str)
	def update(self, control_name):
		""" Controls:
		- <Escape>: close dialog.
		- <Up>: select previous item.
		- <Down>: select next item.
		- <Enter>: pick currently selected item.
		"""
		if control_name in ['escape']:
			raise self.Finished()
		elif control_name == 'up':
			self.select_item(self._items.get_prev_selected_index())
		elif control_name == 'down':
			self.select_item(self._items.get_next_selected_index())
		elif control_name == 'return':
			if self._items.has_selection():
				action = self._items.get_selected_item().get_action()
				return self.perform_action(action)
		return super().update(control_name)
