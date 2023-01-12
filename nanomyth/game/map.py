from ..math import Matrix, Point, Size
from . import actor
from .events import Trigger
from .quest import QuestStateChange
from .actor import NPC, Player, Direction
from .items import Item
from ..utils.meta import fieldproperty, typed

class Terrain:
	""" Represents single map tile of terrain.
	"""
	passable = fieldproperty('_passable', "Is tile passable on terrain level?")

	@typed(list)
	def __init__(self, images, passable=True):
		""" Creates tile with specified images.
		If there are more than one images, they are drawn in the given order.
		E.g. ['basic grass', 'tree']

		To make terrain tile impassable (an obstacle), set passable=False. By default is True.
		"""
		self._images = images
		self._passable = passable
	def get_images(self):
		""" Returns list of images for the terrain tile. """
		return self._images

class Portal:
	""" Marks level exit tile.
	Once player steps on it, they are transferred to the new map
	placed at specified entrance position.
	"""
	@typed(str, (Point, tuple, list))
	def __init__(self, dest_map, entrance_pos):
		""" Creates portal to the entrance_pos on the dest_map.
		"""
		self._entrance_pos = Point(entrance_pos)
		self._dest_map = dest_map
	def get_dest(self):
		""" Returns destination coordinates as tuple: (map name, pos). """
		return self._dest_map, self._entrance_pos

class ObjectOnMap: # TODO common ancestor with access to obj. properties and pos at the same level.
	def __init__(self, pos, obj):
		self.pos = Point(pos)
		self.obj = obj

class ItemOnMap: # TODO common ancestor with access to obj. properties and pos at the same level.
	def __init__(self, pos, item):
		self.pos = Point(pos)
		self.item = item

class ActorOnMap: # TODO common ancestor with access to obj. properties and pos at the same level.
	def __init__(self, pos, actor):
		self.pos = Point(pos)
		self.actor = actor

class Portalling(Exception):
	""" Represents portalling event.
	"""
	@typed(Portal, (NPC, Player))
	def __init__(self, portal, actor):
		self.portal = portal
		self.actor = actor

