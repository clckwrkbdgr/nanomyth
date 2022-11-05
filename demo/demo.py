import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pathlib import Path
import pygame
import nanomyth
import nanomyth.view.sdl
import graphics

tileset_root = Path(graphics.download_dawnlike_tileset())

print('Press <ESC> to close.', file=sys.stdout)
sys.stdout.flush()

class Map:
	def __init__(self):
		self.decor = nanomyth.view.sdl.image.Image(tileset_root/'Objects'/'Decor0.png')
	def draw(self, window):
		sprite = self.decor._data.subsurface(pygame.Rect(0, 0, 16*5, 16*5))
		sprite = pygame.transform.scale(sprite, (16*5*4, 16*5*4))
		window.blit(sprite, pygame.Rect(0, 0, 16*5*4, 16*5*4))

engine = nanomyth.view.sdl.SDLEngine((640, 480), window_title='Nanomyth Demo')
engine.widgets.append(Map())
engine.run()
