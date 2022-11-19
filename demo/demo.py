"""
Demonstration for nanomyth engine API and usage patterns.
Presents in form of a simple and small game.
"""
import os, sys
import textwrap
from pathlib import Path
import json, jsonpickle
import pygame
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import nanomyth
from nanomyth.math import Matrix, Point
from nanomyth.game.savegame import PickleSavefile, JsonpickleSavefile
from nanomyth.game.map import Map, Terrain, Portal, Trigger
from nanomyth.game.game import Game
from nanomyth.game.quest import Quest, ExternalQuestAction
from nanomyth.game.world import World
from nanomyth.game.actor import Player, Direction, NPC
import nanomyth.view.sdl
from nanomyth.view.sdl.tmx import load_tmx_map
from nanomyth.view.sdl.graphml import load_graphml_quest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))
import graphics, manual_content, ui

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

def autosave():
	main_game.get_game().save_to_file(autosavefile, force=True)
	main_game.set_pending_context(
			ui.message_box(engine, resources, 'Autosaved.', font, size=(5, 2))
			)

def farmer_asks_for_help():
	farmer_quest = textwrap.dedent("""\
	Hello there, wanderer!

	Please listen to my story.

	I'm a local farmer growing food for the nearby village. I've been doing this for the last 20 years since I've inherited this farm from my father. This is the only place where farm plants can grow in this desert, so the whole village depends on the crops.

	But some time ago vermins came from nowhere and started to steal growing food, leaving us with just scraps. We cannot survive with what's left, the whole village could starve!

	My fellow dog, Smoke, has been helping me to fight of the vermins, but couple of days ago he disappeared. I'm afraid the worst, that the vermins kidnapped him. Without Smoke, I alone cannot protect this farm. Someone has to find my dog and bring him back!

	Could you please look for him? I would go myself, but someone need to stay here to ward off the vermins.

	I think that vermins are coming from the west of here. I would think they probably live in some sort of cave.

	Godspeed!
	""")
	main_game.set_pending_context(
			ui.conversation(engine, resources, farmer_quest, font)
			)

def hearing_Smoke():
	barking = textwrap.dedent("""\
	You hear barking in the furthest parts of the dungeon.

	It could be Smoke!
	""")
	main_game.set_pending_context(
			ui.conversation(engine, resources, barking, font)
			)

def bringing_Smoke_to_farmer():
	farmer_thanks = textwrap.dedent("""\
	Thank you for bringing my Smoke back!

	Now we can protect our food crops. The village is saved.

	Good luck to you on your adventures!
	""")
	main_game.set_pending_context(
			ui.conversation(engine, resources, farmer_thanks, font)
			)

def Smoke_unknown():
	Smoke_wary = textwrap.dedent("""\
	Bark! Bark!
	
	(The dog seems to be wary of you.)

	(Probably you should step back.)
	""")
	main_game.set_pending_context(
			ui.conversation(engine, resources, Smoke_wary, font)
			)

def Smoke_thanks():
	Smoke_text = textwrap.dedent("""\
	Woof!
	""")
	main_game.set_pending_context(
			ui.conversation(engine, resources, Smoke_text, font)
			)

def finding_Smoke():
	Smoke_is_found = textwrap.dedent("""\
	Woof!
	
	(Smoke appears to be glad to see a person.)

	(He will follow you when you go to the farmer.)
	""")
	main_game.set_pending_context(
			ui.conversation(engine, resources, Smoke_is_found, font)
			)
	Smoke = game.get_world().get_current_map().remove_actor('Smoke')
	farm = game.get_world().get_map('farm')
	farm.add_actor((2, 2), Smoke)

main_map = load_tmx_map(DEMO_ROOTDIR/'home.tmx', engine)
basement_map = manual_content.create_basement_map(engine, resources)
yard_map = load_tmx_map(DEMO_ROOTDIR/'yard.tmx', engine)

