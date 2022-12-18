""" Utilities to loading quests from GraphML files.
"""
from pathlib import Path
from ...utils.graphml import Graph
from ...game.quest import Quest, ExternalQuestAction, HistoryMessage

def load_graphml_quest(filename):
	""" Loads Quest object from GraphML file and returns prepared quest.

	Quest is represented as graph (state diagram),
	where nodes are quest states,
	and edges are external actions and/or transitions.

	Graph attributes:
	- id: Graph internal ID.
	  If not present, file base name (without extension) is used.
	- title: Human-readable quest title.

	Optional attribute "point" can be set for nodes. It can have two values:
	- start: This will be the starting state.
	- finish: Upon reaching this node, quest becomes finished.
	There should be only one point=start node, but could be more than one point=finish nodes.

	Edges should have two required attributes:
	- trigger: a name of the FSM action (the one that triggers transion).
	- action: a name of the external action callback to execute upon triggering. It will be added using ExternalQuestAction wrapper.
	Optional edge attributes:
	- history: a text message for the quest's log, usually marking some important quest step.

	All other attributes will be passed as keyword arguments to ExternalQuestAction callback.
	WARNING: Some GraphML editors may add non-user attributes which will still be parsed by this loader,
	so callbacks should have some double-star-unpack argument for these 'extra' parameters, e.g.:
	callback(param1, param2, **extra)

	Actions that are not supposed to change states (just trigger a callback) should be added as loopback edges.
	Otherwise trigger will force quest to switch to a new target state.
	"""
	quest_data = Graph.parse(filename)

	start_node = next(node.id for node in quest_data.nodes if node['point'] == 'start')
	finish_nodes = [node.id for node in quest_data.nodes if node['point'] == 'finish']
	states = [node.id for node in quest_data.nodes if node.id != start_node]
	actions = list(set(edge['trigger'] for edge in quest_data.edges))
	quest = Quest(quest_data['id'] or Path(filename).stem, quest_data['title'], states, actions, finish_states=finish_nodes)

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
		history = edge.attributes.get('history')
		if history:
			quest.on_state(source, trigger, HistoryMessage(history))
		params = {key:value for key, value in edge.attributes.items() if key not in ('action', 'trigger', 'history')}
		quest.on_state(source, trigger, ExternalQuestAction(action, **params))
	for source, trigger, target in transitions:
		quest.on_state(source, trigger, target)
	return quest
