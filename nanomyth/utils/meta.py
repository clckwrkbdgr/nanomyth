import inspect

def wrap_docstring(f):
	def wrapped(*args, **kwargs): # pragma: no cover -- dummy definition, should not be called at all.
		return f(*args, **kwargs)
	wrapped.__doc__ = (inspect.getdoc(f) or "") + "\n\nNote: See {0} for details.".format(f.__qualname__)
	return wrapped

class Delegate:
	""" Dele """
	def __init__(self, member, base_method):
		self.member = member
		self.base_method = base_method
		self.method = self.base_method.__name__
	def __get__(self, obj, objtype):
		if obj is None:
			# When object does not exist, it probably means that inspect tries to get docstring for the class member.
			# In this case return original method with slightly adjusted docstring to indicate delegation.
			return wrap_docstring(self.base_method)
		return getattr(getattr(obj, self.member), self.method)
