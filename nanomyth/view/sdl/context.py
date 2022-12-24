"""
Game is a set of different contexts (main menu, map, inventory screen etc),
which are organized in a stack and can be switched back and forth.
Main context operations are performed by the SDLEngine itself.
"""
import pygame
from .widget import WidgetAtPos, LevelMapWidget, TextLineWidget, ImageWidget, Layout, Button, MultilineTextWidget, MultilineScrollableTextWidget
from ..utils.ui import Scroller, SelectionList
from ...game.actor import Direction
from ...math import Point, Size, Rect

class Context:
	""" Basic game context.
	Context handles some arbitrary game entities
	and defines how they are drawn (via corresponding Widget objects in method draw())
	and how they are react to the control events (pressed keys etc, method update()).
	"""
	class Finished(Exception):
		""" Raise this when context is finished. """
		pass

	def __init__(self, transparent=False):
		""" Creates empty context.
		Widgets can be added later via add_widget.

		Setting transparent = True makes it draw underlying context (if any).
		Useful for context that does not cover the whole screen, like message boxes.
		"""
		self.transparent = transparent
		self.widgets = []
		self.key_bindings = {}
		self.pending_context = None
	def set_pending_context(self, new_context):
		""" Sets pending context.
		It will be swtiched immediately after controls are back to this context.
		See SDLEngine.run() for details.
		"""
		self.pending_context = new_context
	def add_widget(self, topleft, widget):
		""" Adds new widget. """
		self.widgets.append(WidgetAtPos(topleft, widget))
	def bind_key(self, key_name, action):
		""" Registers custom handler for key name.
		Actions should be a function with no arguments
		that returns new context or None, or raises an Exception.
		"""
		self.key_bindings[key_name] = action
	def update(self, control_name): # pragma: no cover
		""" Processes control events.
		`control_name` is the name of a pressed key.

		Default implementation does nothing except processing custom key bindings.
		Custom implementations should call this basic implementation if they allow custom key bindings.
		"""
		if control_name in self.key_bindings:
			return self.key_bindings[control_name]()
	def _get_widgets_to_draw(self, engine):
		""" Override this function to change widgets to draw.
		Widgets are drawn in the given order, from bottom to top.
		"""
		return self.widgets
	def draw(self, engine):
		""" Draws all widgets. """
		for _ in self._get_widgets_to_draw(engine):
			_.widget.draw(engine, _.topleft)

