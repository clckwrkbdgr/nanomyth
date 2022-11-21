""" Quests and quest-related entities.
"""
from ..math import Matrix

class ExternalQuestAction:
	""" Reference to an external callback.
	"""
	def __init__(self, callback_name, **params):
		""" Creates reference object with the name of a trigger callback
		(which should be registered in the Game object)
		and optional set of keyword params, which will be passed to the call as such.
		"""
		self.name = callback_name
		self.params = params
	def __call__(self, trigger_registry):
		""" Performs trigger callback from the trigger registry (callable)
		Passes provided params as keyword arguments.
		"""
		callback = trigger_registry(self.name)
		return callback(**(self.params))

class QuestStateChange:
	""" Provides means to trigger quest-related event.
	Once player steps on it, quest state is changed.
	"""
	def __init__(self, quest_name, action_name):
		self.quest_name = quest_name
		self.action_name = action_name
	def activate(self, quest_registry, trigger_registry):
		""" Activates quest by name using given quest registry
		and invokes it's action using given trigger registry.
		Registry should be a callable that accepts quest name and returns Quest object.
		"""
		quest_registry(self.quest_name).perform_action(self.action_name, trigger_registry=trigger_registry)

class Quest:
	""" Defines player's quest as a list of tasks to follow.

	Basically a finite state machine, where states are intermediate steps,
	and actions are different actors (NPCs or world triggers) which player interacts with.

	Each state can have a callback object attached,
	which will be called when state is reached with some specific action,
	e.g. when NPC is approached by player with some item in it's inventory,
	they can show a conversation dialog with thanks and/or take said item.
	"""
	def __init__(self, title, states, actions, finish_states=None):
		""" Creates quest with a title and lists of states/actions for the state machine.
		Default state is None, which is considered "not started yet".

		If finish_states are given, it is a list of states that are considered finish points.
		After reaching them, quest becomes finished (inactive).
		"""
		self.title = title
		self.states = [None] + list(states)
		self.actions = list(actions)
		self.state_machine = Matrix((len(self.actions), len(self.states)), [])
		self.finish_states = list(finish_states or [])
		self.finish_callback = None
		self.current_state = None
	def is_active(self):
		""" Retursn True if quest is active,
		i.e. started and not finished.
		"""
		return self.current_state is not None and self.current_state not in self.finish_states
	def perform_action(self, action_name, trigger_registry=None):
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
				if self.current_state in self.finish_states and self.finish_callback:
					self.finish_callback(trigger_registry)
			else:
				action_callback(trigger_registry)
	def on_finish(self, callback_name):
		""" Performs callback action when quest reaches any of the "finish" states via any action. """
		self.finish_callback = ExternalQuestAction(callback_name, quest=self.title)
	def on_state(self, state_name, action_name, callback):
		""" Attaches callback function to the state/action pair,
		meaning that it will be called when given action is performed while quest is in given state.
		If callback is a string, it is considered a name of a state,
		i.e. quest will advance to the specified state,
		otherwise it should be an ExternalQuestAction object.
		Use None instead of state to mark starting point of the quest,
		i.e the call/transition that will be performed when approached given action in default (not started) state.
		"""
		assert isinstance(callback, str) or isinstance(callback, ExternalQuestAction), repr(callback)
		self.state_machine.cell((
			self.actions.index(action_name),
			self.states.index(state_name),
			)).append(callback)
