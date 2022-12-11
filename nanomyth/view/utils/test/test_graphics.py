import textwrap
from ....utils import unittest
from ....math import Matrix, Rect, Size, Point
from .. import graphics

#   |    |    |    |    |
TILES = """\
.000....1..222..333....44
.0.0...11....2...33...4.4
.0.0....1...2.....3..4444
.000....1..222..333.....4
..a...bbb..ccc.W...W.....
.a.a..bb...c...W.W.W.....
.aaa..b.b..c...W.W.W.....
.a.a..bb...ccc..W.W......
"""

class TestBoundRect(unittest.TestCase):
	def get_submatrix(self, m, rect):
		result = Matrix(rect.size)
		for x in range(rect.left, rect.right + 1):
			for y in range(rect.top, rect.bottom + 1):
				result.set_cell((x - rect.left, y - rect.top), m.cell((x, y)))
		return result
	def should_get_bounding_rect_for_tile(self):
		tiles = Matrix.fromstring(TILES)
		is_pixel_background = lambda p: tiles.cell(p) == '.'
		tile_size = Size(5, 4)

		tile_0 = Rect((tile_size.width * 0, tile_size.height * 0), tile_size)
		expected_0 = textwrap.dedent("""\
				000
				0.0
				0.0
				000
				""")
		self.assertEqual(self.get_submatrix(tiles, graphics.get_bounding_rect(tile_0, is_pixel_background)).tostring(), expected_0)

		tile_1 = Rect((tile_size.width * 1, tile_size.height * 0), tile_size)
		expected_1 = textwrap.dedent("""\
				.1
				11
				.1
				.1
				""")
		self.assertEqual(self.get_submatrix(tiles, graphics.get_bounding_rect(tile_1, is_pixel_background)).tostring(), expected_1)

		tile_4 = Rect((tile_size.width * 4, tile_size.height * 0), tile_size)
		expected_4 = textwrap.dedent("""\
				..44
				.4.4
				4444
				...4
				""")
		self.assertEqual(self.get_submatrix(tiles, graphics.get_bounding_rect(tile_4, is_pixel_background)).tostring(), expected_4)

		tile_W = Rect((tile_size.width * 3, tile_size.height * 1), tile_size)
		expected_W = textwrap.dedent("""\
				W...W
				W.W.W
				W.W.W
				.W.W.
				""")
		self.assertEqual(self.get_submatrix(tiles, graphics.get_bounding_rect(tile_W, is_pixel_background)).tostring(), expected_W)

		tile_space = Rect((tile_size.width * 4, tile_size.height * 1), tile_size)
		expected_space = textwrap.dedent("""\
				.
				.
				.
				.
				""")
		self.assertEqual(self.get_submatrix(tiles, graphics.get_bounding_rect(tile_space, is_pixel_background)).tostring(), expected_space)

		expected_wide_space = textwrap.dedent("""\
				...
				...
				...
				...
				""")
		self.assertEqual(self.get_submatrix(tiles, graphics.get_bounding_rect(tile_space, is_pixel_background, space_width=3)).tostring(), expected_wide_space)
