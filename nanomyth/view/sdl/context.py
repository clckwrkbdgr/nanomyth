"""
Game is a set of different contexts (main menu, map, inventory screen etc),
which are organized in a stack and can be switched back and forth.
Main context operations are performed by the SDLEngine itself.
"""
import pygame

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
