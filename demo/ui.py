import nanomyth.view.sdl
from nanomyth.math import Point, Size, Matrix

def load_menu_images(engine, resources):
	background = engine.add_image('background', nanomyth.view.sdl.image.Image(resources['background']/'5DragonsBkgds'/'room2.png'))
	background.get_size() # Dummy instruction, only for coverage of otherwise unused method.
	engine.add_image('main_menu_background', background.get_region((160, 40, 160, 120)))

	gui = engine.add_image('GUI', nanomyth.view.sdl.image.TileSetImage(resources['tileset']/'GUI'/'GUI0.png', (16, 19)))
	engine.add_image('panel_topleft',     gui.get_tile((1, 7)))
	engine.add_image('panel_top',         gui.get_tile((2, 7)))
	engine.add_image('panel_topright',    gui.get_tile((3, 7)))
	engine.add_image('panel_left',        gui.get_tile((1, 8)))
	engine.add_image('panel_middle',      gui.get_tile((2, 8)))
	engine.add_image('panel_right',       gui.get_tile((3, 8)))
	engine.add_image('panel_bottomleft',  gui.get_tile((1, 9)))
	engine.add_image('panel_bottom',      gui.get_tile((2, 9)))
	engine.add_image('panel_bottomright', gui.get_tile((3, 9)))
	engine.add_image('button_ok', gui.get_tile((10, 2)))
	engine.add_image('button_cancel', gui.get_tile((11, 2)))

	button = engine.add_image('Button', nanomyth.view.sdl.image.TileSetImage(resources['tileset']/'Objects'/'Floor.png', (21, 39)))
	engine.add_image('button_off_left',   button.get_tile((4, 10)))
	engine.add_image('button_off_middle', button.get_tile((5, 10)))
	engine.add_image('button_off_right',  button.get_tile((6, 10)))
	engine.add_image('button_on_left',   button.get_tile((4, 4)))
	engine.add_image('button_on_middle', button.get_tile((5, 4)))
	engine.add_image('button_on_right',  button.get_tile((6, 4)))

	engine.add_image('grey_font', nanomyth.view.sdl.image.TileSetImage(resources['font']/'8x8text_darkGrayShadow.png', (12, 14)))
	engine.add_image('white_font', nanomyth.view.sdl.image.TileSetImage(resources['font']/'8x8text_whiteShadow.png', (12, 14)))

def message_box(engine, resources, text, font, size=None, on_ok=None, on_cancel=None):
	size = Size(size)
	size = Size(max(size.width, 2), max(size.height, 2))
	panel_tiles = []
	for row_index in range(size.height):
		vert_pos = 'top' if row_index == 0 else ('bottom' if row_index == size.height - 1 else '')
		middle_pos = 'middle' if vert_pos == '' else vert_pos
		panel_tiles.append([
			'panel_{0}left'.format(vert_pos)
			] + [
			'panel_{0}'.format(middle_pos)
			] * (size.width - 2) + [
			'panel_{0}right'.format(vert_pos)
			])
	panel_tiles = Matrix.from_iterable(panel_tiles)
	panel_widget = nanomyth.view.sdl.widget.TileMapWidget(panel_tiles, (0, 0))
	dialog = nanomyth.view.sdl.context.MessageBox(text, font,
			panel_widget=panel_widget,
			text_shift=(4, 4),
			)
	tile_size = engine.get_image('panel_middle').get_size()
	dialog.add_button(nanomyth.view.sdl.widget.ImageWidget(engine.get_image('button_ok'), (0, 0)), (
		tile_size.width * (size.width - 2) - 2,
		tile_size.height * (size.height - 1),
		))
	if on_cancel:
		dialog.add_button(nanomyth.view.sdl.widget.ImageWidget(engine.get_image('button_cancel'), (0, 0)), (
			tile_size.width * (size.width - 1) - 2,
			tile_size.height * (size.height - 1),
			))
	return dialog

def fill_main_menu(engine, resources, main_menu, main_game_context, save_function, load_function, font, fixed_font, grey_font):
	main_menu.set_background('main_menu_background')
	main_menu.set_caption_pos((20, 4))
	main_menu.set_caption_text('Nanomyth Demo', fixed_font)

	main_menu_info = nanomyth.view.sdl.widget.TextLineWidget(font, (0, 100))
	main_menu.add_widget(main_menu_info)

	button_off_tiles = Matrix.from_iterable([
		['button_off_left', 'button_off_middle', 'button_off_right'],
		])
	button_on_tiles = Matrix.from_iterable([
		['button_on_left', 'button_on_middle', 'button_on_right'],
		])
	main_menu.set_button_group_topleft((100, 20))
	main_menu.set_button_height(20)
	main_menu.set_button_caption_shift((4, 4))
	main_menu.set_button_widget_template(nanomyth.view.sdl.widget.TileMapWidget, button_off_tiles, font=grey_font)
	main_menu.set_highlighted_button_widget_template(nanomyth.view.sdl.widget.TileMapWidget, button_on_tiles, font=font)

	main_menu.add_menu_item(('Play', '> Play'), main_game_context)
	main_menu.add_menu_item(('Save', '> Save'), save_function)
	main_menu.add_menu_item(('Load', '> Load'), load_function)
	main_menu.add_menu_item('Exit', nanomyth.view.sdl.context.Context.Finished)

	main_menu.select_item(0)
	return main_menu_info

def fill_savegame_menu(engine, resources, menu, title, handler, savefiles, font, fixed_font, grey_font):
	menu.set_background('main_menu_background')
	menu.set_caption_pos((50, 10))
	menu.set_caption_text(title)

	button_off_tiles = Matrix.from_iterable([
		['button_off_left', 'button_off_middle', 'button_off_middle', 'button_off_right'],
		])
	button_on_tiles = Matrix.from_iterable([
		['button_on_left', 'button_on_middle', 'button_on_middle', 'button_on_right'],
		])
	menu.set_button_group_topleft((50, 20))
	menu.set_button_height(20)
	menu.set_button_caption_shift((4, 4))
	menu.set_button_widget_template(nanomyth.view.sdl.widget.TileMapWidget, button_off_tiles, font=grey_font)
	menu.set_highlighted_button_widget_template(nanomyth.view.sdl.widget.TileMapWidget, button_on_tiles, font=font)

	menu.add_menu_item(('Slot 1', '> Slot 1'), lambda: handler(savefiles[0]))
	menu.add_menu_item(('Slot 2', '> Slot 2'), lambda: handler(savefiles[1]))
	menu.add_menu_item(('Slot 3', '> Slot 3'), lambda: handler(savefiles[2]))
	#menu.add_menu_item(('Back', '< Back'), nanomyth.view.sdl.context.Context.Finished)
	menu.add_menu_item(
			nanomyth.view.sdl.widget.MenuItem(
				(50, 80),
				nanomyth.view.sdl.widget.TileMapWidget(button_off_tiles, (0, 0)),
				nanomyth.view.sdl.widget.TextLineWidget(grey_font, (0, 0), 'Back'),
				button_highlighted=nanomyth.view.sdl.widget.TileMapWidget(button_on_tiles, (0, 0)),
				caption_highlighted=nanomyth.view.sdl.widget.TextLineWidget(font, (0, 0), '> Back'),
				caption_shift=(4, 4),
				), nanomyth.view.sdl.context.Context.Finished)

	menu.select_item(0)
