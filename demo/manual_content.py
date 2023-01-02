import textwrap
from nanomyth.math import Point
from nanomyth.game.map import Map, Terrain, Portal
from nanomyth.game.quest import Quest, ExternalQuestAction, HistoryMessage
import nanomyth.view.sdl
import ui

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
		game.get_world().get_current_map().remove_actor(game.get_world().get_current_map().find_actor('foodcart'))
		game.get_world().get_current_map().remove_actor(game.get_world().get_current_map().find_actor('Trader'))
	foodcart_quest.on_state('cart is free', 'trader', 'trader is gone')
	foodcart_quest.on_state('cart is free', 'trader', ExternalQuestAction('cart_is_free'))

	game.register_trigger_action('talking_to_trader', foodcart_trader_step)
	game.register_trigger_action('push_foodcart', foodcart_grass_step)
	game.register_trigger_action('trader_asks_for_help', trader_asks_for_help)
	game.register_trigger_action('pushing_cart', pushing_cart)
	game.register_trigger_action('cart_is_free', cart_is_free)

	return foodcart_quest
