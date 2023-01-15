from ...utils import unittest
from ..items import Item, CollectibleItem, Inventory

class TestItem(unittest.TestCase):
	def should_create_item(self):
		knife = Item('knife', 'knife')
		self.assertEqual(knife.get_sprite(), 'knife')

class TestCollectibleItem(unittest.TestCase):
	def should_create_collectible_item(self):
		with self.assertRaises(ValueError) as e:
			CollectibleItem('money', 'gold', 0)
		self.assertEqual(str(e.exception), "Collectible's amount should be greater than 0. Got: 0")

		with self.assertRaises(ValueError) as e:
			CollectibleItem('money', 'gold', -10)
		self.assertEqual(str(e.exception), "Collectible's amount should be greater than 0. Got: -10")

		money = CollectibleItem('money', 'gold', 300)
		self.assertEqual(money.amount, 300)
	def should_join_collectible_items(self):
		money = CollectibleItem('money', 'gold', 300)
		money.add(money.with_amount(500))
		self.assertEqual(money.amount, 800)

		with self.assertRaises(TypeError) as e:
			money.add(CollectibleItem('caps', 'bottle_caps', 10000))
		self.assertEqual(str(e.exception), "Cannot join two different collectibles: CollectibleItem('money') + CollectibleItem('caps')")
	def should_subtract_collectible_items(self):
		money = CollectibleItem('money', 'gold', 300)

		with self.assertRaises(CollectibleItem.InsufficientAmount) as e:
			money.subtract(money.with_amount(500))

		with self.assertRaises(CollectibleItem.Empty) as e:
			money.subtract(money.with_amount(300))

		money.subtract(CollectibleItem('money', 'gold', 50))
		self.assertEqual(money.amount, 250)

		with self.assertRaises(TypeError) as e:
			money.subtract(CollectibleItem('caps', 'bottle_caps', 10))
		self.assertEqual(str(e.exception), "Cannot subtract two different collectibles: CollectibleItem('money') + CollectibleItem('caps')")

class TestInventory(unittest.TestCase):
	def should_add_collectible_items(self):
		apple = Item('apple', 'apple')
		inventory = Inventory()

		inventory.add_item(CollectibleItem('money', 'gold', 100))
		self.assertEqual(list(inventory.iter_plain())[0].amount, 100)

		inventory.add_item(apple)
		self.assertEqual(list(inventory.iter_plain())[0].amount, 100)

		inventory.add_item(CollectibleItem('money', 'gold', 200))
		self.assertEqual(list(inventory.iter_plain())[0].amount, 300)
	def should_remove_collectible_items(self):
		apple = Item('apple', 'apple')
		inventory = Inventory()

		inventory.add_item(CollectibleItem('money', 'gold', 300))
		self.assertEqual(list(inventory.iter_plain())[0].amount, 300)

		inventory.add_item(apple)
		self.assertEqual(list(inventory.iter_plain())[0].amount, 300)

		inventory.remove_item(CollectibleItem('money', 'gold', 200))
		self.assertEqual(list(inventory.iter_plain())[0].amount, 100)

		inventory.remove_item(CollectibleItem('money', 'gold', 100))
		self.assertEqual(list(inventory.iter_plain()), [apple])
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
		money = CollectibleItem('money', 'gold', 100)

		inventory = Inventory()
		inventory.add_item(apple)
		inventory.add_item(knife)
		inventory.add_item(used_knife)
		inventory.add_item(another_knife)
		inventory.add_item(money)

		self.assertEqual(list(inventory.iter_stacked()), [(apple, 1), (knife, 2), (used_knife, 1), (money, 100)])
