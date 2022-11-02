import itertools
import copy
from .vector import Point, Size

class Matrix(object):
	""" Represents 2D matrix of arbitrary objects.
	"""
	def __init__(self, dims, default=None):
		""" Creates Matrix with specified dimensions (iterable len=2) and fills with specified default value:
		a = Matrix( (3, 3), default='.')
		b = Matrix( Size(3, 3), default='.')
		c = Matrix(b) # Creates deepcopy of another matrix.
		"""
		if isinstance(dims, Matrix):
			other = dims
			self.dims = copy.copy(other.dims)
			self.data = copy.deepcopy(other.data)
			return
		self.resize(dims, default=default)
	def resize(self, dims, default=None):
		""" Resizes matrix to a new size.
		NOTE: Clears map and fills with new default values.
		"""
		width, height = dims
		assert isinstance(width, int)
		assert isinstance(height, int)
		assert width > 0
		assert height > 0
		self.dims = Size(width, height)
		# TODO maybe clearing is not the best idea, maybe I should keep old values wherever is possible.
		self.data = [copy.deepcopy(default) for _ in range(width * height)]
	def fill(self, topleft, downright, value):
		""" Fills rectangle (including borders) with specified value. """
		topleft = Point(topleft)
		downright = Point(downright)
		for x in range(topleft.x, downright.x + 1):
			for y in range(topleft.y, downright.y + 1):
				self.set_cell(Point(x, y), value)
	def clear(self, value): # pragma: no cover
		""" Fills the whole map with specified value. """
		return self.fill(Point(0, 0), Point(self.width - 1, self.height - 1), value)
	@property
	def size(self):
		""" Returns iterable of size (two-component). """
		return self.dims
	@property
	def width(self):
		return self.dims.width
	@property
	def height(self):
		return self.dims.height
	def __repr__(self): # pragma: no cover
		return 'Matrix(({0}, {1}))'.format(*self.dims)
	def __eq__(self, other):
		if not isinstance(other, Matrix):
			raise TypeError("Cannot compare matrix with {0}".format(type(other)))
		if self.dims != other.dims:
			return False
		return self.data == other.data
	def __ne__(self, other):
		return not (self == other)
	def valid(self, pos):
		""" Returns True if pos is within Matrix boundaries. """
		pos = Point(pos)
		return 0 <= pos.x < self.dims.width and 0 <= pos.y < self.dims.height
	def cell(self, pos):
		""" Returns value of specified cell.
		Raises KeyError is position is invalid.
		"""
		pos = Point(pos)
		if not self.valid(pos):
			raise KeyError('Invalid cell position: {0}'.format(pos))
		return self.data[pos.x + pos.y * self.dims.width]
	def set_cell(self, pos, value):
		""" Sets value of specified cell.
		Raises KeyError is position is invalid.
		"""
		pos = Point(pos)
		if not self.valid(pos):
			raise KeyError('Invalid cell position: {0}'.format(pos))
		self.data[pos.x + pos.y * self.dims.width] = value
	def keys(self):
		""" Iterates over all available positions. """
		return iter(Point(x, y) for y, x in itertools.product(range(self.dims.height), range(self.dims.width)))
	def values(self):
		""" Iterates over all available values. """
		return iter(self.data)
	def __iter__(self):
		""" Iterates over all available positions, see keys(). """
		return self.keys()
	def find(self, value):
		""" Yields positions where value is found. """
		for pos in self.keys():
			if self.cell(pos) == value:
				yield pos
	def find_if(self, condition):
		""" Yields positions where values match given condition. """
		for pos in self.keys():
			if condition(self.cell(pos)):
				yield pos
	def transform(self, transformer):
		""" Returns new instance of matrix with same dimensions
		and transformer(c) applied for each cell.
		"""
		new_matrix = Matrix(self.dims)
		new_matrix.data = [transformer(copy.deepcopy(c)) for c in self.data]
		return new_matrix
	@classmethod
	def from_iterable(cls, iterable):
		""" Creates matrix from iterable of iterables (set of rows).
		All rows should be of equal width, otherwise ValueError is raised.
		"""
		data = []
		width, height = None, 0
		for row in iterable:
			row = list(row)
			if width is None:
				width = len(row)
			elif len(row) != width:
				raise ValueError('Not all lines are of equal width ({0})'.format(width))
			data.extend(row)
			height += 1
		m = cls(Size(width, height))
		m.data = data
		return m
	@classmethod
	def fromstring(cls, multiline_string, transformer=None):
		""" Creates matrix from multiline string.
		All lines should be of equal width, otherwise ValueError is raised.
		If transformer is specified, it should be callable that takes single argument (single string char) and transforms into matrix element. By default stored as string chars.
		"""
		lines = multiline_string.splitlines()
		width, height = max(map(len, lines)), len(lines)
		if any(len(line) != width for line in lines):
			raise ValueError('Not all lines are of equal width ({0})'.format(width))
		m = cls(Size(width, height))
		if not transformer:
			transformer = lambda c: c
		m.data = list(transformer(c) for c in itertools.chain.from_iterable(lines))
		return m
	def tostring(self, transformer=None):
		""" Returns multiline string representation of matrix.
		Each line represents single row.
		If transformer is specified, it should be callable that takes matrix element and converts to string representation. By default usual str() is used.
		"""
		result = ''
		if not transformer:
			transformer = str
		for start in range(0, len(self.data), self.dims[0]):
			for c in self.data[start:start+self.dims[0]]:
				result += transformer(c)
			result += '\n'
		return result
