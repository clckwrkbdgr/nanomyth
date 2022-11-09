"""
Demonstration for nanomyth engine API and usage patterns.
Presents in form of a simple and small game.
"""
import os, sys
from pathlib import Path
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
import graphics

resources = graphics.download_resources()
DEMO_ROOTDIR = Path(__file__).parent

print('Demo app for the capabilities of the engine.')
print('Press <ESC> to close.')
sys.stdout.flush()

main_menu = nanomyth.view.sdl.context.Menu(on_escape=nanomyth.view.sdl.context.Menu.Finished)
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
engine.add_image('doorway', doors.get_tile((6, 0)))
doors_opened = engine.add_image('Door_Opened', nanomyth.view.sdl.image.TileSetImage(resources['tileset']/'Objects'/'Door1.png', (8, 6)))
engine.add_image('door_opened', doors_opened.get_tile((0, 0)))
extra_tiles = engine.add_image('ExtraTile', nanomyth.view.sdl.image.TileSetImage(resources['tileset']/'Objects'/'Tile.png', (8, 4)))
engine.add_image('empty_way', extra_tiles.get_tile((0, 2)))
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
engine.add_image('desert', floors.get_tile((1, 22)))
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

rogue = engine.add_image('Rogue', nanomyth.view.sdl.image.TileSetImage(resources['tileset']/'Commissions'/'Rogue.png', (4, 4)))
engine.add_image('rogue', rogue.get_tile((0, 0)))
engine.add_image('rogue_down', rogue.get_tile((0, 0)))
engine.add_image('rogue_left', rogue.get_tile((0, 1)))
engine.add_image('rogue_right', rogue.get_tile((0, 2)))
engine.add_image('rogue_up', rogue.get_tile((0, 3)))

main_map = Map((7, 7))
main_map.set_tile((1+0, 1+0), Terrain(['wall_topleft'], passable=False))
main_map.set_tile((1+1, 1+0), Terrain(['wall_top', 'window',], passable=False))
main_map.set_tile((1+2, 1+0), Terrain(['wall_top'], passable=False))
main_map.set_tile((1+3, 1+0), Terrain(['wall_top', 'window',], passable=False))
main_map.set_tile((1+4, 1+0), Terrain(['wall_topright'], passable=False))
main_map.set_tile((1+0, 1+1), Terrain(['wall_left'], passable=False))
main_map.set_tile((1+1, 1+1), Terrain(['floor_topleft', 'chair',], passable=False))
main_map.set_tile((1+2, 1+1), Terrain(['floor_top', 'table',], passable=False))
main_map.set_tile((1+3, 1+1), Terrain(['floor_topright', 'shelf',], passable=False))
main_map.set_tile((1+4, 1+1), Terrain(['wall_right'], passable=False))
main_map.set_tile((1+0, 1+2), Terrain(['wall_left'], passable=False))
main_map.set_tile((1+1, 1+2), Terrain(['floor_left']))
main_map.set_tile((1+2, 1+2), Terrain(['floor_center', 'carpet_topleft',]))
main_map.set_tile((1+3, 1+2), Terrain(['floor_right', 'carpet_topright',]))
main_map.set_tile((1+4, 1+2), Terrain(['wall_right'], passable=False))
main_map.set_tile((1+0, 1+3), Terrain(['wall_left'], passable=False))
main_map.set_tile((1+1, 1+3), Terrain(['floor_bottomleft', 'bed',], passable=False))
main_map.set_tile((1+2, 1+3), Terrain(['floor_bottom', 'carpet_bottomleft',]))
main_map.set_tile((1+3, 1+3), Terrain(['floor_bottomright', 'carpet_bottomright',]))
main_map.set_tile((1+4, 1+3), Terrain(['wall_right'], passable=False))
main_map.set_tile((1+0, 1+4), Terrain(['wall_bottomleft'], passable=False))
main_map.set_tile((1+1, 1+4), Terrain(['wall_bottom'], passable=False))
main_map.set_tile((1+2, 1+4), Terrain(['wall_bottom'], passable=False))
main_map.set_tile((1+3, 1+4), Terrain(['empty_way', 'doorway', 'door_opened',]))
main_map.set_tile((1+4, 1+4), Terrain(['wall_bottomright'], passable=False))
main_map.add_portal((1+3, 1+4), Portal('desert', (4, 0)))
main_map.add_actor((1+2, 1+2), Player('rogue', directional_sprites={
	Direction.UP : 'rogue_up',
	Direction.DOWN : 'rogue_down',
	Direction.LEFT : 'rogue_left',
	Direction.RIGHT : 'rogue_right',
	}))

desert_map = load_tmx_map(DEMO_ROOTDIR/'desert_entrance.tmx', engine)

