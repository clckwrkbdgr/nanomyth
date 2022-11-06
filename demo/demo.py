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
engine.add_image('floor', decor.get_tile((7, 21)))
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

tilemap = Matrix.from_iterable([
	['wall', 'window', 'wall',  'window', 'wall'],
	['wall', 'chair',  'table', 'shelf',  'wall'],
	['wall', 'floor',  'carpet_topleft',   'carpet_topright',    'wall'],
	['wall', 'bed',    'carpet_bottomleft',   'carpet_bottomright',    'wall'],
	['wall', 'wall',   'wall',  'wall',   'wall'],
	])
for pos in tilemap:
	tile = nanomyth.view.sdl.widget.ImageWidget(engine.get_image(tilemap.cell(pos)), pos * 16)
	engine.widgets.append(tile)
engine.run()
