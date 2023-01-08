import inspect
import functools

def wrap_docstring(f, original_delegate=None):
	""" Fixes docstring of wrapped object to propagate the original docstring
	and appends reference to the original method.
	"""
	def wrapper(*args, **kwargs): # pragma: no cover -- dummy definition, should not be called at all.
		return f(*args, **kwargs)
	wrapper.__doc__ = (inspect.getdoc(f) or "") + "\n\nNote: See {0} for details.".format(f.__qualname__)
	wrapper.__wrapped_delegate__  = original_delegate
	return wrapper

class Delegate:
	""" Delegates methods to a member. """
	def __init__(self, member, base_method):
		""" Declares delegated method of a member object.
		base_method should be fully-qualified name of the original member function (Class.func).
		"""
		self.member = member
		self.base_method = base_method
		if hasattr(self.base_method, '__wrapped_delegate__'):
			self.base_method = self.base_method.__wrapped_delegate__
			self.method = None
		else:
			self.method = self.base_method.__name__
	def __get__(self, obj, objtype):
		if obj is None:
			# When object does not exist, it probably means that inspect tries to get docstring for the class member.
			# In this case return original method with slightly adjusted docstring to indicate delegation.
			return wrap_docstring(self.base_method, original_delegate=self)
		if self.method is None:
			# Means that delegate was created to already delegated function,
			# and we need to get delegated's delegate name by questioning member's dict for the original delegate.
			for method, v in getattr(obj, self.member).__class__.__dict__.items():
				if v is self.base_method:
					self.method = method
					return getattr(getattr(obj, self.member), method)
		return getattr(getattr(obj, self.member), self.method)

class fieldproperty:
	""" Read-only property that is directly tied to an internal field.
	"""
	def __init__(self, field_name, docstring=None):
		""" Creates property for given field.
		Optional docstring can be set.
		"""
		self.field_name = field_name
		self.__doc__ = docstring
	def __repr__(self):
		return self.__doc__
	def __get__(self, obj, objtype):
		if obj is None:
			return self
		return getattr(obj, self.field_name)

def typed(*arg_types, **kwarg_types):
	""" Adds simple type checking for arguments (both positional and keyword ones).
	Raises TypeError if arguments are not instances of the corresponding type.
	Types are matched in the order of specification (or by keywords for keyword ones).
	If there are less types specified than there are arguments, remaining arguments are skipped (no type check).
	The same goes for skipped keyword arguments.

	Example:

	>>> class C:
	>>>   @typed(str, value=list)
	>>>   def func(self, str_arg, value=None):
	>>>      ...
	"""
	def _wrapper(f):
		@functools.wraps(f)
		def _actual(*args, **kwargs):
			args_to_check = args
			if next(iter(inspect.signature(f).parameters), None) == 'self': # Hack: detect obj method, first argument is self.
				args_to_check = args_to_check[1:]
			for index, (arg, arg_type) in enumerate(zip(args_to_check, arg_types)):
				if not isinstance(arg, arg_type):
					raise TypeError('Expected {0} for arg #{1}, got: {2}'.format(arg_type.__name__, index, type(arg).__name__))
			for keyword in kwargs.keys():
				if keyword not in kwarg_types:
					continue
				if not isinstance(kwargs[keyword], kwarg_types[keyword]):
					raise TypeError('Expected {0} for arg {1}, got: {2}'.format(kwarg_types[keyword].__name__, repr(keyword), type(kwargs[keyword]).__name__))
			return f(*args, **kwargs)
		return _actual
	return _wrapper
