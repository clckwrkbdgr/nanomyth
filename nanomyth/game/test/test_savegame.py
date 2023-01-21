from pyfakefs import fake_filesystem_unittest
from ...utils import unittest
from .. import savegame
from ...game.world import World
from ...game.map import Map, Terrain, Portal
from ...game.actor import Player, Direction

class TestSavefile(fake_filesystem_unittest.TestCase):
	def setUp(self):
		self.setUpPyfakefs(modules_to_reload=[savegame])
	def _create_world(self):
		world = World()

		foo_map = Map((2, 2))
		foo_map.set_tile((0, 0), Terrain(['ground'], passable=True))
		foo_map.set_tile((1, 0), Terrain(['wall'], passable=False))
		foo_map.add_portal((0, 1), Portal('bar', (2, 2)))
		world.add_map('foo', foo_map)

		bar_map = Map((3, 3))
		bar_map.set_tile((0, 0), Terrain(['grass'], passable=True))
		world.add_map('bar', bar_map)

		foo_map.add_actor((0, 0), Player('Wanderer', 'rogue', directional_sprites={
			Direction.UP : 'rogue_up',
			Direction.DOWN : 'rogue_down',
			Direction.LEFT : 'rogue_left',
			Direction.RIGHT : 'rogue_right',
			}))

		return world
	def assertWorldsEqual(self, actual, expected):
		self.assertEqual(actual._current_map, expected._current_map)
		self.assertEqual(set(actual._maps.keys()), set(expected._maps.keys()))
		self.assertEqual(
				actual._maps['foo']._tiles.tostring(transformer=lambda _:str([_.get_images(), _.passable])),
				expected._maps['foo']._tiles.tostring(transformer=lambda _:str([_.get_images(), _.passable])),
				)
		self.assertEqual(
				[(_.pos, _.obj._entrance_pos, _.obj._dest_map) for _ in actual._maps['foo']._portals],
				[(_.pos, _.obj._entrance_pos, _.obj._dest_map) for _ in expected._maps['foo']._portals],
				)
		self.assertEqual(
				[(_.pos, _.obj._default_sprite, _.obj._direction, _.obj._directional_sprites) for _ in actual._maps['foo']._actors],
				[(_.pos, _.obj._default_sprite, _.obj._direction, _.obj._directional_sprites) for _ in expected._maps['foo']._actors],
				)

		self.assertEqual(
				actual._maps['bar']._tiles.tostring(transformer=lambda _:str([_.get_images(), _.passable])),
				expected._maps['bar']._tiles.tostring(transformer=lambda _:str([_.get_images(), _.passable])),
				)
		self.assertEqual(
				[(_.pos, _._entrance_pos, _._dest_map) for _ in actual._maps['bar']._portals],
				[(_.pos, _._entrance_pos, _._dest_map) for _ in expected._maps['bar']._portals],
				)
		self.assertEqual(
				[(_.pos, _.actor.default_sprite, _.actor.direction, _.actor.directional_sprites) for _ in actual._maps['bar']._actors],
				[(_.pos, _.actor.default_sprite, _.actor.direction, _.actor.directional_sprites) for _ in expected._maps['bar']._actors],
				)

	def should_save_and_load_using_jsonpickle(self):
		world = self._create_world()
		savefile = savegame.JsonpickleSavefile('/game.sav')
		self.assertFalse(savefile.exists())
		self.assertIsNone(savefile.load())
		savefile.save(world)
		self.assertTrue(savefile.exists())
		restored = savefile.load()
		self.assertWorldsEqual(restored, world)
	def should_save_and_load_using_pickle(self):
		world = self._create_world()
		savefile = savegame.PickleSavefile('/game.sav')
		self.assertFalse(savefile.exists())
		self.assertIsNone(savefile.load())
		savefile.save(world)
		self.assertTrue(savefile.exists())
		restored = savefile.load()
		self.assertWorldsEqual(restored, world)
