from ...utils import unittest
from ...math import Point
from ..world import World
from ..map import Map, Terrain, Portal
from ..actor import Player, Direction
from ..quest import Quest

class TestWorld(unittest.TestCase):
	def _create_world(self):
		world = World()
		home, desert = Map((5, 5)), Map((5, 5))
		home.set_tile((0, 0), Terrain(['floor']))
		desert.set_tile((0, 0), Terrain(['desert']))
		world.add_map('home', home)
		world.add_map('desert', desert)
		home.add_actor((2, 2), Player('Wanderer', 'rogue'))
		home.add_portal((2, 1), Portal('desert', (1, 2)))
		quest = Quest('MyQuest', ['foo'], ['a'])
		world.add_quest('my_quest', quest)
		return world

	def should_create_world_with_maps(self):
		world = self._create_world()
		self.assertEqual(world.get_current_map().get_tile((0, 0)).get_images(), ['floor'])
		world.set_current_map('desert')
		self.assertEqual(world.get_current_map().get_tile((0, 0)).get_images(), ['desert'])
		self.assertEqual(world.get_map('home').get_tile((0, 0)).get_images(), ['floor'])
		self.assertEqual(world.get_quest('my_quest').title, 'MyQuest')
	def should_portal_to_another_map(self):
		class Callback:
			def __init__(self): self.data = []
			def __call__(self, *params): self.data.append(params)
		on_change_map = Callback()

		world = self._create_world()
		world.shift_player((0, -1), on_change_map=on_change_map)
		self.assertEqual(world.current_map, 'desert')
		pos, player = next(world.get_current_map().iter_actors())
		self.assertEqual(pos, Point(1, 2))
		self.assertEqual(player.direction, Direction.UP)
		self.assertEqual(on_change_map.data, [(world.get_current_map(),)])
