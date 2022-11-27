import textwrap
from ....utils import unittest
from ....math import Matrix
from .. import math

class TestPanel(unittest.TestCase):
	def should_fill_panel_with_tiles(self):
		tilemap = Matrix.from_iterable([
			'topleft top topright'.split(),
			'left middle right'.split(),
			'bottomleft bottom bottomright'.split(),
			])

		actual = math.tiled_panel(tilemap, (1, 1))
		expected = textwrap.dedent("""\
		[topleft][topright]
		[bottomleft][bottomright]
		""")
		self.assertEqual(actual.tostring(lambda s: '[{0}]'.format(s)), expected)

		actual = math.tiled_panel(tilemap, (5, 3))
		expected = textwrap.dedent("""\
		[topleft][top][top][top][topright]
		[left][middle][middle][middle][right]
		[bottomleft][bottom][bottom][bottom][bottomright]
		""")
		self.assertEqual(actual.tostring(lambda s: '[{0}]'.format(s)), expected)
