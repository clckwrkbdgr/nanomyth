from ..utils.meta import fieldproperty

class Item:
	""" Basic item. """
	name = fieldproperty('_name', "Item's name.")

	def __init__(self, name, sprite):
		""" Creates item with name and sprite. """
		self._name = name
		self._sprite = sprite
	def get_sprite(self):
		return self._sprite
