""" Utilities to loading quests from GraphML files.
"""
from ...utils.graphml import Graph
from ...game.quest import Quest, ExternalQuestAction

def load_graphml_quest(filename):
	""" Loads Quest object from GraphML file and returns prepared quest.

	Quest is represented as graph (state diagram),
	where nodes are quest states,
	and edges are external actions and/or transitions.

	Quest title should be set in graph attribute 'title'.

	Some node should have attribute 'start' set to 'true'.
	This will be the start state.

	Edges should have two required attributes:
	- 'trigger': a name of the FSM action (the one that triggers transion).
	- 'action': a name of the external action callback to execute upon triggering. It will be added using ExternalQuestAction wrapper.
	All other attributes will be passed as keyword arguments to ExternalQuestAction callback.
	WARNING: Some GraphML editors may add non-user attributes which will still be parsed by this loader,
	so callbacks should have some double-star-unpack argument for these 'extra' parameters, e.g.:
	callback(param1, param2, **extra)

	Actions that are not supposed to change states (just trigger a callback) should be added as loopback edges.
	Otherwise trigger will force quest to switch to a new target state.
	"""
	quest_data = Graph.parse(filename)

	states = [node.id for node in quest_data.nodes if not node['start']]
	actions = list(set(edge['trigger'] for edge in quest_data.edges))
	quest = Quest(quest_data['title'], states, actions)

	start_node = next(node.id for node in quest_data.nodes if node['start'])
	transitions = set()
	external_actions = []
	for edge in quest_data.edges:
		source, target = edge.source, edge.target
		if source == start_node:
			source = None
		if target == start_node:
			target = None
		action, trigger = edge['action'], edge['trigger']
		if source != target:
			transitions.add( (source, trigger, target) )
		params = {key:value for key, value in edge.attributes.items() if key not in ('action', 'trigger')}
		quest.on_state(source, trigger, ExternalQuestAction(action, **params))
	for source, trigger, target in transitions:
		quest.on_state(source, trigger, target)
	return quest
