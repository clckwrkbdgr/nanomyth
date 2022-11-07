from ...utils import unittest
from ..actor import Player

class TestPlayer(unittest.TestCase):
	def should_create_character(self):
		char = Player('rogue')
		self.assertEqual(char.sprite, 'rogue')
