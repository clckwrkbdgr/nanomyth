from .vector import Point, Size

class Rect(object):
	""" Represents rectangle. """
	def __init__(self, topleft, size):
		""" Creates rectangle from topleft (Point or tuple of 2 elements)
		and size (Size or tuple of 2 elements).
		"""
		self._topleft = Point(topleft)
		self._size = Size(size)
	def __setstate__(self, data): # pragma: no cover
		self._topleft = data['topleft']
		self._size = data['size']
	def __getstate__(self): # pragma: no cover
		return {'topleft':self._topleft, 'size':self._size}
	def __eq__(self, other):
		return other is not None and self._topleft == other._topleft and self._size == other._size
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
