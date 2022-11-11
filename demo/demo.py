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
from nanomyth.game.savegame import PickleSavefile, JsonpickleSavefile
from nanomyth.game.map import Map, Terrain, Portal
from nanomyth.game.world import World
from nanomyth.game.actor import Player, Direction
import nanomyth.view.sdl
from nanomyth.view.sdl.tmx import load_tmx_map
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))
import graphics, maps, ui

resources = graphics.download_resources()
DEMO_ROOTDIR = Path(__file__).parent

print('Demo app for the capabilities of the engine.')
print('Press <ESC> to close.')
sys.stdout.flush()

engine = nanomyth.view.sdl.SDLEngine((640, 480),
		scale=4,
		window_title='Nanomyth Demo',
		)

ui.load_menu_images(engine, resources)

font_mapping = '~1234567890-+!@#$%^&*()_={}[]|\\:;"\'<,>.?/ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz' + '\x7f'*(3+5*12+7) + ' '
fixed_font = nanomyth.view.sdl.font.FixedWidthFont(engine.get_image('white_font'), font_mapping)
grey_font = nanomyth.view.sdl.font.ProportionalFont(engine.get_image('grey_font'), font_mapping)
font = nanomyth.view.sdl.font.ProportionalFont(engine.get_image('white_font'), font_mapping, space_width=3, transparent_color=255)

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

savefiles = [
		JsonpickleSavefile(DEMO_ROOTDIR/'game1.sav'),
		JsonpickleSavefile(DEMO_ROOTDIR/'game2.sav'),
		JsonpickleSavefile(DEMO_ROOTDIR/'game3.sav'),
		]

def save_game(savefile, force=False):
	ok = main_game.save_to_file(savefile, force=force)
	if not ok:
		return ui.message_box(engine, resources, 'Overwrite slot?', font, size=(6, 2),
				on_ok=lambda: save_game_menu.set_pending_context(save_game(savefile, force=True)),
				on_cancel=lambda: (_ for _ in ()).throw(nanomyth.view.sdl.context.Menu.Finished()) # It's just a way to raise Exception from within labmda.
				)
	return ui.message_box(engine, resources, 'Game saved.', font, size=(5, 2))

def load_game(savefile):
	if main_game.load_from_file(savefile):
		main_menu.set_pending_context(main_game)
	else:
		main_menu_info.set_text('')
		return ui.message_box(engine, resources, 'No such savefile.', font, size=(6, 2))
	raise nanomyth.view.sdl.context.Menu.Finished

save_game_menu = nanomyth.view.sdl.context.Menu(font, on_escape=nanomyth.view.sdl.context.Menu.Finished)
ui.fill_savegame_menu(engine, resources, save_game_menu, 'Save game', save_game, savefiles, font, fixed_font, grey_font)

load_game_menu = nanomyth.view.sdl.context.Menu(font, on_escape=nanomyth.view.sdl.context.Menu.Finished)
ui.fill_savegame_menu(engine, resources, load_game_menu, 'Load game', load_game, savefiles, font, fixed_font, grey_font)

main_menu = nanomyth.view.sdl.context.Menu(font, on_escape=nanomyth.view.sdl.context.Menu.Finished)
main_menu_info = ui.fill_main_menu(engine, resources, main_menu, main_game,
		save_game_menu, load_game_menu, font, fixed_font, grey_font)
engine.init_context(main_menu)

auto_sequence = None
if sys.argv[1:] == ['auto']:
	import autodemo
	save3 = os.path.join(os.path.dirname(__file__), 'game3.sav')
	if os.path.exists(save3): # pragma: no cover -- We need slot 3 to be free.
		os.unlink(save3)
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
		'left', 'left', 'up', 'down', 'left', # Wandering around the basement.
		'escape', # To main menu.
		'down', 'return', 'return', # Save game on existing slot.
		'.', '.', '.', # Just a pause.
		'escape', # Do not overwrite.
		'.', '.', '.', # Just a pause.
		'return', # Again confirmation...
		'.', '.', '.', # Just a pause.
		'return', # Now overwrite save.
		'.', '.', '.', # Just a pause.
		'return', 'escape', 'up', 'return', # Back to playing.
		'right', # Go up.
		'right', 'right', 'right', 'right', # Right into the wall.
		'down', # Exit home and into the desert.
		'left', 'up', # Stuck in doorway.
		'down', 'up', # Re-entering doorway...
		'up', 'down', # and back to the desert.
		'down', 'down', 'down', 'right', 'right', 'down', 'down', 'down', 'left', 'left', 'up', # Go to the portal.
		'.', '.', '.', # Just a pause.
		'escape', # To main menu.
		'down', 'down', 'return', # Load game screen.
		'down', 'down', 'return', # No such savefile.
		'.', '.', '.', # Just a pause.
		'escape', 'up', 'up', 'return', # Load previous save.
		'.', '.', '.', # Just a pause.
		'right', 'up', 'right', # Exit the basement again.
		'.', '.', '.', # Just a pause.
		'escape', # To main menu.
		'escape', # Exit game.
		])
engine.run(custom_update=auto_sequence)
