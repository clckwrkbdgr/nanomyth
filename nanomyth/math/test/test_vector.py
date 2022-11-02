import json
try:
	import jsonpickle
except ImportError: # pragma: no cover
	jsonpickle = None
from ...utils import unittest
from ..vector import Vector, Point, Size

class MyVector(Vector):
	@property
	def first(self): return self.values[0]
	@first.setter
	def first(self, value): self.values[0] = value
	@property
	def second(self): return self.values[1]
	@second.setter
	def second(self, value): self.values[1] = value

class TestVector(unittest.TestCase):
	def should_stringify_vector(self):
		p = MyVector(1, 2)
		self.assertEqual(str(p), str([1, 2]))
		self.assertEqual(repr(p), str(MyVector) + str(p))
	def should_create_vector(self):
		p = MyVector(1, 2)
		self.assertEqual(p.first, 1)
		self.assertEqual(p.second, 2)
		self.assertEqual(p[0], 1)
		self.assertEqual(p[1], 2)
		self.assertEqual(p, (1, 2))
	def should_call_setters(self):
		p = MyVector(1, 2)
		p.first = 2
		p.second = 3
		self.assertEqual(p[0], 2)
		self.assertEqual(p[1], 3)
	@unittest.skipUnless(jsonpickle, "Jsonpickle is not detected.")
	def should_serialize_vector_to_json(self):
		p = MyVector(1, 2)
		data = json.loads(jsonpickle.encode(p, unpicklable=False))
		self.assertEqual(data, [1, 2])
		self.assertEqual(jsonpickle.decode(jsonpickle.encode(p)), p)
	def should_have_hash(self):
		p = MyVector(1, 2)
		other = MyVector(1, 2)
		self.assertEqual(set([p]), set([other]))
	def should_create_vector_from_other_vector(self):
		p = MyVector(1, 2)
		o = MyVector(p)
		self.assertEqual(o.first, 1)
		self.assertEqual(o.second, 2)
	def should_compare_vectors(self):
		self.assertEqual(MyVector(1, 2), MyVector(1, 2))
		self.assertTrue(MyVector(1, 2) == MyVector(1, 2))
		self.assertFalse(MyVector(1, 2) != MyVector(1, 2))
		self.assertTrue(MyVector(1, 2) <= MyVector(1, 2))
		self.assertTrue(MyVector(1, 2) < MyVector(2, 2))
		self.assertTrue(MyVector(1, 2) < MyVector(1, 3))
	def should_get_absolute_values(self):
		self.assertEqual(abs(MyVector(1, 2)), MyVector(1, 2))
		self.assertEqual(abs(MyVector(-1, 2)), MyVector(1, 2))
		self.assertEqual(abs(MyVector(-1, -2)), MyVector(1, 2))
	def should_add_vectors(self):
		self.assertEqual(MyVector(1, 2) + MyVector(2, 3), MyVector(3, 5))
	def should_subtract_vectors(self):
		self.assertEqual(MyVector(3, 5) - MyVector(2, 3), MyVector(1, 2))
	def should_multiply_vector(self):
		self.assertEqual(MyVector(1, 2) * 2, MyVector(2, 4))
	def should_divide_vector(self):
		self.assertEqual(MyVector(2, 4) / 2, MyVector(1, 2))
		self.assertEqual(MyVector(5, 6) // 3, MyVector(1, 2))
		self.assertEqual(MyVector(2, 4).__div__(2), MyVector(1, 2))
		self.assertEqual(MyVector(2, 4).__truediv__(2), MyVector(1, 2))
	def should_iterate_over_vector(self):
		self.assertEqual(list(MyVector(1, 2)), [1, 2])

class TestPoint(unittest.TestCase):
	@unittest.skipUnless(jsonpickle, "Jsonpickle is not detected.")
	def should_serialize_point_to_json(self):
		p = Point(1, 2)
		data = json.loads(jsonpickle.encode(p, unpicklable=False))
		self.assertEqual(data, [1, 2])
		self.assertEqual(jsonpickle.decode(jsonpickle.encode(p)), p)
	def should_access_point_fields(self):
		p = Point(1, 2)
		p.x = 5
		p.y = 6
		self.assertEqual(p.x, 5)
		self.assertEqual(p.y, 6)
		self.assertEqual(list(p), [5, 6])
	def should_yield_all_surrounding_neighbours(self):
		actual = set(Point(1, 2).neighbours())
		expected = set(map(Point, [
			(0, 1), (1, 1), (2, 1),
			(0, 2), (1, 2), (2, 2),
			(0, 3), (1, 3), (2, 3),
			]))
		self.assertEqual(actual, expected)

class TestSize(unittest.TestCase):
	@unittest.skipUnless(jsonpickle, "Jsonpickle is not detected.")
	def should_serialize_size_to_json(self):
		p = Size(1, 2)
		data = json.loads(jsonpickle.encode(p, unpicklable=False))
		self.assertEqual(data, [1, 2])
		self.assertEqual(jsonpickle.decode(jsonpickle.encode(p)), p)
	def should_access_point_fields(self):
		p = Size(1, 2)
		p.width = 5
		p.height = 6
		self.assertEqual(p.width, 5)
		self.assertEqual(p.height, 6)
		self.assertEqual(list(p), [5, 6])
