from ...utils import unittest
from ..itertools import stack_similar

class TestStack(unittest.TestCase):
	def should_stack_similar_objects(self):
		sequence = ['foo', 'bar', 'hello', 'baz', 'hell', 'world']
		actual = list(stack_similar(sequence, key=lambda x:x[:2]))
		expected = [('foo', 1), ('bar', 2), ('hello', 2), ('world', 1)]
		self.assertEqual(actual, expected)

