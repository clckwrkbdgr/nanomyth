from ..math import Matrix, Point
from . import actor
from .quest import QuestStateChange

class Terrain:
	""" Represents single map tile of terrain.
	"""
	def __init__(self, images, passable=True):
		""" Creates tile with specified images.
		If there are more than one images, they are drawn in the given order.
		E.g. ['basic grass', 'tree']

		To make terrain tile impassable (an obstacle), set passable=False. By default is True.
		"""
		self.images = images
		self.passable = passable
	def get_images(self):
		""" Returns list of images for the terrail tile. """
		return self.images

class Portal:
	""" Marks level exit tile.
	Once player steps on it, they are transferred to the new map
	placed at specified entrance position.
	"""
	def __init__(self, dest_map, entrance_pos):
		""" Creates portal to the entrance_pos on the dest_map.
		"""
		self.entrance_pos = Point(entrance_pos)
		self.dest_map = dest_map

class Trigger:
	""" Provides means to trigger user-defined event.
	Once player steps on it, event is triggered and attached action is taken.
	"""
	def __init__(self, trigger_name):
		""" Creates trigger with given name,
		which will be executed when trigger is activated.
		"""
		self.trigger_name = trigger_name
	def activate(self, trigger_registry, *params):
		""" Activates trigger by name using given trigger registry.
		Registry should be a callable that accepts trigger name and returns actual callback.
		"""
		if self.trigger_name:
			trigger_registry(self.trigger_name)(*params)

class ObjectOnMap:
	def __init__(self, pos, obj):
		self.pos = Point(pos)
		self.obj = obj

class ActorOnMap:
	def __init__(self, pos, actor):
		self.pos = Point(pos)
		self.actor = actor

class Portalling(Exception):
	""" Represents portalling event.
	"""
	def __init__(self, portal, player):
		self.portal = portal
		self.player = player

class Map:
	""" Rectangle level map.
	Supports terrain, actors (e.g. player) and other objects/events/triggers (e.g. portal tiles).
	"""
	def __init__(self, size):
		""" Creates empty map of given size with default (empty) terrain.
		"""
		self.tiles = Matrix(size, Terrain([]))
		self.actors = []
		self.portals = []
		self.triggers = []
	def set_tile(self, pos, tile):
		self.tiles.set_cell(pos, tile)
	def get_tile(self, pos):
		return self.tiles.cell(pos)
	def add_actor(self, pos, actor):
		""" Places actor on specified position. """
		self.actors.append(ActorOnMap(pos, actor))
	def remove_actor(self, name):
		""" Removes actor with given name from the map.
		Returns actor object.
		Returns None if no such actor is found.
		"""
		actor_index, actor = next(((i, other.actor) for i, other in enumerate(self.actors) if other.actor.name == name), None)
		if actor_index is not None:
			del self.actors[actor_index]
		return actor
	def find_actor(self, name):
		""" Returns actor with given name.
		Returns None if no such actor is found.
		"""
		return next((other.actor for other in self.actors if other.actor.name == name), None)
	def add_portal(self, pos, portal):
		""" Places a portal at the specified position. """
		self.portals.append(ObjectOnMap(pos, portal))
	def add_trigger(self, pos, trigger):
		""" Places a trigger at the specified position. """
		self.triggers.append(ObjectOnMap(pos, trigger))
	def shift_player(self, shift, trigger_registry=None, quest_registry=None):
		""" Moves player character by given shift.
		Shift could be either Point object (relative to the current position),
		or a Direction object (in this case will be performed as a single-tile step in given direction).

		Performs all available triggers if any are set on destination tile (like portals).
		Requires reference to the trigger registry for that (see details in Trigger).
		"""
		player = next(_ for _ in self.actors if isinstance(_.actor, actor.Player))
		if isinstance(shift, actor.Direction):
			direction = shift
			shift = direction.get_shift()
		else:
			direction = actor.Direction.from_shift(shift)
		new_pos = player.pos + shift
		player.actor.direction = direction
		if not self.tiles.valid(new_pos):
			return
		if not self.tiles.cell(new_pos).passable:
			return
		other_actor = next((other.actor for other in self.actors if other.pos == new_pos), None)
		if other_actor:
			if other_actor.trigger:
				if isinstance(other_actor.trigger, QuestStateChange):
					other_actor.trigger.activate(quest_registry, trigger_registry)
				else:
					other_actor.trigger.activate(trigger_registry, other_actor)
			return
		portal = next((portal.obj for portal in self.portals if portal.pos == new_pos), None)
		if portal:
			self.actors.remove(player)
			raise Portalling(portal, player.actor)
		player.pos = new_pos

		trigger = next((trigger.obj for trigger in self.triggers if trigger.pos == new_pos), None)
		if trigger:
			if isinstance(trigger, QuestStateChange):
				trigger.activate(quest_registry, trigger_registry)
			else:
				trigger.activate(trigger_registry)
	def iter_tiles(self):
		""" Iterates over tiles.
		Yields pairs (pos, tile).
		"""
		return ((pos, self.tiles.cell(pos)) for pos in self.tiles)
	def iter_actors(self):
		""" Iterate over placed actors (characters, monsters).
		Yields pairs (pos, actor).
		"""
		return ((_.pos, _.actor) for _ in self.actors)