class Game(Context):
	""" Context for the main game screen: level map, player character etc.
	Controls player character via keyboard.

	Any other widgets (e.g. UI) can be added via usual .add_widget()
	"""
	def __init__(self, game):
		""" Creates visual context for the game object.
		"""
		super().__init__()
		self.map_widget = LevelMapWidget(None)
		self.add_widget((0, 0), self.map_widget)
		self.game = game
		self.game.on_change_map(self._update_map_widget)
		self._update_map_widget(self.game.get_world().get_current_map())
	def _update_map_widget(self, current_map):
		self.map_widget.set_map(current_map)
	def get_game(self):
		""" Returns game object. """
		return self.game
	def update(self, control_name):
		""" Controls player character: <Up>, <Down>, <Left>, <Right>
		<ESC>: Exit to the previous context.
		"""
		if control_name == 'escape':
			raise self.Finished()
		elif control_name == 'up':
			self.game.shift_player(Direction.UP)
		elif control_name == 'down':
			self.game.shift_player(Direction.DOWN)
		elif control_name == 'left':
			self.game.shift_player(Direction.LEFT)
		elif control_name == 'right':
			self.game.shift_player(Direction.RIGHT)
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
	def __init__(self, font, on_escape=None):
		""" Creates menu context.
		Items can be added later via .add_menu_item().

		If on_escape is specified, it should be an action-like object (see Menu docstring)
		and it will performed when <ESC> is pressed.
		"""
		super().__init__()
		self.items = []
		self.background = None
		self.caption = WidgetAtPos((0, 0), TextLineWidget(font))
		self.selected = None
		self.on_escape = on_escape
		self._button_group_topleft = Point(0, 0)
		self._button_height = 8
		self._button_caption_shift = Point(0, 0)
		self._button_template = None
		self._button_template_highlighted = None
		self._button_caption_font = font
		self._button_caption_font_highlighted = font
	def _get_widgets_to_draw(self, engine):
		widgets = []
		if self.background:
			widgets.append(WidgetAtPos((0, 0), self.background))
		widgets.extend(widget for widget, _ in self.items)
		widgets.append(self.caption)
		widgets.extend(self.widgets)
		return widgets
	def add_menu_item(self, new_menu_item, on_selection=None):
		""" Adds new menu item with optional action on selection.

		Item should be either Button object, or string, or tuple of two strings.
		In case of strings, they are treated as button caption (with optional normal/highlighted configuration)
		and are created using templated method (see set_button_* functions).
		WARNING: At least set_button_widget_template() is required for templated items.

		If action is specified, it should be an action-like object (see Menu docstring).
		"""
		button_pos = self._button_group_topleft + Point(0, self._button_height) * len(self.items)
		if isinstance(new_menu_item, Button):
			self.items.append((WidgetAtPos(button_pos, new_menu_item), on_selection))
			return
		caption, caption_highlighted = '', None
		if isinstance(new_menu_item, str):
			caption = new_menu_item
		else:
			caption, caption_highlighted = new_menu_item
		button = self._button_template[0](*(self._button_template[1]))
		button_highlighted = None
		if self._button_template_highlighted:
			button_highlighted = self._button_template_highlighted[0](*(self._button_template_highlighted[1]))

		normal = Layout()
		normal.add_widget(button)
		normal.add_widget(TextLineWidget(
					self._button_caption_font, caption,
					), self._button_caption_shift)
		highlighted = Layout()
		highlighted.add_widget(button_highlighted)
		highlighted.add_widget(TextLineWidget(
				self._button_caption_font_highlighted if caption_highlighted else self._button_caption_font,
				caption_highlighted if caption_highlighted else caption,
				), self._button_caption_shift)

		self.items.append((WidgetAtPos(button_pos, Button(normal, highlighted)), on_selection))
	def set_caption_pos(self, pos):
		""" Moves caption.
		Default position is topleft corner of the screen.
		"""
		self.caption.topleft = Point(pos)
	def set_caption_text(self, text, font=None):
		""" Changes caption text.
		Default value is empty string (no caption).
		Optionally changes caption's font.
		"""
		self.caption.widget.set_text(text)
		if font:
			self.caption.widget.font = font
	def set_background(self, image):
		""" Set background image.
		Can be either some ImageWidget, or name of the image in global image list -
		in this case image is locked to the topleft corner to fill the screen.
		"""
		if isinstance(image, str):
			image = ImageWidget(image)
		self.background = image
	def set_button_group_topleft(self, pos):
		""" Sets topleft position of menu buttons group.
		Default is (0, 0)
		"""
		self._button_group_topleft = Point(pos)
	def set_button_height(self, height):
		""" Sets height of a menu button (including padding space to the next button).
		Default is 8.
		"""
		self._button_height = height
	def set_button_caption_shift(self, shift):
		""" Sets shift for menu button's caption relative to the topleft position of a button.
		Default is (0, 0).
		"""
		self._button_caption_shift = Point(shift)
	def set_button_widget_template(self, widget_type, *params, font=None):
		""" Sets template for menu button widget.
		It will be placed automatically (using params set by set_button_group_topleft()/set_button_height().
		Params should not include topleft position (the last param), it will be calculated automatically anyway.
		Required when using templated menu items.
		If font is specified, it is used for button captions instead of default menu font.
		"""
		self._button_template = (widget_type, params)
		if font:
			self._button_caption_font = font
	def set_highlighted_button_widget_template(self, widget_type, *params, font=None):
		""" Sets template for highlighted menu button widget.
		It will be placed automatically (using params set by set_button_group_topleft()/set_button_height().
		Params should not include topleft position (the last param), it will be calculated automatically anyway.
		By default uses normal widget button template.
		If font is specified, it is used for highlighted button captions instead of default menu font.
		"""
		self._button_template_highlighted = (widget_type, params)
		if font:
			self._button_caption_font_highlighted = font
	def select_item(self, selected_index):
		""" Selects item by index.
		Highlights corresponding widget.
		"""
		self.selected = selected_index
		for index, item in enumerate(self.items):
			item[0].widget.make_highlighted(index == selected_index)
	def perform_action(self, action):
		""" Programmatically perform action.
		Action should be an action-like object (see Menu docstring).
		"""
		import types
		if isinstance(action, Exception) or action is Exception or (isinstance(action, type) and issubclass(action, Exception)):
			raise action()
		elif callable(action):
			return action()
		return action # Treat as a new context.
	def update(self, control_name):
		""" Controls:
		- <Up>: select previous item.
		- <Down>: select next item.
		- <Enter>: pick currently selected item.
		- <ESC>: optional "escape" action, if specified (see on_escape).
		"""
		if control_name == 'escape':
			if self.on_escape:
				return self.perform_action(self.on_escape)
		elif control_name == 'up':
			self.select_item(max(0, self.selected - 1))
		elif control_name == 'down':
			self.select_item(min(len(self.items) - 1, self.selected + 1))
		elif control_name == 'return':
			if self.selected is not None:
				action = self.items[self.selected][1]
				return self.perform_action(action)
		return super().update(control_name)

