""" Utilities to loading quests from GraphML files.
"""
from ...utils.graphml import Graph
from ...game.quest import Quest, ExternalQuestAction

def load_graphml_quest(filename):
	""" Loads Quest object from GraphML file.
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
		quest.on_state(source, trigger, ExternalQuestAction(action))
	for source, trigger, target in transitions:
		quest.on_state(source, trigger, target)
	return quest
