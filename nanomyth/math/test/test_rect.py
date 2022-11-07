import json
try:
	import jsonpickle
except ImportError: # pragma: no cover
	jsonpickle = None
from ...utils import unittest
from ..vector import Point
from ..rect import Rect

class TestRect(unittest.TestCase):
	def should_construct_rect(self):
		# 01234567890
		#0
		#1
		#2 ####
		#3 #  #
		#4 #  #
		#5 #  #
		#6 ####
		#7
		rect = Rect((1, 2), (4, 5))
		self.assertEqual(rect.topleft, Point(1, 2))
		self.assertEqual(rect.bottomright, Point(4, 6))
		self.assertEqual(rect.size, Point(4, 5))
		self.assertEqual(rect.width, 4)
		self.assertEqual(rect.height, 5)
		self.assertEqual(rect.top, 2)
		self.assertEqual(rect.left, 1)
		self.assertEqual(rect.bottom, 6)
		self.assertEqual(rect.right, 4)

		another_rect = Rect((1, 2, 4, 5))
		self.assertEqual(another_rect, rect)

		yet_another_rect = Rect(another_rect)
		self.assertEqual(yet_another_rect, rect)
	def should_format_rect_repr(self):
		rect = Rect((1, 2), (4, 5))
		self.assertEqual(str(rect), '[1, 2]+[4, 5]')
		self.assertEqual(repr(rect), "<class 'nanomyth.math.rect.Rect'>(<class 'nanomyth.math.vector.Point'>[1, 2], <class 'nanomyth.math.vector.Size'>[4, 5])")
	def should_unpack_rect(self):
		rect = Rect((1, 2), (4, 5))
		self.assertEqual(list(rect), [1, 2, 4, 5])
	@unittest.skipUnless(jsonpickle, "Jsonpickle is not detected.")
	def should_serialize_rect(self):
		rect = Rect((1, 2), (4, 5))
		data = json.loads(jsonpickle.encode(rect, unpicklable=False))
		self.assertEqual(data, {'topleft': [1, 2], 'size' : [4, 5]})
		self.assertEqual(jsonpickle.decode(jsonpickle.encode(rect)), rect)
	def should_check_if_rects_are_equal(self):
		self.assertEqual(Rect((1, 2), (4, 5)), Rect((1, 2), (4, 5)))
		self.assertNotEqual(Rect((1, 2), (4, 5)), Rect((1, 2), (14, 15)))
	def should_detect_rect_containing_point(self):
		rect = Rect((1, 2), (4, 5))
		self.assertFalse(rect.contains(Point(0, 0)))
		self.assertFalse(rect.contains(Point(1, 2)))
		self.assertFalse(rect.contains(Point(1, 3)))
		self.assertTrue (rect.contains(Point(2, 3)))
		self.assertTrue (rect.contains(Point(3, 4)))
		self.assertFalse(rect.contains(Point(4, 5)))
		self.assertFalse(rect.contains(Point(0, 0), with_border=True))
		self.assertTrue (rect.contains(Point(1, 2), with_border=True))
		self.assertTrue (rect.contains(Point(1, 3), with_border=True))
		self.assertTrue (rect.contains(Point(2, 3), with_border=True))
		self.assertTrue (rect.contains(Point(3, 4), with_border=True))
		self.assertTrue (rect.contains(Point(4, 5), with_border=True))
