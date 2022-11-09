import nanomyth.view.sdl
from nanomyth.math import Point, Matrix

def load_menu_images(engine, resources):
	background = engine.add_image('background', nanomyth.view.sdl.image.Image(resources['background']/'5DragonsBkgds'/'room2.png'))

	gui = engine.add_image('GUI', nanomyth.view.sdl.image.TileSetImage(resources['tileset']/'Objects'/'Floor.png', (21, 39)))
	engine.add_image('button_off_left',   gui.get_tile((4, 10)))
	engine.add_image('button_off_middle', gui.get_tile((5, 10)))
	engine.add_image('button_off_right',  gui.get_tile((6, 10)))
	engine.add_image('button_on_left',   gui.get_tile((4, 4)))
	engine.add_image('button_on_middle', gui.get_tile((5, 4)))
	engine.add_image('button_on_right',  gui.get_tile((6, 4)))

	grey_font_image = engine.add_image('grey_font', nanomyth.view.sdl.image.TileSetImage(resources['font']/'8x8text_darkGrayShadow.png', (12, 14)))
	white_font_image = engine.add_image('white_font', nanomyth.view.sdl.image.TileSetImage(resources['font']/'8x8text_whiteShadow.png', (12, 14)))

def fill_main_menu(engine, resources, main_menu, main_game_context):
	load_menu_images(engine, resources)
	background = engine.get_image('background')
	grey_font_image = engine.get_image('grey_font')
	white_font_image = engine.get_image('white_font')

	font_mapping = '~1234567890-+!@#$%^&*()_={}[]|\\:;"\'<,>.?/ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz' + '\x7f'*(3+5*12+7) + ' '
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
				), main_game_context)
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
	return main_menu
