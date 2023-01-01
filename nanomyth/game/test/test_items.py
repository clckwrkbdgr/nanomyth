from ...utils import unittest
from ..items import Item

class TestItem(unittest.TestCase):
	def should_create_item(self):
		knife = Item('knife', 'knife')
		self.assertEqual(knife.get_sprite(), 'knife')
