import textwrap
import json
try:
	import jsonpickle
except ImportError: # pragma: no cover
	jsonpickle = None
from ...utils import unittest
from ..vector import Point
from ..matrix import Matrix

class TestMatrix(unittest.TestCase):
	def should_create_matrix(self):
		m = Matrix((2, 3), default='*')
		self.assertEqual(m.size, (2, 3))
		self.assertEqual(m.width, 2)
		self.assertEqual(m.height, 3)
	@unittest.skipUnless(jsonpickle, "Jsonpickle is not detected.")
	def should_serialize_matrix(self):
		m = Matrix((2, 3), default='*')
		m.set_cell((1, 0), 'A')
		m.set_cell((1, 1), 'Z')
		data = json.loads(jsonpickle.encode(m, unpicklable=False))
		self.assertEqual(data, {'data' : ['*', 'A', '*', 'Z', '*', '*'], 'dims' : [2, 3]})
		self.assertEqual(jsonpickle.decode(jsonpickle.encode(m)), m)
	def should_compare_matrices(self):
		a = Matrix((2, 3), default='*')
		with self.assertRaises(TypeError):
			a == 'something that is not matrix'
		b = Matrix((5, 6), default='*')
		self.assertNotEqual(a, b)

		a = Matrix.fromstring(textwrap.dedent("""\
				.X.
				XXX
				"""))
		b = Matrix.fromstring(textwrap.dedent("""\
				#.#
				.#.
				"""))
		c = Matrix.fromstring(textwrap.dedent("""\
				.X.
				XXX
				"""))
		self.assertNotEqual(a, b)
		self.assertEqual(a, c)
	def should_resize_matrix(self):
		m = Matrix((2, 3), default='*')
		self.assertEqual(m.size, (2, 3))
		m.resize((3, 2), default='_')
		self.assertEqual(m.size, (3, 2))
	def should_create_matrix_from_other_matrix(self):
		original = Matrix((2, 2))
		original.set_cell((0, 0), 'a')
		original.set_cell((0, 1), 'b')
		original.set_cell((1, 0), 'c')
		original.set_cell((1, 1), 'd')

		copy = Matrix(original)
		self.assertEqual(copy.cell((0, 0)), 'a')
		self.assertEqual(copy.cell((0, 1)), 'b')
		self.assertEqual(copy.cell((1, 0)), 'c')
		self.assertEqual(copy.cell((1, 1)), 'd')

		copy.set_cell((0, 0), '*')
		self.assertEqual(original.cell((0, 0)), 'a')

		original.set_cell((0, 0), '#')
		self.assertEqual(copy.cell((0, 0)), '*')
	def should_recognize_invalid_coords(self):
		m = Matrix((2, 2), default='*')
		self.assertTrue(m.valid((0, 0)))
		self.assertTrue(m.valid((0, 1)))
		self.assertTrue(m.valid((1, 0)))
		self.assertTrue(m.valid((1, 1)))
		self.assertFalse(m.valid((2, 2)))
		self.assertFalse(m.valid((-1, 0)))
	def should_get_cell_value(self):
		m = Matrix((2, 2), default='*')
		self.assertEqual(m.cell((0, 0)), '*')
		with self.assertRaises(KeyError):
			m.cell((-1, -1))
		with self.assertRaises(KeyError):
			m.cell((1, 10))
	def should_set_cell_value(self):
		m = Matrix((2, 2), default=' ')
		m.set_cell((0, 0), '*')
		self.assertEqual(m.cell((0, 0)), '*')
		with self.assertRaises(KeyError):
			m.set_cell((-1, -1), 'a')
		with self.assertRaises(KeyError):
			m.set_cell((1, 10), 'a')
	def should_iterate_over_indexes(self):
		m = Matrix((2, 2))
		m.data = list('abcd')
		indexes = ' '.join(''.join(map(str, index)) for index in m)
		self.assertEqual(indexes, '00 10 01 11')
		indexes = ' '.join(''.join(map(str, index)) for index in m.keys())
		self.assertEqual(indexes, '00 10 01 11')
		values = ' '.join(m.values())
		self.assertEqual(values, 'a b c d')
	def should_find_value_in_matrix(self):
		a = Matrix.fromstring(textwrap.dedent("""\
				ab
				ca
				"""))
		self.assertEqual(list(a.find('a')), [Point(0, 0), Point(1, 1)])
		self.assertEqual(list(a.find('X')), [])
		self.assertEqual(list(a.find_if(lambda c:c>'a')), [Point(1, 0), Point(0, 1)])
		self.assertEqual(list(a.find_if(lambda c:c<'a')), [])
	def should_transform_matrix(self):
		original = Matrix.fromstring('01\n23')
		processed = original.transform(int)
		self.assertEqual(processed.width, 2)
		self.assertEqual(processed.height, 2)
		self.assertEqual(processed.data, [
			0, 1,
			2, 3,
			])
	def should_construct_matrix_from_iterable(self):
		with self.assertRaises(ValueError):
			Matrix.from_iterable( (range(3), range(4)) )

		m = Matrix.from_iterable( (range(4), range(4, 8)) )
		self.assertEqual(m.width, 4)
		self.assertEqual(m.height, 2)
		self.assertEqual(m.data, [
			0, 1, 2, 3,
			4, 5, 6, 7,
			])
	def should_construct_matrix_from_multiline_string(self):
		data = textwrap.dedent("""\
				.X.X.
				XXXXX
				""")
		m = Matrix.fromstring(data)
		self.assertEqual(m.width, 5)
		self.assertEqual(m.height, 2)
		self.assertEqual(m.data, [
			'.', 'X', '.', 'X', '.',
			'X', 'X', 'X', 'X', 'X',
			])

		with self.assertRaises(ValueError):
			Matrix.fromstring("short\nlong")

		data = textwrap.dedent("""\
				.a.b.
				cabcd
				""")
		m = Matrix.fromstring(data, transformer=lambda c: -1 if c == '.' else ord(c) - ord('a'))
		self.assertEqual(m.width, 5)
		self.assertEqual(m.height, 2)
		self.assertEqual(m.data, [
			-1, 0, -1, 1, -1,
			2, 0, 1, 2, 3,
			])
	def should_convert_matrix_to_string(self):
		m = Matrix((5, 2))
		m.data = [
			'.', 'X', '.', 'X', '.',
			'X', 'X', 'X', 'X', 'X',
			]
		expected = textwrap.dedent("""\
				.X.X.
				XXXXX
				""")
		self.assertEqual(m.tostring(), expected)

		m = Matrix((5, 2))
		m.data = [
			-1, 0, -1, 1, -1,
			2, 0, 1, 2, 3,
			]
		expected = textwrap.dedent("""\
				.a.b.
				cabcd
				""")
		self.assertEqual(m.tostring(transformer=lambda c: '.' if c < 0 else chr(c + ord('a'))), expected)
	def should_fill_rectangle(self):
		m = Matrix((10, 5), '.')
		m.fill(Point(3, 1), Point(8, 3), 'X')
		expected = textwrap.dedent("""\
				..........
				...XXXXXX.
				...XXXXXX.
				...XXXXXX.
				..........
				""")
		actual = m.tostring()
		self.assertEqual(actual, expected)
