from ..utils.meta import typed, fieldproperty

class Item:
	""" Basic item. """
	name = fieldproperty('_name', "Item's name.")

	@typed(str, str)
	def __init__(self, name, sprite):
		""" Creates item with name and sprite. """
		self._name = name
		self._sprite = sprite
	def __hash__(self):
		return hash((self._name, self._sprite))
	def get_sprite(self):
		return self._sprite
