from ...utils import unittest
from ..items import Item, Inventory

class TestItem(unittest.TestCase):
	def should_create_item(self):
		knife = Item('knife', 'knife')
		self.assertEqual(knife.get_sprite(), 'knife')

class TestInventory(unittest.TestCase):
	def should_list_inventory(self):
		apple = Item('apple', 'apple')
		knife = Item('knife', 'knife')
		used_knife = Item('used knife', 'knife')

		inventory = Inventory()
		inventory.add_item(apple)
		inventory.add_item(knife)
		inventory.add_item(used_knife)

		self.assertEqual(list(inventory.iter_plain()), [apple, knife, used_knife])
	def should_stack_similar_items(self):
		apple = Item('apple', 'apple')
		knife = Item('knife', 'knife')
		used_knife = Item('used knife', 'knife')
		another_knife = Item('knife', 'knife')

		inventory = Inventory()
		inventory.add_item(apple)
		inventory.add_item(knife)
		inventory.add_item(used_knife)
		inventory.add_item(another_knife)

		self.assertEqual(list(inventory.iter_stacked()), [(apple, 1), (knife, 2), (used_knife, 1)])
