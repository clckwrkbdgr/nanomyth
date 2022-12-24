import nanomyth.view.sdl
from nanomyth.math import Point, Size, Matrix, Rect

def load_menu_images(engine, resources):
	background = engine.add_image('background', nanomyth.view.sdl.image.Image(resources['background']/'5DragonsBkgds'/'room2.png'))
	background.get_size() # Dummy instruction, only for coverage of otherwise unused method.
	engine.add_image('main_menu_background', background.get_region((160, 40, 160, 120)))

	decor = engine.add_image('Decor', nanomyth.view.sdl.image.TileSetImage(resources['tileset']/'Objects'/'Decor0.png', (8, 22)))
	engine.add_image('info_line_left',   decor.get_tile((0, 10)))
	engine.add_image('info_line_middle', decor.get_tile((1, 10)))
	engine.add_image('info_line_right',  decor.get_tile((2, 10)))

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
	engine.add_image('button_scroll_up', gui.get_tile((10, 0)))
	engine.add_image('button_scroll_up_highlighted', gui.get_tile((5, 1)))
	engine.add_image('button_scroll_down', gui.get_tile((10, 0)))
	engine.add_image('button_scroll_down_highlighted', gui.get_tile((5, 3)))
	engine.add_image('main_panel_topleft',     gui.get_tile((13, 16)))
	engine.add_image('main_panel_top',         gui.get_tile((14, 16)))
	engine.add_image('main_panel_topright',    gui.get_tile((15, 16)))
	engine.add_image('main_panel_left',        gui.get_tile((13, 17)))
	engine.add_image('main_panel_middle',      gui.get_tile((14, 17)))
	engine.add_image('main_panel_right',       gui.get_tile((15, 17)))
	engine.add_image('main_panel_bottomleft',  gui.get_tile((13, 18)))
	engine.add_image('main_panel_bottom',      gui.get_tile((14, 18)))
	engine.add_image('main_panel_bottomright', gui.get_tile((15, 18)))

	button = engine.add_image('Button', nanomyth.view.sdl.image.TileSetImage(resources['tileset']/'Objects'/'Floor.png', (21, 39)))
	engine.add_image('button_off_left',   button.get_tile((4, 10)))
	engine.add_image('button_off_middle', button.get_tile((5, 10)))
	engine.add_image('button_off_right',  button.get_tile((6, 10)))
	engine.add_image('button_on_left',   button.get_tile((4, 4)))
	engine.add_image('button_on_middle', button.get_tile((5, 4)))
	engine.add_image('button_on_right',  button.get_tile((6, 4)))

	engine.add_image('grey_font', nanomyth.view.sdl.image.TileSetImage(resources['font']/'8x8text_darkGrayShadow.png', (12, 14)))
	engine.add_image('white_font', nanomyth.view.sdl.image.TileSetImage(resources['font']/'8x8text_whiteShadow.png', (12, 14)))

def panel(engine, resources, size):
	size = Size(size)
	size = Size(max(size.width, 2), max(size.height, 2))
	panel_widget = nanomyth.view.sdl.widget.PanelWidget(Matrix.from_iterable([
		['main_panel_topleft',     'main_panel_top',         'main_panel_topright',    ],
		['main_panel_left',        'main_panel_middle',      'main_panel_right',       ],
		['main_panel_bottomleft',  'main_panel_bottom',      'main_panel_bottomright', ],
		]), size)
	return panel_widget

def add_info_panel(parent_context, engine, font):
	info_line_pos = Point(
			0,
			engine.get_window_size().height - 8,
			)
	info_line_panel = nanomyth.view.sdl.widget.TileMapWidget(Matrix.from_iterable([
		['info_line_left'] + ['info_line_middle'] * 8 + ['info_line_right'],
		]))
	info_line = nanomyth.view.sdl.widget.TextLineWidget(font)
	parent_context.add_widget(info_line_pos, info_line_panel)
	parent_context.add_widget(info_line_pos, info_line)
	return info_line

def message_box(engine, resources, text, font, size=None, on_ok=None, on_cancel=None):
	size = Size(size)
	size = Size(max(size.width, 2), max(size.height, 2))
	panel_widget = nanomyth.view.sdl.widget.PanelWidget(Matrix.from_iterable([
		['panel_topleft',     'panel_top',         'panel_topright',    ],
		['panel_left',        'panel_middle',      'panel_right',       ],
		['panel_bottomleft',  'panel_bottom',      'panel_bottomright', ],
		]), size)
	dialog = nanomyth.view.sdl.context.MessageBox(text, font, panel_widget, engine,
			text_shift=(4, 4),
			on_ok=on_ok,
			on_cancel=on_cancel,
			)
	tile_size = engine.get_image('panel_middle').get_size()
	dialog.add_button(engine, (
		-tile_size.width * 2 - 2,
		-tile_size.height,
		), nanomyth.view.sdl.widget.ImageWidget(engine.get_image('button_ok')),
		)
	if on_cancel:
		dialog.add_button(engine, (
			-tile_size.width - 2,
			-tile_size.height,
			), nanomyth.view.sdl.widget.ImageWidget(engine.get_image('button_cancel')),
			)
	return dialog

