from .vector import Point, Size

class Rect(object):
	""" Represents rectangle. """
	def __init__(self, topleft, size=None):
		""" Creates rectangle from topleft (Point or tuple of 2 elements)
		and size (Size or tuple of 2 elements).
		If single argument is found, it is treated as another Rect or a tuple of 4 elements (x, y, width, height).
		"""
		if size is None:
			if isinstance(topleft, Rect):
				topleft, size = topleft.topleft, topleft.size
			else:
				topleft, size = topleft[:2], topleft[2:]
		self._topleft = Point(topleft)
		self._size = Size(size)
	def __str__(self):
		return '{0}+{1}'.format(self._topleft, self._size)
	def __repr__(self):
		return '{0}({1}, {2})'.format(type(self), repr(self._topleft), repr(self._size))
	def __setstate__(self, data): # pragma: no cover
		self._topleft = data['topleft']
		self._size = data['size']
	def __getstate__(self): # pragma: no cover
		return {'topleft':self._topleft, 'size':self._size}
	def __eq__(self, other):
		return other is not None and self._topleft == other._topleft and self._size == other._size
	def __iter__(self):
		return iter(tuple(self._topleft) + tuple(self._size))
	@property
	def width(self): return self._size.width
	@property
	def height(self): return self._size.height
	@property
	def size(self): return self._size
	@property
	def top(self): return self._topleft.y
	@property
	def left(self): return self._topleft.x
	@property
	def bottom(self): return self._topleft.y + self._size.height - 1
	@property
	def right(self): return self._topleft.x + self._size.width - 1
	@property
	def topleft(self): return Point(self.left, self.top)
	@property
	def bottomright(self): return Point(self.right, self.bottom)
	def contains(self, pos, with_border=False):
		pos = Point(pos)
		if with_border:
			return self.left <= pos.x <= self.right and self.top <= pos.y <= self.bottom
		return self.left < pos.x < self.right and self.top < pos.y < self.bottom
