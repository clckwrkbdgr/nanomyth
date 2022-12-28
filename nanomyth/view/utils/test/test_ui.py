from .. import ui
from ....math import Size
from ....utils import unittest
from ..ui import TextWrapper, Scroller, SelectionList

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
		self.assertEqual(scroller.get_visible_slice(), slice(0, 7))
		self.assertEqual(scroller.get_visible_range(), range(0, 7))
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
		self.assertEqual(scroller.get_visible_slice(), slice(1, 8))
		self.assertTrue(scroller.can_scroll_up())
		self.assertTrue(scroller.can_scroll_down())

		scroller.set_top_item(2)
		self.assertEqual(scroller.get_top_item(), 2)
		self.assertEqual(scroller.get_visible_slice(), slice(2, 9))
		self.assertTrue(scroller.can_scroll_up())
		self.assertTrue(scroller.can_scroll_down())

		scroller.set_top_item(3)
		self.assertEqual(scroller.get_top_item(), 3)
		self.assertEqual(scroller.get_visible_slice(), slice(3, 10))
		self.assertTrue(scroller.can_scroll_up())
		self.assertFalse(scroller.can_scroll_down())

		scroller.set_top_item(4)
		self.assertEqual(scroller.get_top_item(), 3)
		self.assertEqual(scroller.get_visible_slice(), slice(3, 10))
		self.assertTrue(scroller.can_scroll_up())
		self.assertFalse(scroller.can_scroll_down())
	def should_consider_items_having_different_heights(self):
		scroller = Scroller(
				total_items=10,
				viewport_height=60,
				item_height=lambda i: [8, 6, 5, 4, 5, 2, 10, 10, 10, 10, 10][i],
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
		self.assertEqual(scroller.get_visible_slice(), slice(1, 9))
		self.assertTrue(scroller.can_scroll_up())
		self.assertTrue(scroller.can_scroll_down())

		scroller.set_top_item(2)
		self.assertEqual(scroller.get_top_item(), 2)
		self.assertEqual(scroller.get_visible_slice(), slice(2, 10))
		self.assertTrue(scroller.can_scroll_up())
		self.assertFalse(scroller.can_scroll_down())

		scroller.set_top_item(3)
		self.assertEqual(scroller.get_top_item(), 2)
		self.assertEqual(scroller.get_visible_slice(), slice(2, 10))
		self.assertTrue(scroller.can_scroll_up())
		self.assertFalse(scroller.can_scroll_down())

		scroller.set_total_items(50, item_height=10)

		scroller.set_top_item(2)
		self.assertEqual(scroller.get_top_item(), 2)
		self.assertEqual(scroller.get_visible_slice(), slice(2, 8))
		self.assertTrue(scroller.can_scroll_up())
		self.assertTrue(scroller.can_scroll_down())
	def should_rearrang_viewport_after_size_is_changed(self):
		scroller = Scroller(
				total_items=10,
				viewport_height=60,
				item_height=8,
				)
		scroller.set_top_item(4)
		self.assertEqual(scroller.get_top_item(), 3)
		self.assertEqual(scroller.get_visible_slice(), slice(3, 10))
		self.assertTrue(scroller.can_scroll_up())
		self.assertFalse(scroller.can_scroll_down())

		scroller.set_height(64)
		self.assertEqual(scroller.get_top_item(), 2)
		self.assertEqual(scroller.get_visible_slice(), slice(2, 10))
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
		self.assertEqual(scroller.get_visible_slice(), slice(3, 10))
		self.assertTrue(scroller.can_scroll_up())
		self.assertFalse(scroller.can_scroll_down())

		scroller.set_total_items(5)
		self.assertEqual(scroller.get_top_item(), 0)
		self.assertEqual(scroller.get_visible_slice(), slice(0, 5))
		self.assertFalse(scroller.can_scroll_up())
		self.assertFalse(scroller.can_scroll_down())

		scroller.set_total_items(50)
		self.assertEqual(scroller.get_top_item(), 0)
		self.assertEqual(scroller.get_visible_slice(), slice(0, 7))
		self.assertFalse(scroller.can_scroll_up())
		self.assertTrue(scroller.can_scroll_down())
	def should_move_viewing_range_to_ensure_visibility_of_specific_item(self):
		scroller = Scroller(
				total_items=10,
				viewport_height=30,
				item_height=lambda i: [8, 6, 5, 4, 5, 2, 10, 10, 10, 10][i],
				)
		self.assertEqual(scroller.get_top_item(), 0)
		self.assertEqual(scroller.get_visible_slice(), slice(0, 6))

		scroller.ensure_item_visible(9)
		self.assertEqual(scroller.get_top_item(), 6)
		self.assertEqual(scroller.get_visible_slice(), slice(6, 9))

		scroller.ensure_item_visible(8)
		self.assertEqual(scroller.get_top_item(), 6)
		self.assertEqual(scroller.get_visible_slice(), slice(6, 9))

		scroller.ensure_item_visible(6)
		self.assertEqual(scroller.get_top_item(), 6)
		self.assertEqual(scroller.get_visible_slice(), slice(6, 9))

		scroller.ensure_item_visible(4)
		self.assertEqual(scroller.get_top_item(), 4)
		self.assertEqual(scroller.get_visible_slice(), slice(4, 8))

		scroller.ensure_item_visible(3)
		self.assertEqual(scroller.get_top_item(), 3)
		self.assertEqual(scroller.get_visible_slice(), slice(3, 7))

		scroller.ensure_item_visible(1)
		self.assertEqual(scroller.get_top_item(), 1)
		self.assertEqual(scroller.get_visible_slice(), slice(1, 6))

class TestSelectionList(unittest.TestCase):
	def should_create_list_without_selection(self):
		items = SelectionList(['foo', 'bar', 'baz'])
		self.assertIsNone(items.get_selected_index())
		self.assertFalse(items.has_selection())
		self.assertEqual(len(items), 3)
	def should_iterate_over_list(self):
		items = SelectionList(['foo', 'bar', 'baz'])
		self.assertEqual(list(items), ['foo', 'bar', 'baz'])
	def should_get_items_directly(self):
		items = SelectionList(['foo', 'bar', 'baz'])
		self.assertEqual(items[0], 'foo')
		self.assertEqual(items[1], 'bar')
		self.assertEqual(items[2], 'baz')
	def should_select_items(self):
		class SelectionEvents:
			def __init__(self): self.data = []
			def __call__(self, item, value): self.data.append((item, value))
		selection_events = SelectionEvents()

		items = SelectionList(['foo', 'bar', 'baz'], on_selection=selection_events)

		items.select(0)
		self.assertTrue(items.has_selection())
		self.assertEqual(items.get_selected_index(), 0)
		self.assertEqual(items.get_selected_item(), 'foo')

		items.select(1)
		self.assertTrue(items.has_selection())
		self.assertEqual(items.get_selected_index(), 1)
		self.assertEqual(items.get_selected_item(), 'bar')

		items.select(2)
		self.assertTrue(items.has_selection())
		self.assertEqual(items.get_selected_index(), 2)
		self.assertEqual(items.get_selected_item(), 'baz')

		items.select(None)
		self.assertFalse(items.has_selection())

		self.assertEqual(selection_events.data, [
			('foo', True),
			('foo', False), ('bar', True),
			('bar', False), ('baz', True),
			('baz', False),
			])
	def should_scroll_selection(self):
		items = SelectionList([])
		self.assertIsNone(items.get_next_selected_index())
		self.assertIsNone(items.get_prev_selected_index())

		items.append('foo')
		items.append('bar')
		items.append('baz')
		self.assertEqual(items.get_next_selected_index(), 0)
		self.assertEqual(items.get_prev_selected_index(), 2)

		items.select(0)
		self.assertEqual(items.get_next_selected_index(), 1)
		self.assertEqual(items.get_prev_selected_index(), 0)

		items.select(1)
		self.assertEqual(items.get_next_selected_index(), 2)
		self.assertEqual(items.get_prev_selected_index(), 0)

		items.select(2)
		self.assertEqual(items.get_next_selected_index(), 2)
		self.assertEqual(items.get_prev_selected_index(), 1)

		items.select(None)
		self.assertEqual(items.get_next_selected_index(), 0)
		self.assertEqual(items.get_prev_selected_index(), 2)
	def should_select_prev_and_next_items(self):
		items = SelectionList([])

		items.append('foo')
		items.append('bar')
		items.append('baz')
		self.assertEqual(items.get_selected_index(), None)

		items.select_next()
		self.assertEqual(items.get_selected_index(), 0)
		items.select_prev()
		self.assertEqual(items.get_selected_index(), 0)
		items.select_next()
		self.assertEqual(items.get_selected_index(), 1)
		items.select_next()
		self.assertEqual(items.get_selected_index(), 2)
		items.select_prev()
		self.assertEqual(items.get_selected_index(), 1)
		items.select_next()
		self.assertEqual(items.get_selected_index(), 2)
		items.select_next()
		self.assertEqual(items.get_selected_index(), 2)
