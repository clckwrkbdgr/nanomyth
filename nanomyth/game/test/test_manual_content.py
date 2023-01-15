from ...utils import unittest
from ..game import Game
from ..world import World
from ..map import Map, Terrain, Portal, Trigger
from ..actor import Player, Direction, NPC
from ..items import Item, CollectibleItem
from ..quest import Quest, ExternalQuestAction, HistoryMessage

class TestManualContent(unittest.TestCase):
	def create_lab_map(self):
		lab = Map((4, 4))
		lab_map = [[
			Terrain(['wall'], passable=False),
			Terrain(['wall', 'window'], passable=False),
			Terrain(['wall'], passable=False),
			Terrain(['wall'], passable=False),
			], [
			Terrain(['wall'], passable=False),
			Terrain(['floor', 'computer'], passable=False),
			Terrain(['floor', 'teleport']),
			Terrain(['wall'], passable=False),
			], [
			Terrain(['wall'], passable=False),
			Terrain(['floor']),
			Terrain(['floor']),
			Terrain(['wall'], passable=False),
			], [
			Terrain(['wall'], passable=False),
			Terrain(['wall'], passable=False),
			Terrain(['doorway', 'door']),
			Terrain(['wall'], passable=False),
			]]
		for pos, _ in lab.iter_tiles():
			lab.set_tile(pos, lab_map[pos.y][pos.x])

		lab.add_portal((2, 3), Portal('warehouse', (5, 0)))
		return lab
	def create_warehouse_map(self):
		warehouse = Map((10, 10))
		warehouse._tiles.clear(Terrain(['floor']))
		for y in range(0, 10):
			warehouse.set_tile((0, y), Terrain(['wall'], passable=False))
			warehouse.set_tile((9, y), Terrain(['wall'], passable=False))
		for x in range(0, 10):
			warehouse.set_tile((x, 0), Terrain(['wall'], passable=False))
			warehouse.set_tile((x, 9), Terrain(['wall'], passable=False))
		warehouse.set_tile((5, 0), Terrain(['doorway', 'door']))
		warehouse.add_portal((5, 0), Portal('lab', (2, 3)))

		warehouse.add_actor((4, 1), NPC('dummy', 'dummy'))

		warehouse.add_trigger((5, 1), Trigger('first glance'))

		warehouse.add_trigger((5, 2), Trigger('robot platform'))
		warehouse.set_tile((7, 1), Terrain(['floor', 'storage']))
		warehouse.add_trigger((7, 1), Trigger('using_gear_storage'))

		warehouse.add_item((6, 5), Item('wrench', 'wrench'))
		warehouse.add_item((6, 6), CollectibleItem('credits', 'money', 100))
		warehouse.add_item((6, 7), CollectibleItem('credits', 'money', 200))
		return warehouse
	def create_robot_quest(self):
		quest = Quest('robot', "Fix robot", [
			'need gear', 'got gear', 'robot is gone',
			], [
			'robot', 'gear storage',
			], finish_states=['robot is gone'],
			)
		quest.on_state(None, 'robot', ExternalQuestAction('robot_asks_for_help'))
		quest.on_state(None, 'robot', HistoryMessage('Robot asks to fix him.'))
		quest.on_state(None, 'robot', 'need gear')
		quest.on_state('need gear', 'robot', ExternalQuestAction('robot_asks_for_help'))
		quest.on_state('need gear', 'gear storage', 'got gear')
		quest.on_state('need gear', 'gear storage', HistoryMessage('You got a gear from storage.'))
		quest.on_state('need gear', 'gear storage', ExternalQuestAction('getting_gear'))
		quest.on_state('got gear', 'robot', 'robot is gone')
		quest.on_state('got gear', 'robot', HistoryMessage('Robot thanked and left.'))
		quest.on_state('got gear', 'robot', ExternalQuestAction('robot_is_fixed'))

		quest.on_start('update_active_quest_count')
		quest.on_finish('update_active_quest_count')

		return quest
	def create_game(self):
		game = Game()

		lab = self.create_lab_map()
		game.get_world().add_map('lab', lab)
		warehouse = self.create_warehouse_map()
		game.get_world().add_map('warehouse', warehouse)

		lab.add_actor((1, 2), Player('You', 'player', directional_sprites={
			Direction.UP: 'player_up',
			Direction.DOWN: 'player_down',
			Direction.LEFT: 'player_left',
			Direction.RIGHT: 'player_right',
			}))

		game.register_trigger_action('update_active_quest_count', self.update_active_quest_count)
		game.register_trigger_action('first glance', self.first_glance)
		game.register_trigger_action('robot platform', self.open_robot_platform)

		game.get_world().add_quest(self.create_robot_quest())
		game.register_trigger_action('talking_to_robot', self.talking_to_robot)
		game.register_trigger_action('using_gear_storage', self.using_gear_storage)
		game.register_trigger_action('robot_asks_for_help', self.robot_asks_for_help)
		game.register_trigger_action('getting_gear', self.getting_gear)
		game.register_trigger_action('robot_is_fixed', self.robot_is_fixed)

		return game

	def update_active_quest_count(self, *args, **kwargs):
		self.log.append("Active quests: {0}".format(len(self.game.get_world().get_active_quests())))
	def first_glance(self):
		self.log.append("You enter the warehouse.")
	def open_robot_platform(self):
		self.log.append("(Robot emerges from some storage under the floor)")
		self.game.get_world().get_current_map().add_actor((5, 3), NPC('robot', 'robot', trigger=Trigger('talking_to_robot')))
	def talking_to_robot(self, *args):
		self.game.get_world().get_quest('robot').perform_action('robot', trigger_registry=self.game.get_trigger_action)
	def using_gear_storage(self):
		self.game.get_world().get_quest('robot').perform_action('gear storage', trigger_registry=self.game.get_trigger_action)
	def robot_asks_for_help(self):
		self.log.append('My walking mechanism is broken. Could you fetch me some backup gear to fix it?')
	def getting_gear(self):
		self.log.append('(You pick up a gear)')
	def robot_is_fixed(self):
		self.log.append('Thanks! (Robot has gone under floor again)')
		self.game.get_world().get_current_map().remove_actor(self.game.get_world().get_current_map().find_actor('robot'))

	def _player_pos(self):
		return self.game.get_world().get_current_map().find_actor_pos('You')
	def _player(self):
		return self.game.get_world().get_current_map().find_actor('You')
	def setUp(self):
		self.game = self.create_game()
		self.log = []
	def tearDown(self):
		del self.game
	def should_add_content_manually_and_control_game_model_directly(self):
		# Look around.
		self.assertEqual([_.get_images() for _pos, _ in self.game.get_world().get_current_map().iter_tiles()], [
			['wall'], ['wall', 'window'], ['wall'], ['wall'],
			['wall'], ['floor', 'computer'], ['floor', 'teleport'], ['wall'],
			['wall'], ['floor'], ['floor'], ['wall'],
			['wall'], ['wall'], ['doorway', 'door'], ['wall'],
			])
		self.assertEqual([_.get_sprite() for _pos, _ in self.game.get_world().get_current_map().iter_actors()], [
			'player_down',
			])
		self.assertEqual([_.image for _pos, _ in self.game.get_world().get_current_map().iter_items()], [
			])

		# Exit lab.
		self.game.shift_player(Direction.UP) # Bump.
		self.assertEqual(self._player().get_sprite(), 'player_up')
		self.game.shift_player(Direction.LEFT) # Bump.
		self.assertEqual(self._player().get_sprite(), 'player_left')
		self.game.shift_player(Direction.RIGHT)
		self.assertEqual(self._player().get_sprite(), 'player_right')
		self.game.shift_player(Direction.DOWN)
		self.assertEqual(self._player().get_sprite(), 'player_down')
		self.assertEqual(self.game.get_world()._current_map, 'warehouse')
		self.assertEqual(self._player_pos(), (5, 0))

		self.game.shift_player(Direction.DOWN)
		self.assertEqual(self._player_pos(), (5, 1))
		self.assertEqual(self.log[-1], "You enter the warehouse.")

		self.game.shift_player(Direction.LEFT)
		self.assertEqual(self._player_pos(), (5, 1))

		self.game.shift_player(Direction.DOWN)
		self.assertEqual(self._player_pos(), (5, 2))
		self.assertEqual(self.log[-1], "(Robot emerges from some storage under the floor)")

		self.assertFalse(self.game.get_world().get_active_quests())
		self.assertFalse(self.game.get_world().get_quest('robot').is_active())

		self.game.shift_player(Direction.DOWN)
		self.assertEqual(self._player_pos(), (5, 2))
		self.assertEqual(self.log[-2:], [
			"My walking mechanism is broken. Could you fetch me some backup gear to fix it?",
			'Active quests: 1',
			])

		self.assertEqual([_.title for _ in self.game.get_world().get_active_quests()], ['Fix robot'])
		self.assertTrue(self.game.get_world().get_quest('robot').is_active())
		self.assertEqual(self.game.get_world().get_quest('robot').get_last_history_entry(), 'Robot asks to fix him.')

		self.game.shift_player(Direction.RIGHT)
		self.game.shift_player(Direction.RIGHT)
		self.game.shift_player(Direction.UP)
		self.assertEqual(self._player_pos(), (7, 1))
		self.assertEqual(self.log[-2:], [
			"Active quests: 1",
			'(You pick up a gear)',
			])
		self.assertEqual(self.game.get_world().get_quest('robot').get_last_history_entry(), 'You got a gear from storage.')

		self.game.shift_player(Direction.DOWN)
		self.game.shift_player(Direction.DOWN)
		self.game.shift_player(Direction.LEFT)
		self.game.shift_player(Direction.LEFT)
		self.assertEqual(self._player_pos(), (6, 3))
		self.assertEqual(self.log[-2:], [
			"Active quests: 0",
			'Thanks! (Robot has gone under floor again)',
			])
		self.assertEqual(self.game.get_world().get_quest('robot').get_history(), [
			'Robot asks to fix him.',
			'You got a gear from storage.',
			'Robot thanked and left.',
			])
		self.assertFalse(self.game.get_world().get_quest('robot').is_active())
		self.assertFalse(self.game.get_world().get_active_quests())
		self.assertIsNone(self.game.get_world().get_current_map().find_actor('robot'))

		self.game.shift_player(Direction.DOWN)
		self.assertEqual(self._player_pos(), (6, 4))
		self.assertIsNone(self.game.get_world().get_current_map().pick_item(self._player()))
		self.game.shift_player(Direction.DOWN)
		self.assertEqual(self._player_pos(), (6, 5))
		self.assertEqual(self.game.get_world().get_current_map().pick_item(self._player()).name, 'wrench')
		self.assertEqual(self.game.get_world().get_current_map().drop_item(self._player(), next(self._player().iter_inventory())).name, 'wrench')
		self.assertEqual(self.game.get_world().get_current_map().pick_item(self._player()).name, 'wrench')
		self.assertFalse(self.game.get_world().get_current_map().items_at_pos((6, 4)))
		self.assertFalse(self.game.get_world().get_current_map().items_at_pos((6, 5)))

		self.game.shift_player(Direction.DOWN)
		self.assertEqual(self.game.get_world().get_current_map().pick_item(self._player()).name, 'credits')
		self.game.shift_player(Direction.DOWN)
		self.assertEqual(self.game.get_world().get_current_map().pick_item(self._player()).name, 'credits')

		money = list(self._player().iter_inventory())[-1]
		to_drop = money.with_amount(50)
		self.assertEqual(self.game.get_world().get_current_map().drop_item(self._player(), to_drop).amount, 50)
		money = list(self._player().iter_inventory())[-1]
		self.assertEqual(money.amount, 250)
