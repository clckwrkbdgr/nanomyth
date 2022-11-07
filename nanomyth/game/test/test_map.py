import itertools
from ...utils import unittest
from ..map import Map, Terrain
from ..actor import Player
from ...math import Point

class TestMap(unittest.TestCase):
	def should_create_map_of_empty_tiles(self):
		level_map = Map()
		self.assertEqual(level_map.get_tile((0, 0)).get_images(), [])
	def should_access_tiles(self):
		level_map = Map()
		level_map.set_tile((1, 0), Terrain(['grass']))
		self.assertEqual(level_map.get_tile((1, 0)).get_images(), ['grass'])
		level_map.set_tile((1, 1), Terrain(['grass', 'tree']))
		self.assertEqual(level_map.get_tile((1, 1)).get_images(), ['grass', 'tree'])
	def should_iterate_over_tiles(self):
		level_map = Map()
		expected = []
		for y, x in itertools.product(range(5), range(5)):
			image_name = '{0}x{1}'.format(x, y)
			expected.append([image_name])
			level_map.set_tile((x, y), Terrain([image_name]))
		tiles = [(['{0}x{1}'.format(pos.x, pos.y)], tile.get_images()) for (pos, tile) in level_map.iter_tiles()]
		positions, actual_images = zip(*tiles)
		self.assertEqual(list(actual_images), expected)
		self.assertEqual(list(positions), expected)
	def should_place_actors(self):
		level_map = Map()
		level_map.add_actor((2, 2), Player('rogue'))
		self.assertEqual([(pos, player.sprite) for pos, player in level_map.iter_actors()], [(Point(2, 2), 'rogue')])
	def should_shift_player(self):
		level_map = Map()
		level_map.add_actor((2, 2), Player('rogue'))
		level_map.shift_player((0, -1))
		self.assertEqual(next(pos for pos, _ in level_map.iter_actors()), Point(2, 1))
		level_map.shift_player((0, -1))
		self.assertEqual(next(pos for pos, _ in level_map.iter_actors()), Point(2, 0))
		level_map.shift_player((0, -1))
		self.assertEqual(next(pos for pos, _ in level_map.iter_actors()), Point(2, 0))
