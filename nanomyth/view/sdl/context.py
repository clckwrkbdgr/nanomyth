"""
Game is a set of different contexts (main menu, map, inventory screen etc),
which are organized in a stack and can be switched back and forth.
Main context operations are performed by the SDLEngine itself.
"""
import pygame
from .widget import LevelMapWidget

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
	def update(self, control_name):
		""" Processes control events.
		`control_name` is the name of a pressed key.
		"""
		if control_name == 'escape':
			raise self.Finished()
	def draw(self, engine):
		""" Draws all widgets. """
		for widget in self.widgets:
			widget.draw(engine)

class Game(Context):
	""" Context for the main game screen: level map, player character etc.
	Controls player character via keyboard.

	Any other widgets (e.g. UI) can be added via usual .add_widget()
	"""
	def __init__(self, level_map):
		""" Creates game with given level map.
		"""
		super().__init__([
			LevelMapWidget(level_map, (0, 0)),
			])
		self.level_map = level_map
	def update(self, control_name):
		""" Controls player character: <Up>, <Down>, <Left>, <Right>
		<ESC>: Exit to the previous context.
		"""
		if control_name == 'escape':
			raise self.Finished()
		elif control_name == 'up':
			self.level_map.shift_player((0, -1))
		elif control_name == 'down':
			self.level_map.shift_player((0, +1))
		elif control_name == 'left':
			self.level_map.shift_player((-1, 0))
		elif control_name == 'right':
			self.level_map.shift_player((+1, 0))

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
	def __init__(self, on_escape=None):
		""" Creates menu context.
		Items can be added later via .add_menu_item().

		If on_escape is specified, it should be an action-like object (see Menu docstring)
		and it will performed when <ESC> is pressed.
		"""
		super().__init__()
		self.items = []
		self.selected = None
		self.on_escape = on_escape
	def add_menu_item(self, new_menu_item, on_selection=None):
		""" Adds new menu item (of MenuItem class) with optional action on selection.
		If action is specified, it should be an action-like object (see Menu docstring).
		"""
		self.widgets.append(new_menu_item)
		self.items.append((new_menu_item, on_selection))
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
