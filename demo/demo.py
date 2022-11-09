"""
Demonstration for nanomyth engine API and usage patterns.
Presents in form of a simple and small game.
"""
import os, sys
from pathlib import Path
import json, jsonpickle
import pygame
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import nanomyth
from nanomyth.math import Matrix, Point
from nanomyth.game.map import Map, Terrain, Portal
from nanomyth.game.world import World
from nanomyth.game.actor import Player, Direction
import nanomyth.view.sdl
from nanomyth.view.sdl.tmx import load_tmx_map
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))
import graphics, maps, ui

resources = graphics.download_resources()
DEMO_ROOTDIR = Path(__file__).parent
SAVEFILE = DEMO_ROOTDIR/'game.sav'

print('Demo app for the capabilities of the engine.')
print('Press <ESC> to close.')
sys.stdout.flush()

main_menu = nanomyth.view.sdl.context.Menu(on_escape=nanomyth.view.sdl.context.Menu.Finished)
engine = nanomyth.view.sdl.SDLEngine((640, 480), main_menu,
		scale=4,
		window_title='Nanomyth Demo',
		)

rogue = engine.add_image('Rogue', nanomyth.view.sdl.image.TileSetImage(resources['tileset']/'Commissions'/'Rogue.png', (4, 4)))
engine.add_image('rogue', rogue.get_tile((0, 0)))
engine.add_image('rogue_down', rogue.get_tile((0, 0)))
engine.add_image('rogue_left', rogue.get_tile((0, 1)))
engine.add_image('rogue_right', rogue.get_tile((0, 2)))
engine.add_image('rogue_up', rogue.get_tile((0, 3)))

main_map = load_tmx_map(DEMO_ROOTDIR/'home.tmx', engine)
basement_map = maps.create_basement_map(engine, resources)
desert_map = load_tmx_map(DEMO_ROOTDIR/'desert_entrance.tmx', engine)

world = World()
world.add_map('main', main_map)
world.add_map('basement', basement_map)
world.add_map('desert', desert_map)

main_game = nanomyth.view.sdl.context.Game(world)
main_game.get_current_map().add_actor((1+2, 1+2), Player('rogue', directional_sprites={
	Direction.UP : 'rogue_up',
	Direction.DOWN : 'rogue_down',
	Direction.LEFT : 'rogue_left',
	Direction.RIGHT : 'rogue_right',
	}))

def save_game():
	savedata = jsonpickle.encode(main_game.get_world())
	SAVEFILE.write_text(json.dumps(json.loads(savedata), indent=1, sort_keys=True))
	main_menu_info.set_text('Game saved.')

def load_game():
	if not SAVEFILE.exists():
		return
	savedata = SAVEFILE.read_text()
	main_game.load_world(jsonpickle.decode(savedata))
	main_menu_info.set_text('Game loaded.')

main_menu_info = ui.fill_main_menu(engine, resources, main_menu, main_game, save_game, load_game)

auto_sequence = None
if sys.argv[1:] == ['auto']:
	import autodemo
	auto_sequence = autodemo.AutoSequence(0.2, [
		'up', # Test menu.
		'down',
		'down',
		'down',
		'down',
		'up', 'up', 'up', # Navigate back to the "Play"
		'return', # Play.
		'up', 'up', # Test obstacles.
		'left', # Test movement and direction.
		'left', # Obstacle.
		'down', 'down', # To the basement.
		'up', 'down', # Stuck on stairs.
		'left', 'left', 'up', 'down', # Wandering around the basement.
		'escape', # To main menu.
		'down', 'return', # Save game.
		'.', '.', '.', # Just a pause.
		'up', 'return', # Back to playing.
		'right', # Go up.
		'right', 'right', 'right', 'right', # Right into the wall.
		'down', # Exit home and into the desert.
		'left', 'up', # Stuck in doorway.
		'down', 'up', # Re-entering doorway...
		'up', 'down', # and back to the desert.
		'down', 'down', 'down', 'right', 'right', 'down', 'down', 'down', 'left', 'left', 'up', # Go to the portal.
		'.', '.', '.', # Just a pause.
		'escape', # To main menu.
		'down', 'down', 'return', # Load game.
		'.', '.', '.', # Just a pause.
		'escape', # Exit game.
		])
engine.run(custom_update=auto_sequence)
