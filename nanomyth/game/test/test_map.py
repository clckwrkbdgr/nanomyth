import itertools
from ...utils import unittest
from ..map import Map, Terrain, Trigger
from ..actor import Player, Direction, NPC
from ...math import Point

class TestMap(unittest.TestCase):
	def should_create_map_of_empty_tiles(self):
		level_map = Map((5, 5))
		self.assertEqual(level_map.get_tile((0, 0)).get_images(), [])
	def should_access_tiles(self):
		level_map = Map((5, 5))
		level_map.set_tile((1, 0), Terrain(['grass']))
		self.assertEqual(level_map.get_tile((1, 0)).get_images(), ['grass'])
		level_map.set_tile((1, 1), Terrain(['grass', 'tree']))
		self.assertEqual(level_map.get_tile((1, 1)).get_images(), ['grass', 'tree'])
	def should_iterate_over_tiles(self):
		level_map = Map((5, 5))
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
		level_map = Map((5, 5))
		level_map.add_actor((2, 2), Player('Wanderer', 'rogue'))
		self.assertEqual([(pos, player.get_sprite()) for pos, player in level_map.iter_actors()], [(Point(2, 2), 'rogue')])
	def should_find_actors_by_name(self):
		level_map = Map((5, 5))
		level_map.add_actor((2, 2), Player('Wanderer', 'rogue'))
		self.assertEqual(level_map.find_actor('Wanderer').get_sprite(), 'rogue')
		self.assertIsNone(level_map.find_actor('Absent'))
	def should_remove_actors(self):
		level_map = Map((5, 5))
		level_map.add_actor((2, 2), Player('Wanderer', 'rogue'))
		level_map.remove_actor('Wanderer')
		self.assertIsNone(level_map.find_actor('Wanderer'))
	def should_shift_player(self):
		level_map = Map((5, 5))
		level_map.add_actor((2, 2), Player('Wanderer', 'rogue'))

		level_map.shift_player((0, -1))
		self.assertEqual(next(pos for pos, _ in level_map.iter_actors()), Point(2, 1))
		self.assertEqual(next(_ for pos, _ in level_map.iter_actors()).direction, Direction.UP)

		level_map.shift_player((0, -1))
		self.assertEqual(next(pos for pos, _ in level_map.iter_actors()), Point(2, 0))
		self.assertEqual(next(_ for pos, _ in level_map.iter_actors()).direction, Direction.UP)

		level_map.shift_player((0, -1))
		self.assertEqual(next(pos for pos, _ in level_map.iter_actors()), Point(2, 0))
		self.assertEqual(next(_ for pos, _ in level_map.iter_actors()).direction, Direction.UP)

		level_map.shift_player(Direction.LEFT)
		self.assertEqual(next(pos for pos, _ in level_map.iter_actors()), Point(1, 0))
		self.assertEqual(next(_ for pos, _ in level_map.iter_actors()).direction, Direction.LEFT)

		level_map.shift_player(Direction.UP)
		self.assertEqual(next(pos for pos, _ in level_map.iter_actors()), Point(1, 0))
		self.assertEqual(next(_ for pos, _ in level_map.iter_actors()).direction, Direction.UP)
	def should_move_only_on_passable_tiles(self):
		level_map = Map((5, 5))
		level_map.set_tile((2, 1), Terrain(['wall'], passable=False))
		level_map.set_tile((1, 2), Terrain(['grass'], passable=True))
		level_map.add_actor((2, 2), Player('Wanderer', 'rogue'))

		level_map.shift_player((0, -1))
		self.assertEqual(next(pos for pos, _ in level_map.iter_actors()), Point(2, 2))
		self.assertEqual(next(_ for pos, _ in level_map.iter_actors()).direction, Direction.UP)

		level_map.shift_player((-1, 0))
		self.assertEqual(next(pos for pos, _ in level_map.iter_actors()), Point(1, 2))
		self.assertEqual(next(_ for pos, _ in level_map.iter_actors()).direction, Direction.LEFT)
	def should_trigger_event_after_walking_on_a_tile(self):
		class TriggerCallback:
			def __init__(self): self.triggered = False
			def __call__(self): self.triggered = True
		level_map = Map((5, 5))
		level_map.set_tile((2, 1), Terrain(['wall'], passable=False))
		level_map.set_tile((1, 2), Terrain(['grass'], passable=True))
		trigger_callback = TriggerCallback()
		level_map.add_trigger((1, 2), Trigger(trigger_callback))
		level_map.add_actor((2, 2), Player('Wanderer', 'rogue'))
		level_map.shift_player(Direction.LEFT)
		self.assertEqual(next(pos for pos, _ in level_map.iter_actors()), Point(1, 2))
		self.assertTrue(trigger_callback.triggered)
	def should_talk_to_npc(self):
		class TriggerCallback:
			def __init__(self): self.talk = None
			def __call__(self, npc): self.talk = npc.get_message()
		class TriggerSecondCallback:
			def __init__(self): self.talk = None
			def __call__(self, npc): self.talk = npc.get_message()
		level_map = Map((5, 5))
		level_map.set_tile((2, 1), Terrain(['wall'], passable=False))
		level_map.set_tile((1, 2), Terrain(['grass'], passable=True))
		level_map.add_actor((2, 2), Player('Wanderer', 'rogue'))
		trigger_callback = TriggerCallback()
		npc = NPC('Farmer', 'npc', trigger=Trigger(trigger_callback))
		npc.set_message('Howdy!')
		self.assertEqual(npc.get_sprite(), 'npc')
		level_map.add_actor((1, 2), npc)

		level_map.shift_player(Direction.LEFT)
		self.assertEqual(next(pos for pos, _ in level_map.iter_actors()), Point(2, 2))
		self.assertEqual(trigger_callback.talk, 'Howdy!')

		npc.set_message('Howdy again!')
		trigger_second_callback = TriggerSecondCallback()
		npc.set_trigger(Trigger(trigger_second_callback))
		level_map.shift_player(Direction.LEFT)
		self.assertEqual(next(pos for pos, _ in level_map.iter_actors()), Point(2, 2))
		self.assertEqual(trigger_callback.talk, 'Howdy!')
		self.assertEqual(trigger_second_callback.talk, 'Howdy again!')
