from enum import Enum
from ..math import Point
from .events import Trigger
from .items import Item
from ..utils.meta import fieldproperty, typed

class Direction(Enum):
	UP, DOWN, LEFT, RIGHT = range(4)
	def get_shift(self):
		if self == self.UP:
			return Point(0, -1)
		elif self == self.DOWN:
			return Point(0, +1)
		elif self == self.LEFT:
			return Point(-1, 0)
		elif self == self.RIGHT:
			return Point(+1, 0)
		raise ValueError('Unknown direction: {0}'.format(self)) # pragma: no cover
	@classmethod
	def from_shift(cls, shift):
		shift = Point(shift)
		if not (shift.x == 0 or shift.y == 0):
			raise ValueError("Cannot determine orthogonal direction from shift {0}, one of the dimensions should be zero".format(shift))
		if shift.y < 0:
			return cls.UP
		if shift.y > 0:
			return cls.DOWN
		if shift.x < 0:
			return cls.LEFT
		if shift.x > 0:
			return cls.RIGHT
		assert False, "Should not reach here." # pragma: no cover

class NPC:
	""" Non-player character. """
	name = fieldproperty('_name', "Character's name.")

	@typed(str, str, trigger=(Trigger, None))
	def __init__(self, name, sprite, trigger=None):
		""" Creates NPC with given name and sprite.
		Optional trigger can be set. It will be activated when interacted with NPC.
		Actor's Trigger should have callback with single parameter (actor itself).
		"""
		self._name = name
		self._sprite = sprite
		self._trigger = trigger
	@typed(Trigger)
	def set_trigger(self, new_trigger):
		""" Changes trigger which will be actived upon interaction. """
		self._trigger = new_trigger
	def get_sprite(self):
		return self._sprite
	def on_interaction(self, trigger_registry, quest_registry=None): # TODO needs to be typed.
		if not self._trigger:
			return
		from .quest import QuestStateChange # TODO move all kinds of triggers to events module
		if isinstance(self._trigger, QuestStateChange):
			self._trigger.activate(quest_registry, trigger_registry)
		else:
			self._trigger.activate(trigger_registry, self)

class Player:
	""" Player character. """
	name = fieldproperty('_name', "Character's name.")
	direction = fieldproperty('_direction', "Current direction character is facing.")

	@typed(str, str, dict)
	def __init__(self, name, default_sprite, directional_sprites=None):
		""" Creates character with given name and sprite.
		Default sprite is used for static sprite (no direction).
		If directional_sprites is given, it should be a dict of {Direction : image_name}
		Sprites for missing directions are substituted with default sprite.
		By default characters faces DOWN (in isometric game this should is direction towards camera).
		"""
		self._name = name
		self._default_sprite = default_sprite
		self._directional_sprites = directional_sprites or {}
		self._direction = Direction.DOWN
		self._inventory = []
	def get_sprite(self):
		return self._directional_sprites.get(self._direction, self._default_sprite)
	@typed(Direction)
	def face_direction(self, new_direction):
		""" Turn character into specified direction. """
		self._direction = new_direction
	@typed(Item)
	def add_item(self, item):
		""" Add item to the inventory. """
		self._inventory.append(item)
	@typed(Item)
	def remove_item(self, item):
		""" Remove item from the inventory. """
		del self._inventory[self._inventory.index(item)]
	def iter_inventory(self):
		""" Yields all items in the inventory. """
		for item in self._inventory:
			yield item
