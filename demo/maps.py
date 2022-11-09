from nanomyth.math import Point
from nanomyth.game.map import Map, Terrain, Portal
import nanomyth.view.sdl

def load_basement_tiles(engine, resources):
	extra_tiles = engine.add_image('ExtraTile', nanomyth.view.sdl.image.TileSetImage(resources['tileset']/'Objects'/'Tile.png', (8, 4)))
	engine.add_image('stairs_up', extra_tiles.get_tile((4, 3)))

	floors = engine.add_image('Floor', nanomyth.view.sdl.image.TileSetImage(resources['tileset']/'Objects'/'Floor.png', (21, 39)))
	engine.add_image('ground_floor', floors.get_tile((1, 25)))

	walls = engine.add_image('Wall', nanomyth.view.sdl.image.TileSetImage(resources['tileset']/'Objects'/'Wall.png', (20, 51)))
	engine.add_image('ground_wall_topleft', walls.get_tile((7, 24)))
	engine.add_image('ground_wall_top', walls.get_tile((8, 24)))
	engine.add_image('ground_wall_topright', walls.get_tile((9, 24)))
	engine.add_image('ground_wall_right', walls.get_tile((7, 25)))
	engine.add_image('ground_wall_bottomright', walls.get_tile((9, 26)))
	engine.add_image('ground_wall_bottom', walls.get_tile((8, 24)))
	engine.add_image('ground_wall_bottomleft', walls.get_tile((7, 26)))
	engine.add_image('ground_wall_left', walls.get_tile((7, 25)))
	engine.add_image('ground_wall_center', walls.get_tile((8, 25)))

def create_basement_map(engine, resources):
	load_basement_tiles(engine, resources)

	basement_map = Map((7, 7))
	shift = Point(2, 2)
	basement_map.set_tile(shift + (0, 0), Terrain(['ground_wall_topleft'], passable=False))
	basement_map.set_tile(shift + (1, 0), Terrain(['ground_wall_top'], passable=False))
	basement_map.set_tile(shift + (2, 0), Terrain(['ground_wall_topright'], passable=False))
	basement_map.set_tile(shift + (0, 1), Terrain(['ground_wall_left'], passable=False))
	basement_map.set_tile(shift + (1, 1), Terrain(['ground_floor'], passable=True))
	basement_map.set_tile(shift + (2, 1), Terrain(['ground_wall_right', 'stairs_up'], passable=True))
	basement_map.set_tile(shift + (3, 1), Terrain([], passable=False)) # To close stairs tile from the right side.
	basement_map.set_tile(shift + (0, 2), Terrain(['ground_wall_bottomleft'], passable=False))
	basement_map.set_tile(shift + (1, 2), Terrain(['ground_wall_bottom'], passable=False))
	basement_map.set_tile(shift + (2, 2), Terrain(['ground_wall_bottomright'], passable=False))
	basement_map.add_portal(shift + (2, 1), Portal('main', (2, 4)))
	return basement_map
