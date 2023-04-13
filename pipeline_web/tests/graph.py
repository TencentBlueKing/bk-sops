import networkx as nx
from django.test import TestCase

from pipeline_web.graph import (
    get_graph_from_pipeline_tree,
    get_necessary_nodes_and_paths_between_nodes,
    get_ordered_necessary_nodes_and_paths_between_nodes,
    get_all_nodes_and_edge_between_nodes,
    check_node_in_circle,
    get_all_nodes_and_edges_in_circle,
)


class PipelineWebGraphTestCase(TestCase):
    def test_get_graph_from_pipeline_tree_with_one_activity(self):
        pipeline_tree = {
            "start_event": {"id": "start_event"},
            "end_event": {"id": "end_event"},
            "gateways": {},
            "activities": {"act_1": {"id": "act_1"}},
            "flows": {
                "flow_1": {"source": "start_event", "target": "act_1"},
                "flow_2": {"source": "act_1", "target": "end_event"},
            },
        }
        graph = get_graph_from_pipeline_tree(pipeline_tree)
        self.assertEqual(len(graph.nodes), 3)
        self.assertEqual(len(graph.edges), 2)

    def test_get_necessary_nodes_and_paths_between_nodes_with_branch(self):
        G = nx.Graph()
        G.add_edges_from([(1, 2), (2, 3), (2, 4), (3, 5), (4, 5), (5, 6)])
        necessary_nodes, paths = get_necessary_nodes_and_paths_between_nodes(G, 1, 6)
        self.assertEqual(necessary_nodes, {1, 2, 5, 6})
        self.assertEqual(paths, [[1, 2, 3, 5, 6], [1, 2, 4, 5, 6]])

    def test_get_ordered_necessary_nodes_and_paths_between_nodes_with_branch(self):
        G = nx.Graph()
        G.add_edges_from([(1, 2), (2, 3), (2, 4), (3, 5), (4, 5), (5, 6)])
        necessary_nodes, paths = get_ordered_necessary_nodes_and_paths_between_nodes(G, 1, 6)
        self.assertEqual(necessary_nodes, [1, 2, 5, 6])
        self.assertEqual(paths, [[1, 2, 3, 5, 6], [1, 2, 4, 5, 6]])

    def test_get_all_nodes_and_edge_between_nodes(self):
        G = nx.Graph()
        G.add_edges_from([(1, 2, {"id": 1}), (2, 3, {"id": 2}), (1, 3, {"id": 3})])
        nodes, edges = get_all_nodes_and_edge_between_nodes(G, 1, 3)
        self.assertEqual(nodes, {1, 2, 3})
        self.assertEqual(edges, {1, 2, 3})

    def test_check_node_in_circle(self):
        G = nx.DiGraph()
        G.add_edges_from([(1, 2, {"id": 1}), (2, 3, {"id": 2}), (1, 3, {"id": 3})])
        self.assertEqual(check_node_in_circle(G, 1), False)
        G.add_edges_from([(3, 1, {"id": 4})])
        self.assertEqual(check_node_in_circle(G, 1), True)

    def test_get_all_nodes_and_edges_in_circle(self):
        G = nx.DiGraph()
        G.add_edges_from([(1, 2, {"id": 1}), (2, 3, {"id": 2}), (1, 3, {"id": 3}), (3, 1, {"id": 4})])
        nodes, edges = get_all_nodes_and_edges_in_circle(G, 1)
        self.assertEqual(nodes, {1, 2, 3})
        self.assertEqual(edges, {1, 2, 3, 4})
