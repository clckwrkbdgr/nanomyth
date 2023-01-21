from .vector import Point

class ObjectAtPos:
	""" Represents an objects put on map at a specific position.
	Object's attributes are accessible as direct attributes or via proxy attribute 'obj':

	>>> o = ObjectAtPos(pos, my_obj)
	>>> o.obj.field # Proxied.
	>>> o.obj.field = new_value
	>>> o.field # Direct.
	>>> o.field = new_value

	Position is accessible through .pos
	"""
	def __init__(self, pos, obj):
		self.__dict__['pos'] = Point(pos)
		self.__dict__['obj'] = obj
	def __getstate__(self):
		return self.__dict__
	def __setstate__(self, new_state):
		self.__dict__.update(new_state)
	def __getattr__(self, attr):
		return getattr(self.__dict__['obj'], attr)
	def __setattr__(self, attr, value):
		if attr in ('pos', 'obj'):
			self.__dict__[attr] = value
		else:
			setattr(self.__dict__['obj'], attr, value)