class Map:
	""" Rectangle level map.
	Supports terrain, actors (e.g. player) and other objects/events/triggers (e.g. portal tiles).
	"""
	@typed((Size, tuple, list))
	def __init__(self, size):
		""" Creates empty map of given size with default (empty) terrain.
		"""
		self._tiles = Matrix(size, Terrain([]))
		self._actors = []
		self._items = []
		self._portals = []
		self._triggers = []
	def get_size(self):
		return self._tiles.size
	@typed((Point, tuple, list), Terrain)
	def set_tile(self, pos, tile):
		self._tiles.set_cell(pos, tile)
	@typed((Point, tuple, list))
	def get_tile(self, pos):
		return self._tiles.cell(pos)
	@typed((Point, tuple, list), (NPC, Player))
	def add_actor(self, pos, actor):
		""" Places actor on specified position. """
		self._actors.append(ActorOnMap(pos, actor))
	@typed((NPC, Player))
	def remove_actor(self, actor):
		""" Removes specified actor from the map.
		Returns actor object.
		Returns None if no such actor is found.
		"""
		actor_index = next((i for i, other in enumerate(self._actors) if other.actor == actor), None)
		if actor_index is not None:
			del self._actors[actor_index]
		return actor
	@typed(str)
	def find_actor(self, name):
		""" Returns actor with given name.
		Returns None if no such actor is found.
		"""
		return next((other.actor for other in self._actors if other.actor.name == name), None)
	@typed(str)
	def find_actor_pos(self, name):
		""" Returns location of actor with given name.
		Returns None if no such actor is found.
		"""
		return next((other.pos for other in self._actors if other.actor.name == name), None)
	@typed((Point, tuple, list), Portal)
	def add_portal(self, pos, portal):
		""" Places a portal at the specified position. """
		self._portals.append(ObjectOnMap(pos, portal))
	@typed((Point, tuple, list), Trigger)
	def add_trigger(self, pos, trigger):
		""" Places a trigger at the specified position. """
		self._triggers.append(ObjectOnMap(pos, trigger))
	@typed((Point, tuple, list), Item)
	def add_item(self, pos, item):
		""" Places item on specified position. """
		self._items.append(ItemOnMap(pos, item))
	@typed((Point, tuple, list))
	def items_at_pos(self, pos):
		""" Returns list of items at specified location. """
		return [_.item for _ in self._items if _.pos == pos]
	@typed(Item)
	def remove_item(self, item):
		""" Removes specified item from the map.
		Returns item object.
		Returns None if no such item is found.
		"""
		item_index = next((i for i, other in enumerate(self._items) if other.item == item), None)
		if item_index is not None:
			del self._items[item_index]
		return item
	@typed((NPC, Player), item=(Item, None), at_pos=(Point, tuple, list, None))
	def pick_item(self, actor, item=None, at_pos=None):
		""" Makes actor pick item and store in their inventory.
		Actor object should have member .inventory.
		If item is not specified, first available item from at_pos is picked.
		If at_pos is not specified, actor's position is used.
		If there were not items at the position, returns None.
		Otherwise transfers item to the inventory and returns picked item object.
		"""
		if not item:
			if not at_pos:
				at_pos = self.find_actor_pos(actor.name)
			items = self.items_at_pos(at_pos)
			if not items:
				return None
			item = items[-1]
		item = self.remove_item(item)
		actor.add_item(item)
		return item
	@typed((NPC, Player), item=(Item, None), at_pos=(Point, tuple, list, None))
	def drop_item(self, actor, item, at_pos=None):
		""" Drops item from actor's inventory at specified pos.
		If pos is not specified, actor's position is used.
		Returns dropped item object.
		"""
		if not at_pos:
			at_pos = self.find_actor_pos(actor.name)
		actor.remove_item(item)
		self.add_item(at_pos, item)
		return item
	@typed((Point, tuple, list, Direction, None))
	def shift_player(self, shift, trigger_registry=None, quest_registry=None): # TODO typing registries.
		""" Moves player character by given shift.
		Shift could be either Point object (relative to the current position),
		or a Direction object (in this case will be performed as a single-tile step in given direction).

		Performs all available triggers if any are set on destination tile (like portals).
		Requires reference to the trigger registry for that (see details in Trigger).
		"""
		player = next(_ for _ in self._actors if isinstance(_.actor, actor.Player))
		if isinstance(shift, actor.Direction):
			direction = shift
			shift = direction.get_shift()
		else:
			direction = actor.Direction.from_shift(shift)
		new_pos = player.pos + shift
		player.actor.face_direction(direction)
		if not self._tiles.valid(new_pos):
			return
		if not self._tiles.cell(new_pos).passable:
			return
		other_actor = next((other.actor for other in self._actors if other.pos == new_pos), None)
		if other_actor:
			other_actor.on_interaction(trigger_registry, quest_registry)
			return
		portal = next((portal.obj for portal in self._portals if portal.pos == new_pos), None)
		if portal:
			raise Portalling(portal, player.actor)
		player.pos = new_pos

		trigger = next((trigger.obj for trigger in self._triggers if trigger.pos == new_pos), None)
		if trigger:
			if isinstance(trigger, QuestStateChange):
				trigger.activate(quest_registry, trigger_registry)
			else:
				trigger.activate(trigger_registry)
	def iter_tiles(self):
		""" Iterates over tiles.
		Yields pairs (pos, tile).
		"""
		return ((pos, self._tiles.cell(pos)) for pos in self._tiles)
	def iter_actors(self):
		""" Iterate over placed actors (characters, monsters).
		Yields pairs (pos, actor).
		"""
		return ((_.pos, _.actor) for _ in self._actors)
	def iter_items(self):
		""" Iterate over placed items.
		Yields pairs (pos, item).
		"""
		return ((_.pos, _.item) for _ in self._items)
