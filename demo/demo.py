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
grey_font = nanomyth.view.sdl.font.ProportionalFont(engine.get_image('grey_font'), font_mapping, space_width=1)
font = nanomyth.view.sdl.font.ProportionalFont(engine.get_image('white_font'), font_mapping, space_width=4, transparent_color=255)

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
	info_line.set_text('Autosaved')

def update_active_quest_count(quest=None):
	if quest:
		quest = game.get_world().get_quest(quest)
		if quest.is_active():
			info_line.set_text('Quest started: {0}'.format(quest.title))
		else:
			info_line.set_text('Quest finished: {0}'.format(quest.title))

def show_dialog(dialog_message, **params):
	main_game.set_pending_context(
			ui.conversation(engine, resources, dialog_message, font)
			)

def portal_actor(actor, dest_map, dest_map_x, dest_map_y, **params):
	Smoke = game.get_world().get_current_map().remove_actor(actor)
	farm = game.get_world().get_map(dest_map)
	farm.add_actor((int(dest_map_x), int(dest_map_y)), Smoke)

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
quest = load_graphml_quest(DEMO_ROOTDIR/'smoke.graphml')
quest.on_start('update_active_quest_count')
quest.on_finish('update_active_quest_count')
game.get_world().add_quest(quest)

main_game = nanomyth.view.sdl.context.Game(game)
main_game.map_widget.get_size(engine) # TODO not needed actually, just for coverage.
foodcart_quest = manual_content.create_foodcart_quest(
		game, main_game,
		engine, resources, font,
		)
foodcart_quest.on_start('update_active_quest_count')
foodcart_quest.on_finish('update_active_quest_count')
game.get_world().add_quest(foodcart_quest)
game.get_world().get_current_map().add_actor((1+2, 1+2), Player('Wanderer', 'rogue', directional_sprites={
	Direction.UP : 'rogue_up',
	Direction.DOWN : 'rogue_down',
	Direction.LEFT : 'rogue_left',
	Direction.RIGHT : 'rogue_right',
	}))
game.register_trigger_action('autosave', autosave)
game.register_trigger_action('show_dialog', show_dialog)
game.register_trigger_action('portal_actor', portal_actor)
game.register_trigger_action('update_active_quest_count', update_active_quest_count)

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
	info_line.set_text('Game saved')
	return ui.message_box(engine, resources, 'Game saved.', font, size=(5, 2))

def load_game(savefile):
	if game.load_from_file(savefile):
		main_menu.set_pending_context(main_game)
	else:
		main_menu_info.set_text('')
		return ui.message_box(engine, resources, 'No such savefile.', font, size=(6, 2))
	info_line.set_text('Game loaded')
	raise nanomyth.view.sdl.context.Menu.Finished

save_game_menu = nanomyth.view.sdl.context.Menu(font, on_escape=nanomyth.view.sdl.context.Menu.Finished)
ui.fill_savegame_menu(engine, resources, save_game_menu, 'Save game', save_game, savefiles, font, fixed_font, grey_font)

load_game_menu = nanomyth.view.sdl.context.Menu(font, on_escape=nanomyth.view.sdl.context.Menu.Finished)
ui.fill_savegame_menu(engine, resources, load_game_menu, 'Load game', load_game, savefiles + [autosavefile], font, fixed_font, grey_font)

main_ui_panel = ui.panel(engine, resources, (3, 7))
main_ui_panel_pos = Point(
		engine.get_window_size().width - main_ui_panel.get_size(engine).width,
		0,
		)
main_ui_text = """\
[Q]uests
"""
main_ui_text = nanomyth.view.sdl.context.MultilineTextWidget(font,
		size=main_ui_panel.get_size(engine) - (4+4, 4+4),
		text=main_ui_text,
		)
main_game.add_widget(main_ui_panel_pos, main_ui_panel)
main_game.add_widget(main_ui_panel_pos + (4, 4), main_ui_text)
update_active_quest_count()

class ShowQuestDetails:
	def __init__(self, quest):
		self.quest = quest
	def __call__(self):
		text = self.quest.title + '\n\n'
		text += '\n'.join('- {0}'.format(_) for _ in self.quest.get_history())
		return ui.conversation(engine, resources, text, font)

def show_quest_list():
	items = [(
		'* {0}\n    - {1}'.format(quest.title, quest.get_last_history_entry()),
		ShowQuestDetails(quest),
		) for quest in game.get_world().get_active_quests()]
	return ui.item_list(engine, resources, grey_font, font, 'Active quests:', items)
main_game.bind_key('q', show_quest_list)

info_line = ui.add_info_panel(main_game, engine, font)

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
