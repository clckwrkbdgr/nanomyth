""" Limited support for parsing GraphML files.
"""
from xml.dom import minidom
from pathlib import Path

class Node:
	""" Graph node.
	Fields:
	- id
	Attributes are accessible by key: node['attr_name']
	"""
	def __init__(self, node_id, attributes):
		self.id = node_id
		self.attributes = attributes
	def __getitem__(self, key):
		return self.attributes.get(key, None)

class Edge:
	""" Graph edge.
	Fields:
	- id
	- source
	- target
	Attributes are accessible by key: edge['attr_name']
	"""
	def __init__(self, edge_id, source, target, attributes):
		self.id = edge_id
		self.source = source
		self.target = target
		self.attributes = attributes
	def __getitem__(self, key):
		return self.attributes.get(key, None)

class Graph:
	""" Graph structure.
	Attributes are accessible by key: graph['attr_name']
	Nodes and edges are available as lists: .nodes, .edges.
	"""
	def __init__(self):
		self.default_graph_attributes = {}
		self.default_node_attributes = {}
		self.default_edge_attributes = {}
		self.nodes = []
		self.edges = []
	def __getitem__(self, key):
		return self.default_graph_attributes.get(key, None)

	@classmethod
	def parse(cls, filename):
		""" Parses given file as GraphML
		and returns a Graph.
		"""
		return cls.fromstring(Path(filename).read_text())
	@classmethod
	def fromstring(cls, string_data):
		""" Parses provided string as GraphML.
		and returns a Graph.
		"""
		dom = minidom.parseString(string_data)
		root = dom.getElementsByTagName("graphml")[0]
		graph = root.getElementsByTagName("graph")[0]

		result = cls()

		def _get_element_content(_element):
			if _element.firstChild:
				return _element.firstChild.data
			return None

		def _convert_attr_value(_attr_value, _attr_type):
			if _attr_type == 'integer':
				return int(_attr_value or 0)
			if _attr_type in ['float', 'double']:
				return float(_attr_value or 0.0)
			return str(_attr_value or '')

		node_attr_types = {}
		edge_attr_types = {}
		for attr in root.getElementsByTagName("key"):
			attr_name = attr.getAttribute('attr.name')
			attr_type = attr.getAttribute('attr.type')
			default_value = next(iter(attr.getElementsByTagName("default")))
			value = _convert_attr_value(_get_element_content(default_value), attr_type)

			entity_type = attr.getAttribute('for')
			if entity_type == 'graph':
				result.default_graph_attributes[attr_name] = value
			elif entity_type == 'node':
				node_attr_types[attr_name] = attr_type
				result.default_node_attributes[attr_name] = value
			elif entity_type == 'edge':
				edge_attr_types[attr_name] = attr_type
				result.default_edge_attributes[attr_name] = value

		for node in graph.getElementsByTagName("node"):
			node_id = node.getAttribute('id')
			attributes = dict(**(result.default_node_attributes))
			for attr in node.getElementsByTagName("data"):
				key = attr.getAttribute("key")
				value = _convert_attr_value(_get_element_content(attr), node_attr_types.get(key, 'string'))
				attributes[key] = value
			result.nodes.append(Node(node_id, attributes))

		for edge in graph.getElementsByTagName("edge"):
			edge_id = edge.getAttribute('id')
			source = edge.getAttribute('source')
			target = edge.getAttribute('target')
			attributes = dict(**(result.default_edge_attributes))
			for attr in edge.getElementsByTagName("data"):
				key = attr.getAttribute("key")
				value = _convert_attr_value(_get_element_content(attr), edge_attr_types.get(key, 'string'))
				attributes[key] = value
			result.edges.append(Edge(edge_id, source, target, attributes))

		return result
