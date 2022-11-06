"""
Demonstration for nanomyth engine API and usage patterns.
Presents in form of a simple and small game.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pathlib import Path
import pygame
import nanomyth
from nanomyth.math import Matrix
from nanomyth.game.map import Map, Terrain
import nanomyth.view.sdl
import graphics

resources = graphics.download_resources()

print('Demo app for the capabilities of the engine.')
print('Press <ESC> to close.')
sys.stdout.flush()

class MainMenu(nanomyth.view.sdl.context.Context):
	def __init__(self, game_context):
		super().__init__()
		self.game_context = game_context
	def update(self, control_name):
		if control_name == 'escape':
			raise self.Finished()
		elif control_name == 'space':
			return self.game_context

main_game = nanomyth.view.sdl.context.Context()
main_menu = MainMenu(main_game)
engine = nanomyth.view.sdl.SDLEngine((640, 480), main_menu,
		scale=4,
		window_title='Nanomyth Demo',
		)
decor = engine.add_image('Decor', nanomyth.view.sdl.image.TileSetImage(resources['tileset']/'Objects'/'Decor0.png', (8, 22)))
engine.add_image('empty', decor.get_tile((7, 21)))
engine.add_image('wall', decor.get_tile((3, 18)))
engine.add_image('window', decor.get_tile((0, 1)))
engine.add_image('chair', decor.get_tile((3, 7)))
engine.add_image('table', decor.get_tile((4, 7)))
engine.add_image('shelf', decor.get_tile((1, 4)))
engine.add_image('bed', decor.get_tile((1, 9)))
engine.add_image('carpet_topleft', decor.get_tile((0, 14)))
engine.add_image('carpet_topright', decor.get_tile((2, 14)))
engine.add_image('carpet_bottomleft', decor.get_tile((0, 16)))
engine.add_image('carpet_bottomright', decor.get_tile((2, 16)))
doors = engine.add_image('Door', nanomyth.view.sdl.image.TileSetImage(resources['tileset']/'Objects'/'Door0.png', (8, 6)))
engine.add_image('door', doors.get_tile((0, 0)))
floors = engine.add_image('Floor', nanomyth.view.sdl.image.TileSetImage(resources['tileset']/'Objects'/'Floor.png', (21, 39)))
engine.add_image('floor_topleft', floors.get_tile((0, 6)))
engine.add_image('floor_top', floors.get_tile((1, 6)))
engine.add_image('floor_topright', floors.get_tile((2, 6)))
engine.add_image('floor_right', floors.get_tile((2, 7)))
engine.add_image('floor_bottomright', floors.get_tile((2, 8)))
engine.add_image('floor_bottom', floors.get_tile((1, 8)))
engine.add_image('floor_bottomleft', floors.get_tile((0, 8)))
engine.add_image('floor_left', floors.get_tile((0, 7)))
engine.add_image('floor_center', floors.get_tile((1, 7)))
walls = engine.add_image('Wall', nanomyth.view.sdl.image.TileSetImage(resources['tileset']/'Objects'/'Wall.png', (20, 51)))
engine.add_image('wall_topleft', walls.get_tile((0, 6)))
engine.add_image('wall_top', walls.get_tile((1, 6)))
engine.add_image('wall_topright', walls.get_tile((2, 6)))
engine.add_image('wall_right', walls.get_tile((0, 7)))
engine.add_image('wall_bottomright', walls.get_tile((2, 8)))
engine.add_image('wall_bottom', walls.get_tile((1, 6)))
engine.add_image('wall_bottomleft', walls.get_tile((0, 8)))
engine.add_image('wall_left', walls.get_tile((0, 7)))
engine.add_image('wall_center', walls.get_tile((1, 7)))

main_map = Map()
main_map.set_tile((0, 0), Terrain(['wall_topleft']))
main_map.set_tile((1, 0), Terrain(['wall_top', 'window',]))
main_map.set_tile((2, 0), Terrain(['wall_top']))
main_map.set_tile((3, 0), Terrain(['wall_top', 'window',]))
main_map.set_tile((4, 0), Terrain(['wall_topright']))
main_map.set_tile((0, 1), Terrain(['wall_left']))
main_map.set_tile((1, 1), Terrain(['floor_topleft', 'chair',]))
main_map.set_tile((2, 1), Terrain(['floor_top', 'table',]))
main_map.set_tile((3, 1), Terrain(['floor_topright', 'shelf',]))
main_map.set_tile((4, 1), Terrain(['wall_right']))
main_map.set_tile((0, 2), Terrain(['wall_left']))
main_map.set_tile((1, 2), Terrain(['floor_left']))
main_map.set_tile((2, 2), Terrain(['floor_center', 'carpet_topleft',]))
main_map.set_tile((3, 2), Terrain(['floor_right', 'carpet_topright',]))
main_map.set_tile((4, 2), Terrain(['wall_right']))
main_map.set_tile((0, 3), Terrain(['wall_left']))
main_map.set_tile((1, 3), Terrain(['floor_bottomleft', 'bed',]))
main_map.set_tile((2, 3), Terrain(['floor_bottom', 'carpet_bottomleft',]))
main_map.set_tile((3, 3), Terrain(['floor_bottomright', 'carpet_bottomright',]))
main_map.set_tile((4, 3), Terrain(['wall_right']))
main_map.set_tile((0, 4), Terrain(['wall_bottomleft']))
main_map.set_tile((1, 4), Terrain(['wall_bottom']))
main_map.set_tile((2, 4), Terrain(['wall_bottom']))
main_map.set_tile((3, 4), Terrain(['wall_bottom', 'door',]))
main_map.set_tile((4, 4), Terrain(['wall_bottomright']))

main_game.add_widget(nanomyth.view.sdl.widget.LevelMapWidget(main_map, (0, 0)))

background = engine.add_image('background', nanomyth.view.sdl.image.Image(resources['background']/'5DragonsBkgds'/'room2.png'))
main_menu_background = background.get_region((160, 40, 160, 120))
main_menu.add_widget(nanomyth.view.sdl.widget.ImageWidget(main_menu_background, (0, 0)))

engine.run()
