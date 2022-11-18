import os
from pathlib import Path
from .. import unittest
from .. import graphml
from ..graphml import Graph

TEST_GRAPHML_FILE = Path(__file__).parent/'test.graphml'
TEST_GRAPHML = TEST_GRAPHML_FILE.read_text()

class TestGraphMLParser(unittest.TestCase):
	def should_parse_graph(self):
		graph = Graph.fromstring(TEST_GRAPHML)

		self.assertEqual(graph['graph_attr'], 'foo')
		self.assertEqual(graph['graph_attr_int'], 12345)

		self.assertEqual(len(graph.nodes), 3)
		self.assertEqual(graph.nodes[0].id, 'A')
		self.assertEqual(graph.nodes[0]['node_attr'], 'lorem\nipsum')
		self.assertAlmostEqual(graph.nodes[0]['node_attr_float'], 6.66)
		self.assertEqual(graph.nodes[1].id, 'B')
		self.assertEqual(graph.nodes[1]['node_attr'], 'node attr')
		self.assertAlmostEqual(graph.nodes[1]['node_attr_float'], 0.12345)
		self.assertEqual(graph.nodes[2].id, 'C')
		self.assertEqual(graph.nodes[2]['node_attr'], 'baz')
		self.assertAlmostEqual(graph.nodes[2]['node_attr_float'], 67.89)

		self.assertEqual(len(graph.edges), 4)
		self.assertEqual(graph.edges[0].id, 'AC')
		self.assertEqual(graph.edges[0].source, 'A')
		self.assertEqual(graph.edges[0].target, 'C')
		self.assertEqual(graph.edges[0]['edge_attr'], 'forward')
		self.assertAlmostEqual(graph.edges[0]['edge_attr_double'], 12.345)
		self.assertEqual(graph.edges[1].id, 'AA')
		self.assertEqual(graph.edges[1].source, 'A')
		self.assertEqual(graph.edges[1].target, 'A')
		self.assertEqual(graph.edges[1]['edge_attr'], 'loop')
		self.assertAlmostEqual(graph.edges[1]['edge_attr_double'], 1.2345)
		self.assertEqual(graph.edges[2].id, 'CA')
		self.assertEqual(graph.edges[2].source, 'C')
		self.assertEqual(graph.edges[2].target, 'A')
		self.assertEqual(graph.edges[2]['edge_attr'], 'bar')
		self.assertAlmostEqual(graph.edges[2]['edge_attr_double'], 34.567)
		self.assertEqual(graph.edges[3].id, 'BA')
		self.assertEqual(graph.edges[3].source, 'B')
		self.assertEqual(graph.edges[3].target, 'A')
		self.assertEqual(graph.edges[3]['edge_attr'], '')
		self.assertAlmostEqual(graph.edges[3]['edge_attr_double'], 1.2345)
	def should_load_graph_from_file(self):
		graph = Graph.parse(TEST_GRAPHML_FILE)
		self.assertEqual(graph['graph_attr_int'], 12345)
		self.assertEqual(graph.nodes[0].id, 'A')
		self.assertEqual(graph.edges[1].source, 'A')