game = Game()
game.get_world().add_map('main', main_map)
game.get_world().add_map('basement', basement_map)
game.get_world().add_map('yard', yard_map)
game.get_world().add_map('farm', load_tmx_map(DEMO_ROOTDIR/'farm.tmx', engine))
game.get_world().add_map('cave_entrance', load_tmx_map(DEMO_ROOTDIR/'cave_entrance.tmx', engine))
game.get_world().add_map('cave', load_tmx_map(DEMO_ROOTDIR/'cave.tmx', engine))
quest = load_graphml_quest(DEMO_ROOTDIR/'foodcart.graphml')
game.get_world().add_quest('smoke', quest)

main_game = nanomyth.view.sdl.context.Game(game)
foodcart_quest = manual_content.create_foodcart_quest(
		game, main_game,
		engine, resources, font,
		)
game.get_world().add_quest('foodcart', foodcart_quest)
game.get_world().get_current_map().add_actor((1+2, 1+2), Player('Wanderer', 'rogue', directional_sprites={
	Direction.UP : 'rogue_up',
	Direction.DOWN : 'rogue_down',
	Direction.LEFT : 'rogue_left',
	Direction.RIGHT : 'rogue_right',
	}))
game.register_trigger_action('autosave', autosave)

game.register_trigger_action('farmer_asks_for_help', farmer_asks_for_help)
game.register_trigger_action('hearing_Smoke', hearing_Smoke)
game.register_trigger_action('bringing_Smoke_to_farmer', bringing_Smoke_to_farmer)
game.register_trigger_action('Smoke_unknown', Smoke_unknown)
game.register_trigger_action('Smoke_thanks', Smoke_thanks)
game.register_trigger_action('finding_Smoke', finding_Smoke)

savefiles = [
		JsonpickleSavefile(DEMO_ROOTDIR/'game1.sav'),
		JsonpickleSavefile(DEMO_ROOTDIR/'game2.sav'),
		JsonpickleSavefile(DEMO_ROOTDIR/'game3.sav'),
		]
autosavefile = JsonpickleSavefile(DEMO_ROOTDIR/'auto.sav')

def save_game(savefile, force=False):
	ok = game.save_to_file(savefile, force=force)
	if not ok:
		return ui.message_box(engine, resources, 'Overwrite slot?', font, size=(6, 2),
				on_ok=lambda: save_game_menu.set_pending_context(save_game(savefile, force=True)),
				on_cancel=lambda: (_ for _ in ()).throw(nanomyth.view.sdl.context.Menu.Finished()) # It's just a way to raise Exception from within labmda.
				)
	return ui.message_box(engine, resources, 'Game saved.', font, size=(5, 2))

def load_game(savefile):
	if game.load_from_file(savefile):
		main_menu.set_pending_context(main_game)
	else:
		main_menu_info.set_text('')
		return ui.message_box(engine, resources, 'No such savefile.', font, size=(6, 2))
	raise nanomyth.view.sdl.context.Menu.Finished

save_game_menu = nanomyth.view.sdl.context.Menu(font, on_escape=nanomyth.view.sdl.context.Menu.Finished)
ui.fill_savegame_menu(engine, resources, save_game_menu, 'Save game', save_game, savefiles, font, fixed_font, grey_font)

load_game_menu = nanomyth.view.sdl.context.Menu(font, on_escape=nanomyth.view.sdl.context.Menu.Finished)
ui.fill_savegame_menu(engine, resources, load_game_menu, 'Load game', load_game, savefiles + [autosavefile], font, fixed_font, grey_font)

main_menu = nanomyth.view.sdl.context.Menu(font, on_escape=nanomyth.view.sdl.context.Menu.Finished)
main_menu_info = ui.fill_main_menu(engine, resources, main_menu, main_game,
		save_game_menu, load_game_menu, font, fixed_font, grey_font)
engine.init_context(main_menu)

auto_sequence = None
if sys.argv[1:2] == ['auto']:
	args = sys.argv[2:]
	import autodemo
	save3 = DEMO_ROOTDIR/'game3.sav'
	if save3.exists(): # pragma: no cover -- We need slot 3 to be free.
		os.unlink(str(save3))
	auto_sequence = autodemo.AutoSequence(0.2 if 'slow' in args else 0.05, DEMO_ROOTDIR/'autodemo.txt')
engine.run(custom_update=auto_sequence)
