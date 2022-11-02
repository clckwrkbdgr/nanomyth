import operator
from functools import total_ordering

@total_ordering
class Vector(object):
	""" Represents N-dim vector.
	Supported operations:
	- iteration over items;
	- serialization (pickle, jsonpickle);
	- accessing items: vector[i];
	- math operations: <=>, +, -, * (scalar), / (scalar), // (scalar).
	"""
	def __init__(self, *values):
		""" Creates vector from values, iterables or Vector:
		Vector(0, 1, 2, ...)
		Vector([0, 1, 2, ...])
		Vector(Vector(0, 1, 2, ...))
		"""
		if len(values) == 1:
			if isinstance(values[0], Vector):
				values = values[0].values
			else:
				values = values[0]
		self.values = list(values)
	def __str__(self):
		return str(self.values)
	def __repr__(self):
		return str(type(self)) + str(self)
	def __hash__(self):
		return hash(tuple(self.values))
	def __iter__(self):
		return iter(self.values)
	def __getitem__(self, attr):
		return self.values[attr]
	def __getstate__(self):
		return self.values
	def __setstate__(self, state):
		self.values = state
	def __eq__(self, other):
		return other is not None and self.values == Vector(other).values
	def __ne__(self, other):
		return not (self == other)
	def __lt__(self, other):
		return other is not None and self.values < Vector(other).values
	def __abs__(self):
		return type(self)(list(map(abs, self.values)))
	def __add__(self, other):
		return type(self)(list(map(operator.add, self.values, Vector(other).values)))
	def __sub__(self, other):
		return type(self)(list(map(operator.sub, self.values, Vector(other).values)))
	def __mul__(self, other):
		return type(self)(list(_ * other for _ in self.values))
	def __floordiv__(self, other):
		return type(self)(list(_ // other for _ in self.values))
	def __truediv__(self, other):
		return type(self)(list(_ / other for _ in self.values))
	def __div__(self, other):
		return type(self)(list(_ / other for _ in self.values))

class Point(Vector):
	""" Convenience type definition for 2D vector
	with access to first two elements under aliases .x and .y
	"""
	@property
	def x(self): return self.values[0]
	@x.setter
	def x(self, value): self.values[0] = value
	@property
	def y(self): return self.values[1]
	@y.setter
	def y(self, value): self.values[1] = value
	def neighbours(self):
		""" Returns all neighbours including the copy of original point:
		All points in 3x3 square around the original one.
		"""
		for x in [-1, 0, 1]:
			for y in [-1, 0, 1]:
				yield Point(self.x + x, self.y + y)

class Size(Vector):
	""" Convenience type definition for 2D vector
	with access to first two elements under aliases .width and .height
	"""
	@property
	def width(self): return self.values[0]
	@width.setter
	def width(self, value): self.values[0] = value
	@property
	def height(self): return self.values[1]
	@height.setter
	def height(self, value): self.values[1] = value
