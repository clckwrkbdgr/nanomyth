import itertools
from ...utils import unittest
from ..map import Map, Terrain, Trigger
from ..items import Item
from ..actor import Player, Direction, NPC
from ..quest import QuestStateChange
from ...math import Point, Size

class TestMap(unittest.TestCase):
	def should_create_map_of_empty_tiles(self):
		level_map = Map((5, 5))
		self.assertEqual(level_map.get_tile((0, 0)).get_images(), [])
		self.assertEqual(level_map.get_size(), Size(5, 5))
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
	def should_place_items(self):
		level_map = Map((5, 5))
		level_map.add_item((2, 2), Item('knife', 'knife'))
		self.assertEqual([(pos, item.get_sprite()) for pos, item in level_map.iter_items()], [(Point(2, 2), 'knife')])
	def should_find_items_by_location(self):
		level_map = Map((5, 5))
		level_map.add_item((2, 2), Item('knife', 'knife'))
		self.assertEqual(level_map.items_at_pos((2, 2))[0].get_sprite(), 'knife')
		self.assertFalse(level_map.items_at_pos((1, 1)))
	def should_remove_items(self):
		level_map = Map((5, 5))
		level_map.add_item((2, 2), Item('knife', 'knife'))
		level_map.remove_item(level_map.items_at_pos((2, 2))[0])
		self.assertFalse(level_map.items_at_pos((2, 2)))
	def should_place_actors(self):
		level_map = Map((5, 5))
		level_map.add_actor((2, 2), Player('Wanderer', 'rogue'))
		self.assertEqual([(pos, player.get_sprite()) for pos, player in level_map.iter_actors()], [(Point(2, 2), 'rogue')])
	def should_find_actors_by_name(self):
		level_map = Map((5, 5))
		level_map.add_actor((2, 2), Player('Wanderer', 'rogue'))
		self.assertEqual(level_map.find_actor('Wanderer').get_sprite(), 'rogue')
		self.assertIsNone(level_map.find_actor('Absent'))
		self.assertEqual(level_map.find_actor_pos('Wanderer'), Point(2, 2))
		self.assertIsNone(level_map.find_actor_pos('Absent'))
	def should_remove_actors(self):
		level_map = Map((5, 5))
		level_map.add_actor((2, 2), Player('Wanderer', 'rogue'))
		level_map.remove_actor(level_map.find_actor('Wanderer'))
		self.assertIsNone(level_map.find_actor('Wanderer'))
	def should_shift_player(self):
		level_map = Map((5, 5))
		player = Player('Wanderer', 'rogue', directional_sprites={
			Direction.UP: 'rogue_up',
			Direction.DOWN: 'rogue_down',
			Direction.LEFT: 'rogue_left',
			Direction.RIGHT: 'rogue_right',
			})
		level_map.add_actor((2, 2), player)

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
		class TriggerRegistry:
			def __init__(self, **callbacks):
				self.registry = dict(**callbacks)
			def __call__(self, name):
				return self.registry[name]
		trigger_callback = TriggerCallback()
		quest_trigger_callback = TriggerCallback()
		trigger_registry = TriggerRegistry(
				trigger=trigger_callback,
				quest_step=quest_trigger_callback,
				)

		class MockQuest:
			def __init__(self):
				self.actions = []
			def perform_action(self, action, trigger_registry):
				trigger_registry(action)()
		class QuestRegistry:
			def __init__(self, **quests):
				self.quests = dict(**quests)
			def __call__(self, name):
				return self.quests[name]
		quest = MockQuest()
		quest_registry = QuestRegistry(quest=quest)

		level_map = Map((5, 5))
		level_map.set_tile((2, 1), Terrain(['wall'], passable=False))
		level_map.set_tile((1, 2), Terrain(['grass'], passable=True))
		level_map.add_trigger((1, 2), Trigger('trigger'))
		level_map.add_actor((2, 2), Player('Wanderer', 'rogue'))
		level_map.add_trigger((0, 2), QuestStateChange('quest', 'quest_step'))

		level_map.shift_player(Direction.LEFT, trigger_registry=trigger_registry)
		self.assertEqual(next(pos for pos, _ in level_map.iter_actors()), Point(1, 2))
		self.assertTrue(trigger_callback.triggered)

		level_map.shift_player(Direction.LEFT, trigger_registry=trigger_registry, quest_registry=quest_registry)
		self.assertEqual(next(pos for pos, _ in level_map.iter_actors()), Point(0, 2))
		self.assertTrue(quest_trigger_callback.triggered)

	def should_talk_to_npc(self):
		class TriggerCallback:
			def __init__(self): self.talk = None
			def __call__(self, npc): self.talk = npc.name
		class TriggerSecondCallback:
			def __init__(self): self.talk = None
			def __call__(self, npc): self.talk = npc.name
		class QuestTriggerCallback:
			def __init__(self): self.talk = False
			def __call__(self): self.talk = True
		trigger_callback = TriggerCallback()
		trigger_second_callback = TriggerSecondCallback()
		quest_trigger_callback = QuestTriggerCallback()
		class TriggerRegistry:
			def __init__(self, **callbacks):
				self.registry = dict(**callbacks)
			def __call__(self, name):
				return self.registry[name]
		trigger_registry = TriggerRegistry(
				trigger=trigger_callback,
				second=trigger_second_callback,
				quest_step=quest_trigger_callback,
				)

		class MockQuest:
			def __init__(self):
				self.actions = []
			def perform_action(self, action, trigger_registry):
				trigger_registry(action)()
		class QuestRegistry:
			def __init__(self, **quests):
				self.quests = dict(**quests)
			def __call__(self, name):
				return self.quests[name]
		quest = MockQuest()
		quest_registry = QuestRegistry(quest=quest)

		level_map = Map((5, 5))
		level_map.set_tile((2, 1), Terrain(['wall'], passable=False))
		level_map.set_tile((1, 2), Terrain(['grass'], passable=True))
		level_map.add_actor((2, 2), Player('Wanderer', 'rogue'))
		npc = NPC('Farmer', 'npc', trigger=Trigger('trigger'))
		self.assertEqual(npc.get_sprite(), 'npc')
		level_map.add_actor((1, 2), npc)

		level_map.shift_player(Direction.LEFT, trigger_registry=trigger_registry)
		self.assertEqual(next(pos for pos, _ in level_map.iter_actors()), Point(2, 2))
		self.assertEqual(trigger_callback.talk, 'Farmer')

		npc.name = 'IT Switcher'
		npc.set_trigger(Trigger('second'))
		level_map.shift_player(Direction.LEFT, trigger_registry=trigger_registry)
		self.assertEqual(next(pos for pos, _ in level_map.iter_actors()), Point(2, 2))
		self.assertEqual(trigger_callback.talk, 'Farmer')
		self.assertEqual(trigger_second_callback.talk, 'IT Switcher')

		npc.name = 'Quest Giver'
		npc.set_trigger(QuestStateChange('quest', 'quest_step'))
		level_map.shift_player(Direction.LEFT, trigger_registry=trigger_registry, quest_registry=quest_registry)
		self.assertEqual(next(pos for pos, _ in level_map.iter_actors()), Point(2, 2))
		self.assertTrue(quest_trigger_callback.talk)
	def should_pick_items(self):
		level_map = Map((5, 5))
		level_map.add_actor((2, 2), Player('Wanderer', 'rogue'))
		player = level_map.find_actor('Wanderer')
		level_map.add_item((2, 2), Item('sword', 'sword'))
		level_map.add_item((2, 2), Item('shield', 'shield'))
		sword, shield = level_map.items_at_pos((2, 2))
		level_map.add_item((2, 3), Item('bag of gold', 'bag'))
		bag_of_gold = level_map.items_at_pos((2, 3))[0]
		level_map.add_item((2, 1), Item('golden key', 'key'))
		golden_key = level_map.items_at_pos((2, 1))[0]

		self.assertEqual(level_map.pick_item(player, item=bag_of_gold), bag_of_gold)
		self.assertEqual(list(player.iter_inventory()), [bag_of_gold])
		self.assertFalse(level_map.items_at_pos((2, 3)))

		self.assertEqual(level_map.pick_item(player, at_pos=(2, 1)), golden_key)
		self.assertEqual(list(player.iter_inventory()), [bag_of_gold, golden_key])
		self.assertFalse(level_map.items_at_pos((2, 1)))

		self.assertEqual(level_map.pick_item(player), shield)
		self.assertEqual(list(player.iter_inventory()), [bag_of_gold, golden_key, shield])
		self.assertEqual(level_map.pick_item(player), sword)
		self.assertEqual(list(player.iter_inventory()), [bag_of_gold, golden_key, shield, sword])
		self.assertEqual([_.name for _ in player.iter_inventory()], ['bag of gold', 'golden key', 'shield', 'sword'])
		self.assertFalse(level_map.items_at_pos((2, 2)))

		self.assertIsNone(level_map.pick_item(player))
	def should_drop_items(self):
		level_map = Map((5, 5))
		level_map.add_actor((2, 2), Player('Wanderer', 'rogue'))
		player = level_map.find_actor('Wanderer')
		bag_of_gold = Item('bag of gold', 'bag')
		golden_key = Item('golden key', 'key')
		player.add_item(bag_of_gold)
		player.add_item(golden_key)
		level_map.add_item((2, 2), Item('sword', 'sword'))

		self.assertEqual(level_map.drop_item(player, golden_key, at_pos=(2, 1)), golden_key)
		self.assertEqual([_.name for _ in level_map.items_at_pos((2, 1))], ['golden key'])
		self.assertEqual(list(player.iter_inventory()), [bag_of_gold])
		self.assertEqual(level_map.drop_item(player, bag_of_gold), bag_of_gold)
		self.assertEqual([_.name for _ in level_map.items_at_pos((2, 2))], ['sword', 'bag of gold'])
		self.assertEqual(list(player.iter_inventory()), [])
