import inspect

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
