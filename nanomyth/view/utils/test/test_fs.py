from ....utils import unittest
from .. import fs
from pathlib import PurePath

class TestFileNames(unittest.TestCase):
	def should_create_unique_name(self):
		self.assertEqual(fs.create_unique_name(PurePath('foo', 'bar', 'baz.png'), []), 'baz')
		self.assertEqual(fs.create_unique_name(PurePath('foo', 'bar', 'baz.png'), ['baz']), 'bar_baz')
		self.assertEqual(fs.create_unique_name(PurePath('foo', 'bar', 'baz.png'), ['baz', 'bar_baz']), 'foo_bar_baz')
		self.assertEqual(fs.create_unique_name(PurePath('foo', 'bar', 'baz.png'), ['baz', 'bar_baz', 'foo_bar_baz']), str(PurePath('foo', 'bar', 'baz.png')))
