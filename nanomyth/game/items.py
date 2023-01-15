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
	def __repr__(self):
		return '{0}({1})'.format(type(self).__name__, repr(self._name))
	def __hash__(self):
		return hash((self._name, self._sprite))
	def get_sprite(self):
		return self._sprite

class CollectibleItem(Item):
	""" Item that can be collected in large amounts as a single entity (money, ammo etc). """
	class InsufficientAmount(RuntimeError): pass
	class Empty(RuntimeError): pass

	amount = fieldproperty('_amount', "Amount of sub-items in the collectible.")

	@typed(str, str, int)
	def __init__(self, name, sprite, amount):
		""" Creates a collectible item with name and sprite and specified amount (> 0). """
		if amount <= 0:
			raise ValueError("Collectible's amount should be greater than 0. Got: {0}".format(amount))
		super().__init__(name, sprite)
		self._amount = amount
	@typed('CollectibleItem')
	def add(self, other):
		""" Adds other item into amount (should be the same exact item). """
		if hash(self) != hash(other):
			raise TypeError("Cannot join two different collectibles: {0} + {1}".format(self, other))
		self._amount += other._amount
	@typed('CollectibleItem')
	def subtract(self, other):
		""" Removes other item from amount (should be the same exact item).
		If item becomes empty in the result, raises CollectibleItem.Empty and does not perform operation.
		If requested item's amount is greater than actual, raises CollectibleItem.InsufficientAmount.
		"""
		if hash(self) != hash(other):
			raise TypeError("Cannot subtract two different collectibles: {0} + {1}".format(self, other))
		if self._amount < other._amount:
			raise CollectibleItem.InsufficientAmount()
		if self._amount == other._amount:
			raise CollectibleItem.Empty()
		self._amount -= other._amount
	@typed(int)
	def with_amount(self, amount):
		""" Returns new instance with specified amount.
		Amount is not checked against current one.
		"""
		return type(self)(self._name, self._sprite, amount=amount)

class Inventory:
	def __init__(self):
		self._items = []
	@typed(Item)
	def add_item(self, item):
		""" Add item to the inventory.
		If items is a CollectibleItem, it joins the existing one (if any), increasing its amount.
		"""
		if isinstance(item, CollectibleItem):
			existing = next((_ for _ in self._items if isinstance(_, CollectibleItem) and hash(_) == hash(item)), None)
			if existing:
				existing.add(item)
				return
		self._items.append(item)
	@typed(Item)
	def remove_item(self, item):
		""" Remove item from the inventory. """
		try:
			found = self._items.index(item)
		except ValueError:
			found = next((i for i, _ in enumerate(self._items) if hash(_) == hash(item)), None)
		if found is not None and isinstance(self._items[found], CollectibleItem):
			try:
				self._items[found].subtract(item)
				return
			except CollectibleItem.Empty:
				pass # Cannot be subtracted, should be removed completely as an item.
		del self._items[found]
	def iter_plain(self):
		""" Iterates over items in the inventory.  """
		for item in self._items:
			yield item
	def iter_stacked(self):
		""" Iterates over items in the inventory
		while stacking similar items.
		For collectible items returns their total amount.
		Yields pairs (item, count)
		"""
		for item, count in stack_similar(self._items):
			if isinstance(item, CollectibleItem) and count == 1:
				count = item.amount
			yield item, count
