from pyfakefs import fake_filesystem_unittest
from ...utils import unittest
from ..game import Game
from ..world import World
from ..map import Map, Terrain, Portal, Trigger
from ..actor import Player, Direction
from ..items import Item
from ..quest import Quest
from .. import savegame

def _create_game():
	game = Game()
	world = World()
	home, desert = Map((5, 5)), Map((5, 5))
	home.set_tile((0, 0), Terrain(['floor']))
	desert.set_tile((0, 0), Terrain(['desert']))
	game.get_world().add_map('home', home)
	game.get_world().add_map('desert', desert)
	home.add_actor((2, 2), Player('Wanderer', 'rogue'))
	home.add_item((2, 1), Item('knife', 'knife'))
	home.add_portal((2, 1), Portal('desert', (1, 2)))
	home.add_trigger((1, 2), Trigger('trigger'))
	quest = Quest('my_quest', 'MyQuest', ['foo'], ['a'])
	game.get_world().add_quest(quest)
	return game

class TestGame(unittest.TestCase):
	def should_load_new_world(self):
		class Callback:
			def __init__(self): self.data = []
			def __call__(self, *params): self.data.append(params)
		on_change_map = Callback()

		game = _create_game()
		game.on_change_map(on_change_map)
		game.get_world().get_current_map()._tiles.set_cell((0, 0), None)
		game.load_world(_create_game().get_world())
		self.assertEqual(
				game.get_world().get_current_map().get_tile((0, 0)).get_images(),
				['floor'],
				)
		self.assertEqual(on_change_map.data, [(game.get_world().get_current_map(),)])
	def should_have_global_registry_for_triggers(self):
		class TriggerCallback:
			def __init__(self): self.triggered = False
			def __call__(self): self.triggered = True
		trigger_callback = TriggerCallback()

		game = _create_game()
		game.register_trigger_action('trigger', trigger_callback)
		game.shift_player(Direction.LEFT)
		self.assertTrue(trigger_callback.triggered)

class TestSaveGame(fake_filesystem_unittest.TestCase):
	def setUp(self):
		self.setUpPyfakefs(modules_to_reload=[savegame])
	def assertWorldsEqual(self, actual, expected):
		self.assertEqual(actual._current_map, expected._current_map)
		self.assertEqual(set(actual._maps.keys()), set(expected._maps.keys()))
		self.assertEqual(
				actual._maps['home']._tiles.tostring(transformer=lambda _:str([_.get_images(), _.passable])),
				expected._maps['home']._tiles.tostring(transformer=lambda _:str([_.get_images(), _.passable])),
				)
	def should_save_and_load_game(self):
		game = _create_game()
		savefile = savegame.JsonpickleSavefile('/game.sav')
		self.assertFalse(savefile.exists())
		self.assertFalse(game.load_from_file.__wrapped__(game, savefile))

		expected_world = game._world

		self.assertTrue(game.save_to_file.__wrapped__(game, savefile))
		self.assertTrue(savefile.exists())
		self.assertTrue(game.load_from_file.__wrapped__(game, savefile))
		self.assertWorldsEqual(game.get_world(), expected_world)

		game.get_world().get_map('home').set_tile((0, 0), Terrain(['desert']))
		self.assertFalse(game.save_to_file.__wrapped__(game, savefile))
		self.assertTrue(game.load_from_file.__wrapped__(game, savefile))
		self.assertWorldsEqual(game.get_world(), expected_world)

		game.get_world().get_map('home').set_tile((0, 0), Terrain(['desert']))
		expected_world.get_map('home').set_tile((0, 0), Terrain(['desert']))
		self.assertTrue(game.save_to_file.__wrapped__(game, savefile, force=True))
		self.assertTrue(game.load_from_file.__wrapped__(game, savefile))
		self.assertWorldsEqual(game.get_world(), expected_world)
