import textwrap
from nanomyth.math import Point
from nanomyth.game.map import Map, Terrain, Portal
from nanomyth.game.quest import Quest, ExternalQuestAction, HistoryMessage
import nanomyth.view.sdl
import ui

def load_basement_tiles(engine, resources):
	extra_tiles = engine.add_image('ExtraTile', nanomyth.view.sdl.image.TileSetImage(resources['tileset']/'Objects'/'Tile.png', (8, 4)))
	engine.add_image('stairs_up', extra_tiles.get_tile((4, 3)))

	floors = engine.add_image('Floor', nanomyth.view.sdl.image.TileSetImage(resources['tileset']/'Objects'/'Floor.png', (21, 39)))
	engine.add_image('ground_floor', floors.get_tile((1, 25)))

	walls = engine.add_image('Wall', nanomyth.view.sdl.image.TileSetImage(resources['tileset']/'Objects'/'Wall.png', (20, 51)))
	engine.add_image('ground_wall_topleft', walls.get_tile((7, 24)))
	engine.add_image('ground_wall_top', walls.get_tile((8, 24)))
	engine.add_image('ground_wall_topright', walls.get_tile((9, 24)))
	engine.add_image('ground_wall_right', walls.get_tile((7, 25)))
	engine.add_image('ground_wall_bottomright', walls.get_tile((9, 26)))
	engine.add_image('ground_wall_bottom', walls.get_tile((8, 24)))
	engine.add_image('ground_wall_bottomleft', walls.get_tile((7, 26)))
	engine.add_image('ground_wall_left', walls.get_tile((7, 25)))
	engine.add_image('ground_wall_center', walls.get_tile((8, 25)))

def create_basement_map(engine, resources):
	load_basement_tiles(engine, resources)

	basement_map = Map((7, 7))
	shift = Point(2, 2)
	basement_map.set_tile(shift + (0, 0), Terrain(['ground_wall_topleft'], passable=False))
	basement_map.set_tile(shift + (1, 0), Terrain(['ground_wall_top'], passable=False))
	basement_map.set_tile(shift + (2, 0), Terrain(['ground_wall_topright'], passable=False))
	basement_map.set_tile(shift + (0, 1), Terrain(['ground_wall_left'], passable=False))
	basement_map.set_tile(shift + (1, 1), Terrain(['ground_floor'], passable=True))
	basement_map.set_tile(shift + (2, 1), Terrain(['ground_wall_right', 'stairs_up'], passable=True))
	basement_map.set_tile(shift + (3, 1), Terrain([], passable=False)) # To close stairs tile from the right side.
	basement_map.set_tile(shift + (0, 2), Terrain(['ground_wall_bottomleft'], passable=False))
	basement_map.set_tile(shift + (1, 2), Terrain(['ground_wall_bottom'], passable=False))
	basement_map.set_tile(shift + (2, 2), Terrain(['ground_wall_bottomright'], passable=False))
	basement_map.add_portal(shift + (2, 1), Portal('main', (2, 4)))
	return basement_map

def create_foodcart_quest(game, main_game, engine, resources, font):
	foodcart_quest = Quest('foodcart', "All flesh is grass", [
		'pushing cart', 'cart is free', 'trader is gone',
		], [
		'trader', 'grass',
		], finish_states=['trader is gone'],
		)
	def foodcart_trader_step(trader): game.get_world().get_quest('foodcart').perform_action('trader', trigger_registry=game.get_trigger_action)
	def foodcart_grass_step(): game.get_world().get_quest('foodcart').perform_action('grass', trigger_registry=game.get_trigger_action)
	def trader_asks_for_help():
		trader_quest = textwrap.dedent("""\
		My food cart is stuck in this grass. Could you push from the back?
		""")
		main_game.set_pending_context(
				ui.conversation(engine, resources, trader_quest, font)
				)
	foodcart_quest.on_state(None, 'trader', ExternalQuestAction('trader_asks_for_help'))
	foodcart_quest.on_state(None, 'trader', HistoryMessage('Trader asks to help him move the cart.'))
	foodcart_quest.on_state(None, 'trader', 'pushing cart')
	foodcart_quest.on_state('pushing cart', 'trader', ExternalQuestAction('trader_asks_for_help'))
	foodcart_quest.on_state('pushing cart', 'grass', 'cart is free')
	def pushing_cart():
		push_cart = textwrap.dedent("""\
		You are trying to push cart with all the strength when you notice that one of the wheels is entangled in a grass knot.

		You cut the grass and the wheel is free.
		""")
		main_game.set_pending_context(
				ui.conversation(engine, resources, push_cart, font)
				)
	foodcart_quest.on_state('pushing cart', 'grass', HistoryMessage('The cart is free. You should tell this to trader.'))
	foodcart_quest.on_state('pushing cart', 'grass', ExternalQuestAction('pushing_cart'))
	def cart_is_free():
		trader_thanks = textwrap.dedent("""\
		Thanks! I'm going to the market to sell these crops from the farm that's east from here. Farmer there could use your help too.
		""")
		main_game.set_pending_context(
				ui.conversation(engine, resources, trader_thanks, font)
				)
		game.get_world().get_current_map().remove_actor('foodcart')
		game.get_world().get_current_map().remove_actor('Trader')
	foodcart_quest.on_state('cart is free', 'trader', 'trader is gone')
	foodcart_quest.on_state('cart is free', 'trader', ExternalQuestAction('cart_is_free'))

	game.register_trigger_action('talking_to_trader', foodcart_trader_step)
	game.register_trigger_action('push_foodcart', foodcart_grass_step)
	game.register_trigger_action('trader_asks_for_help', trader_asks_for_help)
	game.register_trigger_action('pushing_cart', pushing_cart)
	game.register_trigger_action('cart_is_free', cart_is_free)

	return foodcart_quest