class MessageBox(Context):
	""" Displays message and requires answer or confirmation.
	"""
	def __init__(self, text, font, panel_widget, engine, text_shift=None, on_ok=None, on_cancel=None):
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
		self.on_ok = on_ok
		self.on_cancel = on_cancel

		self._panel_size = panel_widget.get_size(engine)
		window_size = engine.get_window_size()
		self._panel_topleft = Point(
				(window_size.width - self._panel_size.width) // 2,
				(window_size.height - self._panel_size.height) // 2,
				)

		self.add_widget(self._panel_topleft, panel_widget)
		self.add_widget(self._panel_topleft + (text_shift or Point(0, 0)), TextLineWidget(font, text))
	def add_button(self, engine, pos, button_widget):
		""" Adds button (non-functional decorative widget actually).
		Position is relative to the message box topleft corner.
		If any dimension of position is negative, it is counting back from the other side (bottom/right).
		"""
		pos = Point(pos)
		if pos.x < 0 or pos.y < 0:
			if pos.x < 0:
				pos.x = self._panel_size.width + pos.x
			if pos.y < 0:
				pos.y = self._panel_size.height + pos.y
		self.add_widget(self._panel_topleft + pos, button_widget)
	def update(self, control_name):
		""" Controls:
		- <Enter>, <Space>: OK
		- <Escape>: Cancel
		"""
		if control_name == 'escape':
			if self.on_cancel:
				self.on_cancel()
			raise self.Finished()
		elif control_name in ['space', 'return']:
			if self.on_ok:
				self.on_ok()
			raise self.Finished()
		return super().update(control_name)

class TextScreen(Context):
	""" Displays multiline (scrollablle) text screen.
	"""
	def __init__(self, text, font, panel_widget, engine, text_rect=None):
		""" Creates text screen with given text and font (required).
		Panel widget will be draw under the text and should fit the whole screen.
		Text will fit into given text_rect with automatic wrapping and automatic scrolling.
		"""
		super().__init__(transparent=False)
		window_size = engine.get_window_size()
		self.text_rect = Rect(text_rect or (0, 0, window_size.width, window_size.height))
		self._panel_size = panel_widget.get_size(engine)

		self.add_widget((0, 0), panel_widget)
		self._text_widget = MultilineScrollableTextWidget(font, self.text_rect.size, text)
		self.add_widget(self.text_rect.topleft, self._text_widget)
		self._button_up = None
		self._button_down = None
	def set_scroll_up_button(self, engine, pos, button_widget):
		""" Adds button for scrolling up.
		It should be of Button class so it can be highlighted when scrolling up is available
		and display as normal (inactive) when it's not.
		Position is relative to the message box topleft corner.
		If any dimension of position is negative, it is counting back from the other side (bottom/right).
		"""
		self._button_up = button_widget
		self._button_up.make_highlighted(self._text_widget.can_scroll_up())
		self.add_button(engine, pos, button_widget)
	def set_scroll_down_button(self, engine, pos, button_widget):
		""" Adds button for scrolling down.
		It should be of Button class so it can be highlighted when scrolling down is available
		and display as normal (inactive) when it's not.
		Position is relative to the message box topleft corner.
		If any dimension of position is negative, it is counting back from the other side (bottom/right).
		"""
		self._button_down = button_widget
		self._button_down.make_highlighted(self._text_widget.can_scroll_down())
		self.add_button(engine, pos, button_widget)
	def add_button(self, engine, pos, button_widget):
		""" Adds button (non-functional decorative widget actually).
		Position is relative to the message box topleft corner.
		If any dimension of position is negative, it is counting back from the other side (bottom/right).
		"""
		pos = Point(pos)
		if pos.x < 0 or pos.y < 0:
			if pos.x < 0:
				pos.x = self._panel_size.width + pos.x
			if pos.y < 0:
				pos.y = self._panel_size.height + pos.y
		self.add_widget(pos, button_widget)
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
		if self._button_up:
			self._button_up.make_highlighted(self._text_widget.can_scroll_up())
		if self._button_down:
			self._button_down.make_highlighted(self._text_widget.can_scroll_down())
		return super().update(control_name)

