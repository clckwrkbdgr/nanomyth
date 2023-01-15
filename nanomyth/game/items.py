from ..utils.meta import typed, fieldproperty
from ..math.itertools import stack_similar

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

class Inventory:
	def __init__(self):
		self._items = []
	@typed(Item)
	def add_item(self, item):
		""" Add item to the inventory. """
		self._items.append(item)
	@typed(Item)
	def remove_item(self, item):
		""" Remove item from the inventory. """
		del self._items[self._items.index(item)]
	def iter_plain(self):
		""" Iterates over items in the inventory.  """
		for item in self._items:
			yield item
	def iter_stacked(self):
		""" Iterates over items in the inventory
		while stacking similar items.
		Yields pairs (item, count)
		"""
		for item, count in stack_similar(self._items):
			yield item, count
