"""
Game is a set of different contexts (main menu, map, inventory screen etc),
which are organized in a stack and can be switched back and forth.
Main context operations are performed by the SDLEngine itself.
"""
import pygame
from .widget import LevelMapWidget, TextLineWidget, ImageWidget
from ...math import Point

class Context:
	""" Basic game context.
	Context handles some arbitrary game entities
	and defines how they are drawn (via corresponding Widget objects in method draw())
	and how they are react to the control events (pressed keys etc, method update()).
	"""
	class Finished(Exception):
		""" Raise this when context is finished. """
		pass

	def __init__(self, widgets=None):
		""" Creates context with optional list of widgets.
		Widgets can be added later via add_widget.
		"""
		self.widgets = widgets or []
	def add_widget(self, widget):
		""" Adds new widget. """
		self.widgets.append(widget)
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
		for widget in self._get_widgets_to_draw():
			widget.draw(engine)

class Game(Context):
	""" Context for the main game screen: level map, player character etc.
	Controls player character via keyboard.

	Any other widgets (e.g. UI) can be added via usual .add_widget()
	"""
	def __init__(self, world):
		""" Creates game with given world.
		"""
		self.map_widget = LevelMapWidget(None, (0, 0))
		super().__init__([
			self.map_widget,
			])
		self.world = world
		self.map_widget.set_map(self.world.get_current_map())
	def load_world(self, new_world):
		""" Replaces World object with a new one.
		Used for loading savegames etc.
		"""
		self.world = new_world
		self.map_widget.set_map(self.world.get_current_map())
	def save_to_file(self, savefile):
		""" Saves game state to the file using Savefile instance.
		"""
		savefile.save(self.world)
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
		self.caption = TextLineWidget(font, (0, 0))
		self.selected = None
		self.on_escape = on_escape
	def _get_widgets_to_draw(self):
		widgets = []
		if self.background:
			widgets.append(self.background)
		widgets.extend(widget for widget, _ in self.items)
		widgets.append(self.caption)
		widgets.extend(self.widgets)
		return widgets
	def add_menu_item(self, new_menu_item, on_selection=None):
		""" Adds new menu item (of MenuItem class) with optional action on selection.
		If action is specified, it should be an action-like object (see Menu docstring).
		"""
		self.items.append((new_menu_item, on_selection))
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
		self.caption.set_text(text)
		if font:
			self.caption.font = font
	def set_background(self, image):
		""" Set background image.
		Can be either some ImageWidget, or name of the image in global image list -
		in this case image is locked to the topleft corner to fill the screen.
		"""
		if isinstance(image, str):
			image = ImageWidget(image, (0, 0))
		self.background = image
	def select_item(self, selected_index):
		""" Selects item by index.
		Highlights corresponding widget.
		"""
		self.selected = selected_index
		for index, item in enumerate(self.items):
			item[0].make_highlighted(index == selected_index)
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
