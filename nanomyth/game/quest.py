""" Quests and quest-related entities.
"""
from ..math import Matrix
from .events import Trigger
from ..utils.meta import fieldproperty, typed

class ExternalQuestAction: # TODO move all kinds of triggers to events module
	""" Reference to an external callback.
	"""
	def __init__(self, callback_name, **params): # TODO needs to be typed.
		""" Creates reference object with the name of a trigger callback
		(which should be registered in the Game object)
		and optional set of keyword params, which will be passed to the call as such.
		"""
		self._name = callback_name
		self._params = params
	def __call__(self, trigger_registry): # TODO needs to be typed.
		""" Performs trigger callback from the trigger registry (callable)
		Passes provided params as keyword arguments.
		"""
		callback = trigger_registry(self._name)
		return callback(**(self._params))

class HistoryMessage:
	""" Element of a Quest's history.
	"""
	@typed(str)
	def __init__(self, message):
		self._message = message
	def __str__(self):
		return self._message

class QuestStateChange(Trigger): # TODO move all kinds of triggers to events module
	""" Provides means to trigger quest-related event.
	Once player steps on it, quest state is changed.
	"""
	@typed(str, str)
	def __init__(self, quest_name, action_name):
		self._quest_name = quest_name
		self._action_name = action_name
	def activate(self, quest_registry, trigger_registry): # TODO needs to be typed.
		""" Activates quest by name using given quest registry
		and invokes it's action using given trigger registry.
		Registry should be a callable that accepts quest name and returns Quest object.
		"""
		quest_registry(self._quest_name).perform_action(self._action_name, trigger_registry=trigger_registry)

class Quest:
	""" Defines player's quest as a list of tasks to follow.

	Basically a finite state machine, where states are intermediate steps,
	and actions are different actors (NPCs or world triggers) which player interacts with.

	Each state can have a callback object attached,
	which will be called when state is reached with some specific action,
	e.g. when NPC is approached by player with some item in it's inventory,
	they can show a conversation dialog with thanks and/or take said item.
	"""
	id = fieldproperty('_id', "Quest's internal ID.")
	title = fieldproperty('_title', "Quest's title.")

	@typed(str, str, list, list, finish_states=list)
	def __init__(self, quest_id, title, states, actions, finish_states=None):
		""" Creates quest with an ID, a title and lists of states/actions for the state machine.
		Default state is None, which is considered "not started yet".

		If finish_states are given, it is a list of states that are considered finish points.
		After reaching them, quest becomes finished (inactive).
		"""
		self._id = quest_id
		self._title = title
		self._states = [None] + list(states)
		self._actions = list(actions)
		self._state_machine = Matrix((len(self._actions), len(self._states)), [])
		self._finish_states = list(finish_states or [])
		self._start_callback = None
		self._finish_callback = None
		self._current_state = None
		self._history = []
	def get_history(self):
		""" Returns full quest history. """
		return self._history
	def get_last_history_entry(self):
		""" Returns the last quest history entry
		or None if there is nothing written there yet.
		"""
		return self._history[-1] if self._history else None
	def is_active(self):
		""" Retursn True if quest is active,
		i.e. started and not finished.
		"""
		return self._current_state is not None and self._current_state not in self._finish_states
	def perform_action(self, action_name, trigger_registry=None): # TODO needs typing.
		""" Performs action for the current state,
		resulting in calling all real callbacks attached to the state/action pair.
		Given params will be passed to every callback.
		"""
		actions_to_take = self._state_machine.cell((
			self._actions.index(action_name),
			self._states.index(self._current_state),
			))
		for action in actions_to_take:
			if isinstance(action, str):
				launch_start_callback = False
				if self._current_state is None and self._start_callback:
					launch_start_callback = True
				self._current_state = action
				if launch_start_callback:
					self._start_callback(trigger_registry)
				if self._current_state in self._finish_states and self._finish_callback:
					self._finish_callback(trigger_registry)
			elif isinstance(action, HistoryMessage):
				self._history.append(str(action))
			else:
				action(trigger_registry)
	@typed(str)
	def on_start(self, callback_name):
		""" Performs callback action when quest moves from start state via any action.
		Callback should accept parameter keyword quest=<this quest id>
		"""
		self._start_callback = ExternalQuestAction(callback_name, quest=self._id)
	@typed(str)
	def on_finish(self, callback_name):
		""" Performs callback action when quest reaches any of the "finish" states via any action.
		Callback should accept parameter keyword quest=<this quest id>
		"""
		self._finish_callback = ExternalQuestAction(callback_name, quest=self._id)
	@typed((str, None), str, (str, ExternalQuestAction, HistoryMessage))
	def on_state(self, state_name, action_name, callback):
		""" Attaches callback function to the state/action pair,
		meaning that it will be called when given action is performed while quest is in given state.
		If callback is a string, it is considered a name of a state,
		i.e. quest will advance to the specified state,
		otherwise it should be an ExternalQuestAction object.
		Use None instead of state to mark starting point of the quest,
		i.e the call/transition that will be performed when approached given action in default (not started) state.
		"""
		self._state_machine.cell((
			self._actions.index(action_name),
			self._states.index(state_name),
			)).append(callback)
