import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pathlib import Path
import pygame
import nanomyth
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
decor = nanomyth.view.sdl.image.TileSetImage(tileset_root/'Objects'/'Decor0.png', (8, 22))
decor_tile = decor.get_tile((1, 4))
image = nanomyth.view.sdl.widget.ImageWidget(decor_tile, (0, 0))
engine.widgets.append(image)
engine.run()
