import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pathlib import Path
import pygame
import nanomyth
from nanomyth.math import Matrix
import nanomyth.view.sdl
import graphics

tileset_root = Path(graphics.download_dawnlike_tileset())

print('Demo app for the capabilities of the engine.')
print('Press <ESC> to close.')
sys.stdout.flush()

engine = nanomyth.view.sdl.SDLEngine((640, 480),
		scale=4,
		window_title='Nanomyth Demo',
		)
decor = engine.add_image('Decor', nanomyth.view.sdl.image.TileSetImage(tileset_root/'Objects'/'Decor0.png', (8, 22)))
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
doors = engine.add_image('Door', nanomyth.view.sdl.image.TileSetImage(tileset_root/'Objects'/'Door0.png', (8, 6)))
engine.add_image('door', doors.get_tile((0, 0)))
floors = engine.add_image('Floor', nanomyth.view.sdl.image.TileSetImage(tileset_root/'Objects'/'Floor.png', (21, 39)))
engine.add_image('floor_topleft', floors.get_tile((0, 6)))
engine.add_image('floor_top', floors.get_tile((1, 6)))
engine.add_image('floor_topright', floors.get_tile((2, 6)))
engine.add_image('floor_right', floors.get_tile((2, 7)))
engine.add_image('floor_bottomright', floors.get_tile((2, 8)))
engine.add_image('floor_bottom', floors.get_tile((1, 8)))
engine.add_image('floor_bottomleft', floors.get_tile((0, 8)))
engine.add_image('floor_left', floors.get_tile((0, 7)))
engine.add_image('floor_center', floors.get_tile((1, 7)))
walls = engine.add_image('Wall', nanomyth.view.sdl.image.TileSetImage(tileset_root/'Objects'/'Wall.png', (20, 51)))
engine.add_image('wall_topleft', walls.get_tile((0, 6)))
engine.add_image('wall_top', walls.get_tile((1, 6)))
engine.add_image('wall_topright', walls.get_tile((2, 6)))
engine.add_image('wall_right', walls.get_tile((0, 7)))
engine.add_image('wall_bottomright', walls.get_tile((2, 8)))
engine.add_image('wall_bottom', walls.get_tile((1, 6)))
engine.add_image('wall_bottomleft', walls.get_tile((0, 8)))
engine.add_image('wall_left', walls.get_tile((0, 7)))
engine.add_image('wall_center', walls.get_tile((1, 7)))


terrain_tilemap = Matrix.from_iterable([
	['wall_topleft', 'wall_top', 'wall_top',  'wall_top', 'wall_topright'],
	['wall_left', 'floor_topleft',  'floor_top', 'floor_topright',  'wall_right'],
	['wall_left', 'floor_left',  'floor_center',   'floor_right',    'wall_right'],
	['wall_left', 'floor_bottomleft',    'floor_bottom',   'floor_bottomright',    'wall_right'],
	['wall_bottomleft', 'wall_bottom',   'wall_bottom',  'wall_bottom',   'wall_bottomright'],
	])
objects_tilemap = Matrix.from_iterable([
	['empty', 'window', 'empty',  'window', 'empty'],
	['empty', 'chair',  'table', 'shelf',  'empty'],
	['empty', 'empty',  'carpet_topleft',   'carpet_topright',    'empty'],
	['empty', 'bed',    'carpet_bottomleft',   'carpet_bottomright',    'empty'],
	['empty', 'empty',   'empty',  'door',   'empty'],
	])
engine.widgets.append(nanomyth.view.sdl.widget.TileMapWidget(terrain_tilemap, (0, 0)))
engine.widgets.append(nanomyth.view.sdl.widget.TileMapWidget(objects_tilemap, (0, 0)))
engine.run()
