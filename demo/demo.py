import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import nanomyth
import nanomyth.view.sdl
import graphics

graphics.download_dawnlike_tileset()

print('Press <ESC> to close.', file=sys.stdout)
sys.stdout.flush()

engine = nanomyth.view.sdl.SDLEngine((640, 480), window_title='Nanomyth Demo')
engine.run()
