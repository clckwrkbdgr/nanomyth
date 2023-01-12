from ...utils import unittest
from ...math import Point
from ..actor import Player, Direction
from ..items import Item

class TestDirection(unittest.TestCase):
	def should_get_shift_from_direction(self):
		self.assertEqual(Direction.UP.get_shift(), Point(0, -1))
		self.assertEqual(Direction.DOWN.get_shift(), Point(0, +1))
		self.assertEqual(Direction.LEFT.get_shift(), Point(-1, 0))
		self.assertEqual(Direction.RIGHT.get_shift(), Point(+1, 0))
	def should_get_direction_from_shift(self):
		self.assertEqual(Direction.from_shift((0, -1)), Direction.UP)
		self.assertEqual(Direction.from_shift((0, -666)), Direction.UP)
		self.assertEqual(Direction.from_shift((0, +1)), Direction.DOWN)
		self.assertEqual(Direction.from_shift((0, +666)), Direction.DOWN)
		self.assertEqual(Direction.from_shift((-1, 0)), Direction.LEFT)
		self.assertEqual(Direction.from_shift((-666, 0)), Direction.LEFT)
		self.assertEqual(Direction.from_shift((+1, 0)), Direction.RIGHT)
		self.assertEqual(Direction.from_shift((+666, 0)), Direction.RIGHT)
		with self.assertRaises(ValueError):
			Direction.from_shift((1, 1))

class TestPlayer(unittest.TestCase):
	def should_create_character(self):
		char = Player('Wanderer', 'rogue')
		self.assertEqual(char.get_sprite(), 'rogue')
	def should_turn_character(self):
		char = Player('Wanderer', 'rogue', directional_sprites={
			Direction.UP : 'rogue_up',
			Direction.DOWN : 'rogue_down',
			Direction.LEFT : 'rogue_left',
			# Not Direction.RIGHT
			})
		self.assertEqual(char.get_sprite(), 'rogue_down')
		char.face_direction(Direction.UP)
		self.assertEqual(char.get_sprite(), 'rogue_up')
		char.face_direction(Direction.DOWN)
		self.assertEqual(char.get_sprite(), 'rogue_down')
		char.face_direction(Direction.LEFT)
		self.assertEqual(char.get_sprite(), 'rogue_left')
		char.face_direction(Direction.RIGHT)
		self.assertEqual(char.get_sprite(), 'rogue')
	def should_list_inventory(self):
		apple = Item('apple', 'apple')
		knife = Item('knife', 'knife')
		used_knife = Item('used knife', 'knife')

		char = Player('Wanderer', 'rogue')
		char.add_item(apple)
		char.add_item(knife)
		char.add_item(used_knife)

		self.assertEqual(list(char.iter_inventory()), [apple, knife, used_knife])
	def should_stack_similar_items(self):
		apple = Item('apple', 'apple')
		knife = Item('knife', 'knife')
		used_knife = Item('used knife', 'knife')
		another_knife = Item('knife', 'knife')

		char = Player('Wanderer', 'rogue')
		char.add_item(apple)
		char.add_item(knife)
		char.add_item(used_knife)
		char.add_item(another_knife)

		self.assertEqual(list(char.iter_stacked_inventory()), [(apple, 1), (knife, 2), (used_knife, 1)])