def item_list(engine, resources, normal_font, highlighted_font, caption, items):
	window_size = engine.get_window_size()

	items = [nanomyth.view.sdl.widget.Button(
		nanomyth.view.sdl.widget.MultilineTextWidget(
			normal_font, (window_size.width, 0), item,
			),
		nanomyth.view.sdl.widget.MultilineTextWidget(
			highlighted_font, (window_size.width, 0), item,
			),
		action=action,
		) for item, action in items]

	size = Size(10, 7)
	panel_widget = nanomyth.view.sdl.widget.PanelWidget(Matrix.from_iterable([
		['main_panel_topleft',     'main_panel_top',         'main_panel_topright',    ],
		['main_panel_left',        'main_panel_middle',      'main_panel_right',       ],
		['main_panel_bottomleft',  'main_panel_bottom',      'main_panel_bottomright', ],
		]), size)

	caption_widget = nanomyth.view.sdl.widget.TextLineWidget(highlighted_font, caption)

	dialog = nanomyth.view.sdl.context.ItemList(engine, panel_widget, items,
			caption_widget=caption_widget,
			view_rect=Rect((4, 4, window_size.width - 4, window_size.height - 4 - 12)),
			)

	info_line = add_info_panel(dialog, engine, highlighted_font)
	return dialog

def conversation(engine, resources, text, font, on_ok=None):
	size = Size(10, 7)
	panel_widget = nanomyth.view.sdl.widget.PanelWidget(Matrix.from_iterable([
		['panel_topleft',     'panel_top',         'panel_topright',    ],
		['panel_left',        'panel_middle',      'panel_right',       ],
		['panel_bottomleft',  'panel_bottom',      'panel_bottomright', ],
		]), size)
	window_size = engine.get_window_size()
	dialog = nanomyth.view.sdl.context.TextScreen(text, font, panel_widget, engine,
			text_rect=(4, 4, window_size.width - 4, window_size.height - 8 - 4 - 16),
			)
	tile_size = engine.get_image('panel_middle').get_size()
	dialog.set_scroll_up_button(engine, (
		-tile_size.width * 2 - 2,
		-tile_size.height - 2,
		), nanomyth.view.sdl.widget.Button(
			nanomyth.view.sdl.widget.ImageWidget(engine.get_image('button_scroll_up')),
			nanomyth.view.sdl.widget.ImageWidget(engine.get_image('button_scroll_up_highlighted')),
			),
		)
	dialog._button_up.get_size(engine) # TODO not needed actually, just for coverage.
	dialog.set_scroll_down_button(engine, (
		2,
		-tile_size.height - 2,
		), nanomyth.view.sdl.widget.Button(
			nanomyth.view.sdl.widget.ImageWidget(engine.get_image('button_scroll_down')),
			nanomyth.view.sdl.widget.ImageWidget(engine.get_image('button_scroll_down_highlighted')),
			),
		)
	dialog.add_button(engine, (
		-tile_size.width - 2,
		-tile_size.height,
		), nanomyth.view.sdl.widget.ImageWidget(engine.get_image('button_ok')),
		)
	info_line = add_info_panel(dialog, engine, font)
	return dialog

def fill_main_menu(engine, resources, main_menu, main_game_context, save_function, load_function, font, fixed_font, grey_font):
	main_menu.set_background('main_menu_background')
	main_menu.set_caption_pos((20, 4))
	main_menu.set_caption_text('Nanomyth Demo', fixed_font)

	main_menu_info = nanomyth.view.sdl.widget.TextLineWidget(font)
	main_menu.add_widget((0, 100), main_menu_info)

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

	if len(savefiles) == 4:
		menu.add_menu_item(('Auto', '> Auto'), lambda: handler(savefiles[3]))
	menu.add_menu_item(('Slot 1', '> Slot 1'), lambda: handler(savefiles[0]))
	menu.add_menu_item(('Slot 2', '> Slot 2'), lambda: handler(savefiles[1]))
	menu.add_menu_item(('Slot 3', '> Slot 3'), lambda: handler(savefiles[2]))

	normal = nanomyth.view.sdl.widget.Layout()
	normal.add_widget(nanomyth.view.sdl.widget.TileMapWidget(button_off_tiles))
	normal.add_widget(nanomyth.view.sdl.widget.TextLineWidget(grey_font, 'Back'), (4, 4))
	normal.get_size(engine) # TODO not needed actually, just for coverage.
	highlighted = nanomyth.view.sdl.widget.Layout()
	highlighted.add_widget(nanomyth.view.sdl.widget.TileMapWidget(button_on_tiles))
	highlighted.add_widget(nanomyth.view.sdl.widget.TextLineWidget(font, '> Back'), (4, 4))

	menu.add_menu_item(
			nanomyth.view.sdl.widget.Button(normal, highlighted),
			nanomyth.view.sdl.context.Context.Finished,
			)

	menu.select_item(0)
