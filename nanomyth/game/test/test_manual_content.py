from ...utils import unittest
from ..game import Game
from ..world import World
from ..map import Map, Terrain, Portal, Trigger
from ..actor import Player, Direction
from ..items import Item
from ..quest import Quest

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
		for pos in lab.tiles.keys():
			lab.set_tile(pos, lab_map[pos.y][pos.x])

		lab.add_portal((2, 3), Portal('warehouse', (5, 0)))
		return lab
	def create_warehouse_map(self):
		warehouse = Map((10, 10))
		for y in range(0, 10):
			warehouse.set_tile((0, y), Terrain(['wall']))
			warehouse.set_tile((9, y), Terrain(['wall']))
		for x in range(0, 10):
			warehouse.set_tile((x, 0), Terrain(['wall']))
			warehouse.set_tile((x, 9), Terrain(['wall']))
		warehouse.set_tile((5, 0), Terrain(['doorway', 'door']))

		warehouse.add_portal((5, 0), Portal('lab', (2, 3)))
		return warehouse
	def create_game(self):
		game = Game()

		lab = self.create_lab_map()
		game.get_world().add_map('lab', lab)
		warehouse = self.create_warehouse_map()
		game.get_world().add_map('warehouse', warehouse)

		lab.add_actor((1, 2), Player('You', 'player'))
		return game

	def should_add_content_manually_and_control_game_model_directly(self):
		game = self.create_game()

		# Exit lab.
		game.shift_player(Direction.UP) # Bump.
		game.shift_player(Direction.LEFT) # Bump.
		game.shift_player(Direction.RIGHT)
		game.shift_player(Direction.DOWN)
		self.assertEqual(game.get_world().current_map, 'warehouse')
		player_pos = game.get_world().get_current_map().find_actor_pos('You')
		self.assertEqual(player_pos, (5, 0))
