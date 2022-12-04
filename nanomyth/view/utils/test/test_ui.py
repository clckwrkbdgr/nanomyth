from .. import ui
from ....math import Size
from ..ui import TextWrapper
from ....utils import unittest

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
