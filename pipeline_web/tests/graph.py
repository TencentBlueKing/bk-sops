import networkx as nx
from django.test import TestCase

from pipeline_web.graph import (
    get_graph_from_pipeline_tree,
    get_necessary_nodes_and_paths_between_nodes,
    get_ordered_necessary_nodes_and_paths_between_nodes,
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
