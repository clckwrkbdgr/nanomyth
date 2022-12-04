from .. import ui
from ....math import Size
from ....utils import unittest
from ..ui import TextWrapper, Scroller

class MockTextWrapper(TextWrapper):
	def get_letter_size(self, letter):
		return Size(5, 8) if letter != ' ' else Size(8, 8)

LOREM_IPSUM = """\
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
"""
LOREM_IPSUM_SPLIT = '.\n'.join(LOREM_IPSUM.split('. '))

class TestWrapping(unittest.TestCase):
	def should_wrap_text_to_fit_into_width(self):
		self.maxDiff = None

		wrapper = MockTextWrapper(LOREM_IPSUM, 200)
		self.assertEqual(wrapper.lines, [
			'Lorem ipsum dolor sit amet,',
			'consectetur adipiscing elit, sed do',
			'eiusmod tempor incididunt ut labore',
			'et dolore magna aliqua. Ut enim ad',
			'minim veniam, quis nostrud',
			'exercitation ullamco laboris nisi ut',
			'aliquip ex ea commodo consequat.',
			'Duis aute irure dolor in',
			'reprehenderit in voluptate velit',
			'esse cillum dolore eu fugiat nulla',
			'pariatur. Excepteur sint occaecat',
			'cupidatat non proident, sunt in',
			'culpa qui officia deserunt mollit',
			'anim id est laborum.',
			])
		self.assertEqual(wrapper.total_height, len(wrapper.lines) * 8)

		wrapper = MockTextWrapper(LOREM_IPSUM_SPLIT, 200)
		self.assertEqual(wrapper.lines, [
			'Lorem ipsum dolor sit amet,',
			'consectetur adipiscing elit, sed do',
			'eiusmod tempor incididunt ut labore',
			'et dolore magna aliqua.',
			'Ut enim ad minim veniam, quis',
			'nostrud exercitation ullamco laboris',
			'nisi ut aliquip ex ea commodo',
			'consequat.',
			'Duis aute irure dolor in',
			'reprehenderit in voluptate velit',
			'esse cillum dolore eu fugiat nulla',
			'pariatur.',
			'Excepteur sint occaecat cupidatat',
			'non proident, sunt in culpa qui',
			'officia deserunt mollit anim id est',
			'laborum.',
			])
		self.assertEqual(wrapper.total_height, len(wrapper.lines) * 8)

class TestScrolling(unittest.TestCase):
	def should_display_only_lines_that_fit_into_window(self):
		scroller = Scroller(
				total_items=10,
				viewport_height=60,
				item_height=8,
				)
		self.assertEqual(scroller.number_of_visible_items(), 7)
		self.assertEqual(scroller.get_visible_range(), slice(0, 7))
	def should_scroll_viewport(self):
		scroller = Scroller(
				total_items=10,
				viewport_height=60,
				item_height=8,
				)
		self.assertEqual(scroller.get_top_item(), 0)
		self.assertFalse(scroller.can_scroll_up())
		self.assertTrue(scroller.can_scroll_down())

		scroller.set_top_item(-1)
		self.assertEqual(scroller.get_top_item(), 0)
		self.assertFalse(scroller.can_scroll_up())
		self.assertTrue(scroller.can_scroll_down())

		scroller.set_top_item(0)
		self.assertEqual(scroller.get_top_item(), 0)
		self.assertFalse(scroller.can_scroll_up())
		self.assertTrue(scroller.can_scroll_down())

		scroller.set_top_item(1)
		self.assertEqual(scroller.get_top_item(), 1)
		self.assertEqual(scroller.get_visible_range(), slice(1, 8))
		self.assertTrue(scroller.can_scroll_up())
		self.assertTrue(scroller.can_scroll_down())

		scroller.set_top_item(2)
		self.assertEqual(scroller.get_top_item(), 2)
		self.assertEqual(scroller.get_visible_range(), slice(2, 9))
		self.assertTrue(scroller.can_scroll_up())
		self.assertTrue(scroller.can_scroll_down())

		scroller.set_top_item(3)
		self.assertEqual(scroller.get_top_item(), 3)
		self.assertEqual(scroller.get_visible_range(), slice(3, 10))
		self.assertTrue(scroller.can_scroll_up())
		self.assertFalse(scroller.can_scroll_down())

		scroller.set_top_item(4)
		self.assertEqual(scroller.get_top_item(), 3)
		self.assertEqual(scroller.get_visible_range(), slice(3, 10))
		self.assertTrue(scroller.can_scroll_up())
		self.assertFalse(scroller.can_scroll_down())
	def should_rearrang_viewport_after_size_is_changed(self):
		scroller = Scroller(
				total_items=10,
				viewport_height=60,
				item_height=8,
				)
		scroller.set_top_item(4)
		self.assertEqual(scroller.get_top_item(), 3)
		self.assertEqual(scroller.get_visible_range(), slice(3, 10))
		self.assertTrue(scroller.can_scroll_up())
		self.assertFalse(scroller.can_scroll_down())

		scroller.set_height(64)
		self.assertEqual(scroller.get_top_item(), 2)
		self.assertEqual(scroller.get_visible_range(), slice(2, 10))
		self.assertTrue(scroller.can_scroll_up())
		self.assertFalse(scroller.can_scroll_down())
	def should_rearrang_viewport_after_item_count_is_changed(self):
		scroller = Scroller(
				total_items=10,
				viewport_height=60,
				item_height=8,
				)
		scroller.set_top_item(4)
		self.assertEqual(scroller.get_top_item(), 3)
		self.assertEqual(scroller.get_visible_range(), slice(3, 10))
		self.assertTrue(scroller.can_scroll_up())
		self.assertFalse(scroller.can_scroll_down())

		scroller.set_total_items(5)
		self.assertEqual(scroller.get_top_item(), 0)
		self.assertEqual(scroller.get_visible_range(), slice(0, 5))
		self.assertFalse(scroller.can_scroll_up())
		self.assertFalse(scroller.can_scroll_down())

		scroller.set_total_items(50)
		self.assertEqual(scroller.get_top_item(), 0)
		self.assertEqual(scroller.get_visible_range(), slice(0, 7))
		self.assertFalse(scroller.can_scroll_up())
		self.assertTrue(scroller.can_scroll_down())
