from ...utils import unittest
from ..vector import Point
from ..mapping import ObjectAtPos
import pickle

class MockObject:
	def __init__(self, name):
		self.name = name

class TestObjectsAtPositions(unittest.TestCase):
	def should_access_objects_attributes_directly(self):
		obj = ObjectAtPos((5, 6), MockObject('name'))
		self.assertEqual(obj.obj.name, 'name')
		self.assertEqual(obj.name, 'name')
		self.assertEqual(obj.pos, Point(5, 6))
		obj.name = 'new name'
		self.assertEqual(obj.obj.name, 'new name')
		self.assertEqual(obj.name, 'new name')
		obj.pos += (1, 0)
		self.assertEqual(obj.pos, Point(6, 6))
	def should_pickle_and_unpickle_objects_at_pos(self):
		obj = ObjectAtPos((5, 6), MockObject('name'))
		savedata = pickle.dumps(obj)
		new_obj = pickle.loads(savedata)
		self.assertEqual(obj.name, new_obj.name)
		self.assertEqual(obj.obj.name, new_obj.obj.name)
		self.assertEqual(obj.pos, new_obj.pos)