class ItemList(Context):
	""" Displays list of items with option to scroll up/down.
	Each item is a standalone widget of any type.
	"""
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
		window_size = engine.get_window_size()
		self.view_rect = Rect(view_rect or (0, 0, window_size.width, window_size.height))
		self._panel_size = background_widget.get_size(engine)
		self._caption_widget = caption_widget
		self._caption_height = self._caption_widget.get_size(engine).height if self._caption_widget else 0

		self.items = SelectionList(items, on_selection=lambda item, value: item.make_highlighted(value))
		self.items.select(self.items.get_next_selected_index())
		self.item_heights = [item.get_size(engine).height for item in self.items]

		self.scroller = Scroller(
				total_items=len(self.items),
				viewport_height=self.view_rect.height,
				item_height=lambda i: self.item_heights[i],
				)

		self.add_widget((0, 0), background_widget)
		self._button_up = None
		self._button_down = None
	def select_item(self, selected_index):
		""" Selects item by index.
		Highlights corresponding widget.
		"""
		self.items.select(selected_index)
		self.scroller.ensure_item_visible(selected_index)
	def can_scroll_up(self):
		""" Returns True if list can be scrolled up. """
		return self.scroller.can_scroll_up()
	def can_scroll_down(self):
		""" Returns True if list can be scrolled down. """
		return self.scroller.can_scroll_down()
	def add_button(self, engine, pos, button_widget):
		""" Adds button (non-functional decorative widget actually).
		Position is relative to the view rect topleft corner.
		If any dimension of position is negative, it is counting back from the other side (bottom/right).
		"""
		pos = Point(pos)
		if pos.x < 0 or pos.y < 0:
			if pos.x < 0:
				pos.x = self._panel_size.width + pos.x
			if pos.y < 0:
				pos.y = self._panel_size.height + pos.y
		self.add_widget(pos, button_widget)
	def set_scroll_up_button(self, engine, pos, button_widget):
		""" Adds button for scrolling up.
		It should be of Button class so it can be highlighted when scrolling up is available
		and display as normal (inactive) when it's not.
		Position is relative to the view rect topleft corner.
		If any dimension of position is negative, it is counting back from the other side (bottom/right).
		"""
		self._button_up = button_widget
		self._button_up.make_highlighted(self.can_scroll_up())
		self.add_button(engine, pos, button_widget)
	def set_scroll_down_button(self, engine, pos, button_widget):
		""" Adds button for scrolling down.
		It should be of Button class so it can be highlighted when scrolling down is available
		and display as normal (inactive) when it's not.
		Position is relative to the view rect topleft corner.
		If any dimension of position is negative, it is counting back from the other side (bottom/right).
		"""
		self._button_down = button_widget
		self._button_down.make_highlighted(self.can_scroll_down())
		self.add_button(engine, pos, button_widget)
	def _get_widgets_to_draw(self, engine):
		widgets = []
		widgets.extend(self.widgets)

		top_pos = self.view_rect.top
		if self._caption_widget:
			widgets.append(WidgetAtPos((
				self.view_rect.left,
				top_pos,
				), self._caption_widget))
			top_pos += self._caption_height
		for item_index in self.scroller.get_visible_range():
			widgets.append(WidgetAtPos((
				self.view_rect.left,
				top_pos,
				), self.items[item_index]))
			top_pos += self.item_heights[item_index]
		return widgets
	def perform_action(self, action):
		""" Programmatically perform action.
		Action should be an action-like object (see Menu docstring).
		"""
		import types
		if isinstance(action, Exception) or action is Exception or (isinstance(action, type) and issubclass(action, Exception)):
			raise action()
		elif callable(action):
			return action()
		return action # Treat as a new context.
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
			self.select_item(self.items.get_prev_selected_index())
		elif control_name == 'down':
			self.select_item(self.items.get_next_selected_index())
		elif control_name == 'return':
			if self.items.has_selection():
				action = self.items.get_selected_item().action
				return self.perform_action(action)
		if self._button_up:
			self._button_up.make_highlighted(self.can_scroll_up())
		if self._button_down:
			self._button_down.make_highlighted(self.can_scroll_down())
		return super().update(control_name)
