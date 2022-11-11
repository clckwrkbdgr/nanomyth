"""
Game is a set of different contexts (main menu, map, inventory screen etc),
which are organized in a stack and can be switched back and forth.
Main context operations are performed by the SDLEngine itself.
"""
import pygame
from .widget import LevelMapWidget, TextLineWidget, ImageWidget, MenuItem
from ...math import Point, Size

class WidgetAtPos:
	def __init__(self, topleft, widget):
		self.topleft = Point(topleft)
		self.widget = widget

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
	def update(self, control_name): # pragma: no cover
		""" Processes control events.
		`control_name` is the name of a pressed key.

		Default implementation does nothing.
		"""
	def _get_widgets_to_draw(self):
		""" Override this function to change widgets to draw.
		Widgets are drawn in the given order, from bottom to top.
		"""
		return self.widgets
	def draw(self, engine):
		""" Draws all widgets. """
		for _ in self._get_widgets_to_draw():
			_.widget.draw(engine, _.topleft)

class Game(Context):
	""" Context for the main game screen: level map, player character etc.
	Controls player character via keyboard.

	Any other widgets (e.g. UI) can be added via usual .add_widget()
	"""
	def __init__(self, world):
		""" Creates game with given world.
		"""
		super().__init__()
		self.map_widget = LevelMapWidget(None)
		self.add_widget((0, 0), self.map_widget)
		self.world = world
		self.map_widget.set_map(self.world.get_current_map())
	def load_world(self, new_world):
		""" Replaces World object with a new one.
		Used for loading savegames etc.
		"""
		self.world = new_world
		self.map_widget.set_map(self.world.get_current_map())
	def save_to_file(self, savefile, force=False):
		""" Saves game state to the file using Savefile instance.
		Returns True if was saved successfully, False if savefile already exists.
		With force=True overwrites existing savefile.
		"""
		if savefile.exists() and not force:
			return False
		savefile.save(self.world)
		return True
	def load_from_file(self, savefile):
		""" Loads game state from the file using Savefile instance.
		"""
		new_world = savefile.load()
		if not new_world: # pragma: no cover -- should not reach here in properly developed game.
			return False
		self.load_world(new_world)
		return True
	def get_current_map(self):
		""" Returns current map of the world
		(usually where player is).
		"""
		return self.world.get_current_map()
	def update(self, control_name):
		""" Controls player character: <Up>, <Down>, <Left>, <Right>
		<ESC>: Exit to the previous context.
		"""
		if control_name == 'escape':
			raise self.Finished()
		elif control_name == 'up':
			self.world.shift_player((0, -1))
		elif control_name == 'down':
			self.world.shift_player((0, +1))
		elif control_name == 'left':
			self.world.shift_player((-1, 0))
		elif control_name == 'right':
			self.world.shift_player((+1, 0))
		self.map_widget.set_map(self.world.get_current_map())

class Menu(Context):
	""" Game context for menu screens.

	Operates on set of MenuItem widgets with option to pick one and perform its action.
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
	def _get_widgets_to_draw(self):
		widgets = []
		if self.background:
			widgets.append(WidgetAtPos((0, 0), self.background))
		widgets.extend(widget for widget, _ in self.items)
		widgets.append(self.caption)
		widgets.extend(self.widgets)
		return widgets
	def add_menu_item(self, new_menu_item, on_selection=None):
		""" Adds new menu item with optional action on selection.

		Item should be either MenuItem object, or string, or tuple of two strings.
		In case of strings, they are treated as button caption (with optional normal/highlighted configuration)
		and are created using templated method (see set_button_* functions).
		WARNING: At least set_button_widget_template() is required for templated items.

		If action is specified, it should be an action-like object (see Menu docstring).
		"""
		button_pos = self._button_group_topleft + Point(0, self._button_height) * len(self.items)
		if isinstance(new_menu_item, MenuItem):
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
		self.items.append((WidgetAtPos(button_pos,
			MenuItem(
				button,
				TextLineWidget(
					self._button_caption_font, caption,
					),
				button_highlighted=button_highlighted,
				caption_highlighted=TextLineWidget(
					self._button_caption_font_highlighted, caption_highlighted,
					) if caption_highlighted else None,
				caption_shift=self._button_caption_shift,
				)),
			on_selection))
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