world = World()
world.add_map('main', main_map)
world.add_map('desert', desert_map)

main_game = nanomyth.view.sdl.context.Game(world)

background = engine.add_image('background', nanomyth.view.sdl.image.Image(resources['background']/'5DragonsBkgds'/'room2.png'))

gui = engine.add_image('gui', nanomyth.view.sdl.image.TileSetImage(resources['tileset']/'GUI'/'GUI0.png', (16, 19)))
engine.add_image('button_off_left',   floors.get_tile((4, 10)))
engine.add_image('button_off_middle', floors.get_tile((5, 10)))
engine.add_image('button_off_right',  floors.get_tile((6, 10)))
engine.add_image('button_on_left',   floors.get_tile((4, 4)))
engine.add_image('button_on_middle', floors.get_tile((5, 4)))
engine.add_image('button_on_right',  floors.get_tile((6, 4)))

font_mapping = '~1234567890-+!@#$%^&*()_={}[]|\\:;"\'<,>.?/ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz' + '\x7f'*(3+5*12+7) + ' '
grey_font_image = engine.add_image('grey_font', nanomyth.view.sdl.image.TileSetImage(resources['font']/'8x8text_darkGrayShadow.png', (12, 14)))
white_font_image = engine.add_image('white_font', nanomyth.view.sdl.image.TileSetImage(resources['font']/'8x8text_whiteShadow.png', (12, 14)))
fixed_font = nanomyth.view.sdl.font.FixedWidthFont(white_font_image, font_mapping)
grey_font = nanomyth.view.sdl.font.ProportionalFont(grey_font_image, font_mapping)
font = nanomyth.view.sdl.font.ProportionalFont(white_font_image, font_mapping, space_width=3, transparent_color=255)
main_menu_background = engine.add_image('main_menu_background', background.get_region((160, 40, 160, 120)))
main_menu.add_widget(nanomyth.view.sdl.widget.ImageWidget('main_menu_background', (0, 0)))
main_menu_caption = nanomyth.view.sdl.widget.TextLineWidget(fixed_font, (40, 0))
main_menu_caption.set_text('Nanomyth Demo')
main_menu.add_widget(main_menu_caption)
button_off_tiles = Matrix.from_iterable([
	['button_off_left', 'button_off_middle', 'button_off_right'],
	])
button_on_tiles = Matrix.from_iterable([
	['button_on_left', 'button_on_middle', 'button_on_right'],
	])
main_menu.add_menu_item(
		nanomyth.view.sdl.widget.MenuItem(
			(100, 20),
			nanomyth.view.sdl.widget.TileMapWidget(button_off_tiles, (0, 0)),
			nanomyth.view.sdl.widget.TextLineWidget(grey_font, (0, 0), 'Play'),
			button_highlighted=nanomyth.view.sdl.widget.TileMapWidget(button_on_tiles, (0, 0)),
			caption_highlighted=nanomyth.view.sdl.widget.TextLineWidget(font, (0, 0), '> Play'),
			caption_shift=(4, 4),
			), main_game)
main_menu.add_menu_item(
		nanomyth.view.sdl.widget.MenuItem(
			(100, 40),
			nanomyth.view.sdl.widget.TileMapWidget(button_off_tiles, (0, 0)),
			nanomyth.view.sdl.widget.TextLineWidget(grey_font, (0, 0), 'Exit'),
			button_highlighted=nanomyth.view.sdl.widget.TileMapWidget(button_on_tiles, (0, 0)),
			caption_highlighted=nanomyth.view.sdl.widget.TextLineWidget(font, (0, 0), '> Exit'),
			caption_shift=(4, 4),
			), nanomyth.view.sdl.context.Context.Finished)
main_menu.select_item(0)

auto_sequence = None
if sys.argv[1:] == ['auto']:
	import autodemo
	auto_sequence = autodemo.AutoSequence(0.2, [
		'up', # Test menu.
		'down',
		'down',
		'up', # Navigate back to the "Play"
		'return', # Play.
		'up', # Test obstacles.
		'left', # Test movement and direction.
		'left', # Obstacle.
		'down', # Obstacle.
		'right', 'right', 'right', 'right', # Right into the wall.
		'down', 'down', # Exit home and into the desert.
		'left', 'up', # Stuck in doorway.
		'down', 'up', # Re-entering doorway...
		'up', 'down', # and back to the desert.
		'down', 'down', 'down', 'right', 'right', 'down', 'down', 'down', 'left', 'left', 'up', # Go to the portal.
		'.', '.', '.', # Just a pause.
		'escape', # To main menu.
		'escape', # Exit game.
		])
engine.run(custom_update=auto_sequence)
