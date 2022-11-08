from ...utils import unittest
from ...math import Point
from ..actor import Player, Direction

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
		char = Player('rogue')
		self.assertEqual(char.get_sprite(), 'rogue')
	def should_turn_character(self):
		char = Player('rogue', directional_sprites={
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
