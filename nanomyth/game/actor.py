from enum import Enum
from ..math import Point

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
	def __init__(self, name, sprite, trigger=None):
		""" Creates NPC with given name and sprite.
		Optional trigger can be set. It will be activated when interacted with NPC.
		Actor's Trigger should have callback with single parameter (actor itself).
		"""
		self.name = name
		self.sprite = sprite
		self.message = None
		self.trigger = trigger
	def set_trigger(self, new_trigger):
		""" Changes trigger which will be actived upon interaction. """
		self.trigger = new_trigger
	def get_sprite(self):
		return self.sprite

class Player:
	""" Player character. """
	def __init__(self, name, default_sprite, directional_sprites=None):
		""" Creates character with given name and sprite.
		Default sprite is used for static sprite (no direction).
		If directional_sprites is given, it should be a dict of {Direction : image_name}
		Sprites for missing directions are substituted with default sprite.
		By default characters faces DOWN (in isometric game this should is direction towards camera).
		"""
		self.name = name
		self.default_sprite = default_sprite
		self.directional_sprites = directional_sprites or {}
		self.direction = Direction.DOWN
	def get_sprite(self):
		return self.directional_sprites.get(self.direction, self.default_sprite)
	def face_direction(self, new_direction):
		self.direction = new_direction
