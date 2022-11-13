""" Quests and quest-related entities.
"""
from ..math import Matrix

class Quest:
	""" Defines player's quest as a list of tasks to follow.

	Basically a finite state machine, where states are intermediate steps,
	and actions are different actors (NPCs or world triggers) which player interacts with.

	Each state can have a callback object attached,
	which will be called when state is reached with some specific action,
	e.g. when NPC is approached by player with some item in it's inventory,
	they can show a conversation dialog with thanks and/or take said item.
	"""
	def __init__(self, title, states, actions):
		""" Creates quest with a title and lists of states/actions for the state machine.
		Default state is None, which is considered "not started yet".
		"""
		self.title = title
		self.states = [None] + list(states)
		self.actions = list(actions)
		self.state_machine = Matrix((len(self.actions), len(self.states)), [])
		self.current_state = None
	def get_action_callback(self, action_name):
		""" Creates callback function to perform action for a current state.
		Callback can accept any numbers of positional arguments,
		they will be passed to all the real callbacks attached to the state/action pair.
		"""
		return lambda *params: self.perform_action(action_name, *params)
	def perform_action(self, action_name, *params):
		""" Performs action for the current state,
		resulting in calling all real callbacks attached to the state/action pair.
		Given params will be passed to every callback.
		"""
		actions_to_take = self.state_machine.cell((
			self.actions.index(action_name),
			self.states.index(self.current_state),
			))
		for action_callback in actions_to_take:
			if isinstance(action_callback, str):
				self.current_state = action_callback
			else:
				action_callback(*params)
	def on_state(self, state_name, action_name, callback):
		""" Attaches callback function to the state/action pair,
		meaning that it will be called when given action is performed while quest is in given state.
		If callback is a string, it is considered a name of a state,
		i.e. quest will advance to the specified state.
		Use None instead of state to mark starting point of the quest,
		i.e the call/transition that will be performed when approached given action in default (not started) state.
		"""
		self.state_machine.cell((
			self.actions.index(action_name),
			self.states.index(state_name),
			)).append(callback)