import unittest

import dominator_mutants
import txt_to_dominator_mutants


class TestCase(unittest.TestCase):

    def test_create_empty_node_with_no_name_and_tests(self):
        test_node = dominator_mutants.Node()
        self.assertEquals(set(), test_node.mutant_name)
        self.assertEquals(set(), test_node.tests)
        self.assertEquals(set(), test_node.children)
        self.assertEquals(set(), test_node.parents)

    def test_create_simple_node_with_all_attributes(self):
        test_node = dominator_mutants.Node({1}, {1, 2})
        self.assertEquals(test_node.mutant_name, {1})
        self.assertEquals(test_node.tests, {1, 2})
        self.assertEquals(set(), test_node.children)
        self.assertEquals(set(), test_node.parents)

    def test_create_node_from_with_tests_only_from_kill_map(self):
        kill_map = {frozenset({1}): {1, 2}, frozenset({2}): {1, 4},
                    frozenset({3}): {2}, frozenset({4}): {1, 2, 3, 4}}
        test_graph = dominator_mutants.calculate_dominating_mutants(kill_map)[0]

        self.assertEquals(test_graph.nodes[0].mutant_name,
                          list(kill_map.keys())[0])
        self.assertEquals(test_graph.nodes[0].tests,
                          kill_map.get(list(kill_map)[0]))
        self.assertEquals(test_graph.nodes[3].mutant_name,
                          list(kill_map.keys())[3])
        self.assertEquals(test_graph.nodes[3].tests,
                          kill_map.get(list(kill_map)[3]))

    def test_is_distinguishable(self):
        mutant_2 = dominator_mutants.Node(frozenset({2}), {1, 4})
        mutant_5 = dominator_mutants.Node(frozenset({5}), {1, 4})
        mutant_1 = dominator_mutants.Node(frozenset({1}), {1, 2})
        self.assertTrue(mutant_2.is_distinguishable_from(mutant_1))
        self.assertFalse(mutant_1.is_distinguishable_from(mutant_1))
        self.assertFalse(mutant_2.is_distinguishable_from(mutant_5))

    def test_merge_indistinguishable(self):

        mutant_2 = dominator_mutants.Node({2}, {1, 4})
        mutant_5 = dominator_mutants.Node({5}, {1, 4})

        test_graph = dominator_mutants.Graph()
        test_graph.add_node(mutant_2)
        test_graph.add_node(mutant_5)
        test_graph.create_edges()

        result = []
        for node in test_graph.nodes:
            result.append(node)

        self.assertEquals(result[0].mutant_name, {2, 5})

    def test_add_node(self):
        mutant_1 = dominator_mutants.Node({1}, {1, 2})
        test_graph = dominator_mutants.Graph()
        test_graph.add_node(mutant_1)
        self.assertEquals(mutant_1, test_graph.nodes[0])

    def test_connect_the_same_node_to_itself(self):
        mutant_2 = dominator_mutants.Node({2}, {1, 4})
        test_graph = dominator_mutants.Graph()
        test_graph.add_node(mutant_2)
        test_graph.create_edges()
        test_graph_nodes = test_graph.nodes
        result = []
        for nodes in test_graph_nodes:
            result.append(nodes.mutant_name)

        self.assertEquals([{2}], result)

    def test_connect_nodes_indistinguishable(self):
        mutant_2 = dominator_mutants.Node({2}, {1, 4})
        mutant_5 = dominator_mutants.Node({5}, {1, 4})
        test_graph = dominator_mutants.Graph()
        test_graph.add_node(mutant_2)
        test_graph.add_node(mutant_5)
        test_graph.create_edges()
        test_graph_nodes = test_graph.nodes
        result = []
        for nodes in test_graph_nodes:
            result.append(nodes.mutant_name)
        self.assertEquals([{2, 5}], result)

    def test_connect_two_nodes_distinguishable(self):
        mutant_1 = dominator_mutants.Node({1}, {1, 2})
        mutant_2 = dominator_mutants.Node({2}, {1, 4})
        test_graph = dominator_mutants.Graph()
        test_graph.add_node(mutant_1)
        test_graph.add_node(mutant_2)

        test_graph.create_edges()
        test_graph_nodes = test_graph.nodes
        result = []
        for nodes in test_graph_nodes:
            result.append(nodes.mutant_name)
        self.assertEquals([{1}, {2}], result)

    def test_add_relation_just_two_nodes_children(self):
        mutant_3 = dominator_mutants.Node({3}, {2})
        mutant_1 = dominator_mutants.Node({1}, {1, 2})
        test_graph = dominator_mutants.Graph()
        test_graph.add_node(mutant_3)
        test_graph.add_node(mutant_1)
        test_graph.create_edges()

        result = []
        result_parent = []

        if mutant_3.parents is None:
            mutant_3.parents = set()
        for nodes in mutant_3.parents:
            result.append(nodes.mutant_name)
        self.assertEquals([], result)
        if mutant_3.children is None:
            mutant_3.children = set()
        for parents in mutant_3.children:
            result_parent.append(parents.mutant_name)
        self.assertEquals([{1}], result_parent)

        result2 = []
        result_parent2 = []

        if mutant_1.parents is None:
            mutant_1.parents = set()
        for nodes2 in mutant_1.parents:
            result2.append(nodes2.mutant_name)
        self.assertEquals([{3}], result2)
        if mutant_1.parents is None:
            mutant_1.parents = set()
        for parents in mutant_1.parents:
            result_parent2.append(parents.mutant_name)
        self.assertEquals([{3}], result_parent2)

    def test_add_relation_for_children_with_3_level_graph(self):
        mutant_3 = dominator_mutants.Node({3}, {2})
        mutant_1 = dominator_mutants.Node({1}, {1, 2})
        mutant_4 = dominator_mutants.Node({4}, {1, 2, 3, 4})

        test_graph = dominator_mutants.Graph()
        test_graph.add_node(mutant_3)
        test_graph.add_node(mutant_1)
        test_graph.add_node(mutant_4)

        test_graph.create_edges()

        # mutant 3
        result = []
        result_parent = []

        if test_graph.nodes[0].children is None:
            test_graph.nodes[0].children = set()
        for nodes in test_graph.nodes[0].children:
            result.append(nodes.mutant_name)
        self.assertEquals([{1}], result)

        if test_graph.nodes[0].parents is None:
            test_graph.nodes[0].parents = set()
        for parents in test_graph.nodes[0].parents:
            result_parent.append(parents.mutant_name)
        self.assertEquals([], result_parent)

        # mutant 1
        result2 = []
        result_parent2 = []

        if test_graph.nodes[1].parents is None:
            test_graph.nodes[1].parents = set()
        for parents2 in test_graph.nodes[1].parents:
            result_parent2.append(parents2.mutant_name)
        self.assertEquals([{3}], result_parent2)

        if test_graph.nodes[1].children is None:
            test_graph.nodes[1].children = set()
        for nodes2 in test_graph.nodes[1].children:
            result2.append(nodes2.mutant_name)
        self.assertEquals([{4}], result2)

        # mutant 4
        result4 = []
        result_parent4 = []

        if test_graph.nodes[2].parents is None:
            test_graph.nodes[2].parents = set()
        for parents4 in test_graph.nodes[2].parents:
            result_parent4.append(parents4.mutant_name)
        self.assertEquals([{1}], result_parent4)

        if test_graph.nodes[2].children is None:
            test_graph.nodes[2].children = set()
        for nodes4 in test_graph.nodes[2].children:
            result4.append(nodes4.mutant_name)
        self.assertEquals([], result4)

    def test_add_relation_for_children_with_4_level_graph(self):
        mutant_3 = dominator_mutants.Node({3}, {2})
        mutant_1 = dominator_mutants.Node({1}, {1, 2})
        mutant_6 = dominator_mutants.Node({6}, {1, 2, 3})
        mutant_4 = dominator_mutants.Node({4}, {1, 2, 3, 4})

        test_graph = dominator_mutants.Graph()
        test_graph.add_node(mutant_3)
        test_graph.add_node(mutant_1)
        test_graph.add_node(mutant_6)
        test_graph.add_node(mutant_4)

        test_graph.create_edges()

        # mutant 3
        result = []
        result_parent = []

        if test_graph.nodes[0].children is None:
            test_graph.nodes[0].children = set()
        for nodes in test_graph.nodes[0].children:
            result.append(nodes.mutant_name)
        self.assertEquals([{1}], result)

        if test_graph.nodes[0].parents is None:
            test_graph.nodes[0].parents = set()
        for parents in test_graph.nodes[0].parents:
            result_parent.append(parents.mutant_name)
        self.assertEquals([], result_parent)

        # mutant 1
        result2 = []
        result_parent2 = []

        if test_graph.nodes[1].parents is None:
            test_graph.nodes[1].parents = set()
        for parents2 in test_graph.nodes[1].parents:
            result_parent2.append(parents2.mutant_name)
        self.assertEquals([{3}], result_parent2)

        if test_graph.nodes[1].children is None:
            test_graph.nodes[1].children = set()
        for nodes2 in test_graph.nodes[1].children:
            result2.append(nodes2.mutant_name)
        self.assertEquals([{6}], result2)

        # mutant 6
        result3 = []
        result_parent3 = []

        if test_graph.nodes[2].parents is None:
            test_graph.nodes[2].parents = set()
        for parents3 in test_graph.nodes[2].parents:
            result_parent3.append(parents3.mutant_name)
        self.assertEquals([{1}], result_parent3)

        if test_graph.nodes[2].children is None:
            test_graph.nodes[2].children = set()
        for nodes3 in test_graph.nodes[2].children:
            result3.append(nodes3.mutant_name)
        self.assertEquals([{4}], result3)

        # mutant 4
        result4 = []
        result_parent4 = []

        if test_graph.nodes[3].parents is None:
            test_graph.nodes[3].parents = set()
        for parents4 in test_graph.nodes[3].parents:
            result_parent4.append(parents4.mutant_name)
        self.assertEquals([{6}], result_parent4)

        if test_graph.nodes[3].children is None:
            test_graph.nodes[3].children = set()
        for nodes4 in test_graph.nodes[3].children:
            result4.append(nodes4.mutant_name)
        self.assertEquals([], result4)

    def test_add_relation_just_two_nodes_parents(self):
        mutant_3 = dominator_mutants.Node({3}, {2})
        mutant_1 = dominator_mutants.Node({1}, {1, 2})
        test_graph = dominator_mutants.Graph()
        test_graph.add_node(mutant_1)
        test_graph.add_node(mutant_3)
        test_graph.create_edges()

        result = []
        result_parent = []

        if mutant_3.parents is None:
            mutant_3.parents = set()
        for nodes in mutant_3.parents:
            result.append(nodes.mutant_name)
        self.assertEquals([], result)
        if mutant_3.children is None:
            mutant_3.children = set()
        for parents in mutant_3.children:
            result_parent.append(parents.mutant_name)
        self.assertEquals([{1}], result_parent)

        result2 = []
        result_parent2 = []

        if mutant_1.parents is None:
            mutant_1.parents = set()
        for nodes2 in mutant_1.parents:
            result2.append(nodes2.mutant_name)
        self.assertEquals([{3}], result2)
        if mutant_1.parents is None:
            mutant_1.parents = set()
        for parents in mutant_1.parents:
            result_parent2.append(parents.mutant_name)
        self.assertEquals([{3}], result_parent2)

    def test_add_relation_for_parents_with_3_level_graph(self):
        mutant_4 = dominator_mutants.Node({4}, {1, 2, 3, 4})
        mutant_1 = dominator_mutants.Node({1}, {1, 2})
        mutant_3 = dominator_mutants.Node({3}, {2})

        test_graph = dominator_mutants.Graph()
        test_graph.add_node(mutant_4)
        test_graph.add_node(mutant_1)
        test_graph.add_node(mutant_3)

        test_graph.create_edges()

        # mutant 3
        result = []
        result_parent = []

        if test_graph.nodes[2].children is None:
            test_graph.nodes[2].children = set()
        for nodes in test_graph.nodes[2].children:
            result.append(nodes.mutant_name)
        self.assertEquals([{1}], result)

        if test_graph.nodes[2].parents is None:
            test_graph.nodes[2].parents = set()
        for parents in test_graph.nodes[2].parents:
            result_parent.append(parents.mutant_name)
        self.assertEquals([], result_parent)

        # mutant 1
        result2 = []
        result_parent2 = []

        if test_graph.nodes[1].parents is None:
            test_graph.nodes[1].parents = set()
        for parents2 in test_graph.nodes[1].parents:
            result_parent2.append(parents2.mutant_name)
        self.assertEquals([{3}], result_parent2)

        if test_graph.nodes[1].children is None:
            test_graph.nodes[1].children = set()
        for nodes2 in test_graph.nodes[1].children:
            result2.append(nodes2.mutant_name)
        self.assertEquals([{4}], result2)

        # mutant 4
        result4 = []
        result_parent4 = []

        if test_graph.nodes[0].parents is None:
            test_graph.nodes[0].parents = set()
        for parents4 in test_graph.nodes[0].parents:
            result_parent4.append(parents4.mutant_name)
        self.assertEquals([{1}], result_parent4)

        if test_graph.nodes[0].children is None:
            test_graph.nodes[0].children = set()
        for nodes4 in test_graph.nodes[0].children:
            result4.append(nodes4.mutant_name)
        self.assertEquals([], result4)

    def test_add_relation_for_parents_with_3_level_graph_one_indistinguishable(
            self):
        mutant_4 = dominator_mutants.Node({4}, {1, 2, 3, 4})
        mutant_1 = dominator_mutants.Node({1}, {1, 2})
        mutant_3 = dominator_mutants.Node({3}, {2})
        mutant_6 = dominator_mutants.Node({6}, {1, 2})

        test_graph = dominator_mutants.Graph()
        test_graph.add_node(mutant_4)
        test_graph.add_node(mutant_1)
        test_graph.add_node(mutant_3)
        test_graph.add_node(mutant_6)

        test_graph.create_edges()

        # mutant 3
        result2 = []
        result_parent2 = []

        if test_graph.nodes[2].parents is None:
            test_graph.nodes[2].parents = set()
        for parents2 in test_graph.nodes[2].parents:
            result_parent2.append(parents2.mutant_name)
        self.assertEquals([], result_parent2)

        if test_graph.nodes[2].children is None:
            test_graph.nodes[2].children = set()
        for nodes2 in test_graph.nodes[2].children:
            result2.append(nodes2.mutant_name)
        self.assertEquals([{1, 6}], result2)

        # mutant 1, 6
        result3 = []
        result_parent3 = []

        if test_graph.nodes[1].parents is None:
            test_graph.nodes[1].parents = set()
        for parents3 in test_graph.nodes[1].parents:
            result_parent3.append(parents3.mutant_name)
        self.assertEquals([{3}], result_parent3)

        if test_graph.nodes[1].children is None:
            test_graph.nodes[1].children = set()
        for nodes3 in test_graph.nodes[1].children:
            result3.append(nodes3.mutant_name)
        self.assertEquals([{4}], result3)

        # mutant 4
        result4 = []
        result_parent4 = []

        if test_graph.nodes[0].parents is None:
            test_graph.nodes[0].parents = set()
        for parents4 in test_graph.nodes[0].parents:
            result_parent4.append(parents4.mutant_name)
        self.assertEquals([{1, 6}], result_parent4)

        if test_graph.nodes[0].children is None:
            test_graph.nodes[0].children = set()
        for nodes4 in test_graph.nodes[0].children:
            result4.append(nodes4.mutant_name)
        self.assertEquals([], result4)

    def test_add_relation_for_parents_with_4_level_graph_2(self):
        mutant_4 = dominator_mutants.Node({4}, {1, 2, 3, 4})
        mutant_6 = dominator_mutants.Node({6}, {1, 2, 3})
        mutant_1 = dominator_mutants.Node({1}, {1, 2})
        mutant_3 = dominator_mutants.Node({3}, {2})

        test_graph = dominator_mutants.Graph()
        test_graph.add_node(mutant_4)
        test_graph.add_node(mutant_6)
        test_graph.add_node(mutant_1)
        test_graph.add_node(mutant_3)

        test_graph.create_edges()

        # mutant 3
        result = []
        result_parent = []

        if test_graph.nodes[3].children is None:
            test_graph.nodes[3].children = set()
        for nodes in test_graph.nodes[3].children:
            result.append(nodes.mutant_name)
        self.assertEquals([{1}], result)

        if test_graph.nodes[3].parents is None:
            test_graph.nodes[3].parents = set()
        for parents in test_graph.nodes[3].parents:
            result_parent.append(parents.mutant_name)
        self.assertEquals([], result_parent)

        # mutant 1
        result2 = []
        result_parent2 = []

        if test_graph.nodes[2].parents is None:
            test_graph.nodes[2].parents = set()
        for parents2 in test_graph.nodes[2].parents:
            result_parent2.append(parents2.mutant_name)
        self.assertEquals([{3}], result_parent2)

        if test_graph.nodes[2].children is None:
            test_graph.nodes[2].children = set()
        for nodes2 in test_graph.nodes[2].children:
            result2.append(nodes2.mutant_name)
        self.assertEquals([{6}], result2)

        # mutant 6
        result3 = []
        result_parent3 = []

        if test_graph.nodes[1].parents is None:
            test_graph.nodes[1].parents = set()
        for parents3 in test_graph.nodes[1].parents:
            result_parent3.append(parents3.mutant_name)
        self.assertEquals([{1}], result_parent3)

        if test_graph.nodes[1].children is None:
            test_graph.nodes[1].children = set()
        for nodes3 in test_graph.nodes[1].children:
            result3.append(nodes3.mutant_name)
        self.assertEquals([{4}], result3)

        # mutant 4
        result4 = []
        result_parent4 = []

        if test_graph.nodes[0].parents is None:
            test_graph.nodes[0].parents = set()
        for parents4 in test_graph.nodes[0].parents:
            result_parent4.append(parents4.mutant_name)
        self.assertEquals([{6}], result_parent4)

        if test_graph.nodes[0].children is None:
            test_graph.nodes[0].children = set()
        for nodes4 in test_graph.nodes[0].children:
            result4.append(nodes4.mutant_name)
        self.assertEquals([], result4)

    def test_add_relation_for_parents_and_children_with_3_level_graph(self):
        mutant_4 = dominator_mutants.Node({4}, {1, 2, 3, 4})
        mutant_3 = dominator_mutants.Node({3}, {2})
        mutant_1 = dominator_mutants.Node({1}, {1, 2})

        test_graph = dominator_mutants.Graph()
        test_graph.add_node(mutant_4)
        test_graph.add_node(mutant_3)
        test_graph.add_node(mutant_1)

        test_graph.create_edges()

        # mutant 3
        result = []
        result_parent = []

        if test_graph.nodes[1].children is None:
            test_graph.nodes[1].children = set()
        for nodes in test_graph.nodes[1].children:
            result.append(nodes.mutant_name)
        self.assertEquals([{1}], result)

        if test_graph.nodes[1].parents is None:
            test_graph.nodes[1].parents = set()
        for parents in test_graph.nodes[1].parents:
            result_parent.append(parents.mutant_name)
        self.assertEquals([], result_parent)

        # mutant 1
        result2 = []
        result_parent2 = []

        if test_graph.nodes[2].parents is None:
            test_graph.nodes[2].parents = set()
        for parents2 in test_graph.nodes[2].parents:
            result_parent2.append(parents2.mutant_name)
        self.assertEquals([{3}], result_parent2)

        if test_graph.nodes[2].children is None:
            test_graph.nodes[2].children = set()
        for nodes2 in test_graph.nodes[2].children:
            result2.append(nodes2.mutant_name)
        self.assertEquals([{4}], result2)

        # mutant 4
        result4 = []
        result_parent4 = []

        if test_graph.nodes[0].parents is None:
            test_graph.nodes[0].parents = set()
        for parents4 in test_graph.nodes[0].parents:
            result_parent4.append(parents4.mutant_name)
        self.assertEquals([{1}], result_parent4)

        if test_graph.nodes[0].children is None:
            test_graph.nodes[0].children = set()
        for nodes4 in test_graph.nodes[0].children:
            result4.append(nodes4.mutant_name)
        self.assertEquals([], result4)

    def test_add_relation_for_parents_and_children_with_3_level_graph_2(self):
        mutant_1 = dominator_mutants.Node({1}, {1, 2})
        mutant_4 = dominator_mutants.Node({4}, {1, 2, 3, 4})
        mutant_3 = dominator_mutants.Node({3}, {2})

        test_graph = dominator_mutants.Graph()

        test_graph.add_node(mutant_3)
        test_graph.add_node(mutant_4)
        test_graph.add_node(mutant_1)

        test_graph.create_edges()

        # mutant 3
        result = []
        result_parent = []

        if test_graph.nodes[0].children is None:
            test_graph.nodes[0].children = set()
        for nodes in test_graph.nodes[0].children:
            result.append(nodes.mutant_name)
        self.assertEquals([{1}], result)

        if test_graph.nodes[0].parents is None:
            test_graph.nodes[0].parents = set()
        for parents in test_graph.nodes[0].parents:
            result_parent.append(parents.mutant_name)
        self.assertEquals([], result_parent)

        # mutant 1
        result2 = []
        result_parent2 = []

        if test_graph.nodes[2].parents is None:
            test_graph.nodes[2].parents = set()
        for parents2 in test_graph.nodes[2].parents:
            result_parent2.append(parents2.mutant_name)
        self.assertEquals([{3}], result_parent2)

        if test_graph.nodes[2].children is None:
            test_graph.nodes[2].children = set()
        for nodes2 in test_graph.nodes[2].children:
            result2.append(nodes2.mutant_name)
        self.assertEquals([{4}], result2)

        # mutant 4
        result4 = []
        result_parent4 = []

        if test_graph.nodes[1].parents is None:
            test_graph.nodes[1].parents = set()
        for parents4 in test_graph.nodes[1].parents:
            result_parent4.append(parents4.mutant_name)
        self.assertEquals([{1}], result_parent4)

        if test_graph.nodes[1].children is None:
            test_graph.nodes[1].children = set()
        for nodes4 in test_graph.nodes[1].children:
            result4.append(nodes4.mutant_name)
        self.assertEquals([], result4)

    def test_add_relation_for_parents_and_children_with_4_level_graph(self):
        mutant_6 = dominator_mutants.Node({6}, {1, 2, 3})
        mutant_4 = dominator_mutants.Node({4}, {1, 2, 3, 4})
        mutant_1 = dominator_mutants.Node({1}, {1, 2})
        mutant_3 = dominator_mutants.Node({3}, {2})

        test_graph = dominator_mutants.Graph()
        test_graph.add_node(mutant_6)
        test_graph.add_node(mutant_4)
        test_graph.add_node(mutant_1)
        test_graph.add_node(mutant_3)

        test_graph.create_edges()

        # mutant 3
        result = []
        result_parent = []

        if test_graph.nodes[3].children is None:
            test_graph.nodes[3].children = set()
        for nodes in test_graph.nodes[3].children:
            result.append(nodes.mutant_name)
        self.assertEquals([{1}], result)

        if test_graph.nodes[3].parents is None:
            test_graph.nodes[3].parents = set()
        for parents in test_graph.nodes[3].parents:
            result_parent.append(parents.mutant_name)
        self.assertEquals([], result_parent)

        # mutant 1
        result2 = []
        result_parent2 = []

        if test_graph.nodes[2].parents is None:
            test_graph.nodes[2].parents = set()
        for parents2 in test_graph.nodes[2].parents:
            result_parent2.append(parents2.mutant_name)
        self.assertEquals([{3}], result_parent2)

        if test_graph.nodes[2].children is None:
            test_graph.nodes[2].children = set()
        for nodes2 in test_graph.nodes[2].children:
            result2.append(nodes2.mutant_name)
        self.assertEquals([{6}], result2)

        # mutant 6
        result3 = []
        result_parent3 = []

        if test_graph.nodes[0].parents is None:
            test_graph.nodes[0].parents = set()
        for parents3 in test_graph.nodes[0].parents:
            result_parent3.append(parents3.mutant_name)
        self.assertEquals([{1}], result_parent3)

        if test_graph.nodes[0].children is None:
            test_graph.nodes[0].children = set()
        for nodes3 in test_graph.nodes[0].children:
            result3.append(nodes3.mutant_name)
        self.assertEquals([{4}], result3)

        # mutant 4
        result4 = []
        result_parent4 = []

        if test_graph.nodes[1].parents is None:
            test_graph.nodes[1].parents = set()
        for parents4 in test_graph.nodes[1].parents:
            result_parent4.append(parents4.mutant_name)
        self.assertEquals([{6}], result_parent4)

        if test_graph.nodes[1].children is None:
            test_graph.nodes[1].children = set()
        for nodes4 in test_graph.nodes[1].children:
            result4.append(nodes4.mutant_name)
        self.assertEquals([], result4)

    def test_calculate_dominating_mutants_two_mutants(self):
        kill_map = {frozenset({1}): {1, 2}, frozenset({4}): {1, 2, 3, 4}}
        result = dominator_mutants.calculate_dominating_mutants(kill_map)
        self.assertEquals({frozenset({1})}, result[1])

    def test_calculate_dominating_mutants_three_mutants_two_branches(self):
        kill_map = {frozenset({1}): {1, 2}, frozenset({2}): {1, 4},
                    frozenset({4}): {1, 2, 3, 4}}
        result = dominator_mutants.calculate_dominating_mutants(kill_map)
        self.assertEquals({frozenset({2}), frozenset({1})}, result[1])

    def test_calculate_dominating_mutants_three_mutants_one_branches(self):
        kill_map = {frozenset({1}): {1, 2}, frozenset({3}): {2},
                    frozenset({4}): {1, 2, 3, 4}}
        result = dominator_mutants.calculate_dominating_mutants(kill_map)
        self.assertEquals({frozenset({3})}, result[1])

    def test_calculate_dominating_mutants_four_mutants_two_branches_2_indistinguishable(
            self):
        kill_map = {frozenset({5}): {1, 4}, frozenset({3}): {2},
                    frozenset({4}): {1, 2, 3, 4}, frozenset({2}): {1, 4}}
        result = dominator_mutants.calculate_dominating_mutants(kill_map)
        self.assertEquals({frozenset({3}), frozenset({2, 5})}, result[1])

    def test_calculate_dominating_mutants_five_three_layers_mutants_two_branches_2_indistinguishable(
            self):
        kill_map = {frozenset({1}): {1, 2},
                    frozenset({5}): {1, 4}, frozenset({2}): {1, 4},
                    frozenset({3}): {2}, frozenset({4}): {1, 2, 3, 4}}
        result = dominator_mutants.calculate_dominating_mutants(kill_map)
        self.assertEquals({frozenset({3}), frozenset({2, 5})}, result[1])

    def test_tests_covered(self):
        mutant_6 = dominator_mutants.Node({6}, {1, 2, 3})
        mutant_4 = dominator_mutants.Node({4}, {1, 2, 3, 4})
        mutant_1 = dominator_mutants.Node({1}, {1, 2})
        mutant_3 = dominator_mutants.Node({3}, {2})

        test_graph = dominator_mutants.Graph()
        test_graph.add_node(mutant_6)
        test_graph.add_node(mutant_4)
        test_graph.add_node(mutant_1)
        test_graph.add_node(mutant_3)

        test_graph.create_edges()

        # mutant 3
        result = []

        self.assertEquals({1, 2, 3, 4}, test_graph.get_tests_covered(
            test_graph.nodes[3]))

    def test_csv_reader(self):
        result = dominator_mutants.convert_csv_to_killmap(
            "test-data/killMap.csv")
        self.assertEqual(
            {frozenset({729}): {68}, frozenset({730}): {68},
             frozenset({731}): {68}, frozenset({732}): {68},
             frozenset({733}): {68}, frozenset({734}): {68},
             frozenset({735}): {68}, frozenset({736}): {68, 93},
             frozenset({737}): {68, 93}, frozenset({738}): {68, 93},
             frozenset({739}): {68}, frozenset({680}): {69},
             frozenset({681}): {69}, frozenset({682}): {69},
             frozenset({683}): {69}, frozenset({684}): {69},
             frozenset({685}): {69}, frozenset({686}): {69},
             frozenset({687}): {69}, frozenset({689}): {69},
             frozenset({690}): {69}, frozenset({691}): {69},
             frozenset({692}): {69}, frozenset({693}): {69},
             frozenset({665}): {78}, frozenset({666}): {78},
             frozenset({667}): {78}, frozenset({668}): {78},
             frozenset({669}): {78}, frozenset({670}): {78},
             frozenset({671}): {78}, frozenset({672}): {78},
             frozenset({673}): {78}, frozenset({675}): {78},
             frozenset({676}): {78}, frozenset({677}): {78},
             frozenset({678}): {78}, frozenset({679}): {78},
             frozenset({78}): {153, 164, 92, 167},
             frozenset({79}): {153, 164, 92, 167},
             frozenset({80}): {153, 164, 92, 167},
             frozenset({82}): {153, 164, 92, 167},
             frozenset({83}): {153, 164, 92, 167},
             frozenset({88}): {153, 164, 92, 167},
             frozenset({89}): {153, 164, 92, 167},
             frozenset({90}): {153, 164, 92, 167},
             frozenset({92}): {153, 164, 92, 167},
             frozenset({94}): {153, 164, 92, 167},
             frozenset({96}): {153, 164, 92, 167},
             frozenset({98}): {153, 164, 92, 167},
             frozenset({102}): {153, 164, 92, 167},
             frozenset({119}): {164, 167, 112, 113, 114, 115, 153, 92},
             frozenset({120}): {164, 167, 112, 113, 114, 115, 153, 92},
             frozenset({121}): {164, 92, 167},
             frozenset({122}): {153, 164, 92, 167},
             frozenset({126}): {164, 167, 112, 113, 114, 115, 153, 92},
             frozenset({127}): {164, 167, 112, 113, 114, 115, 153, 92},
             frozenset({133}): {164, 167, 112, 113, 114, 115, 153, 92},
             frozenset({134}): {164, 167, 112, 113, 114, 115, 153, 92},
             frozenset({140}): {164, 167, 112, 113, 114, 115, 153, 92},
             frozenset({141}): {164, 167, 112, 113, 114, 115, 153, 92},
             frozenset({150}): {164, 167, 115, 153, 92},
             frozenset({152}): {164, 167, 115, 153, 92},
             frozenset({225}): {153, 164, 92, 167},
             frozenset({227}): {153, 164, 92, 167},
             frozenset({250}): {164, 92, 167}, frozenset({254}): {164, 92, 167},
             frozenset({255}): {153, 164, 92, 167},
             frozenset({256}): {153, 164, 92, 167},
             frozenset({257}): {164, 92, 167},
             frozenset({258}): {153, 164, 92, 167},
             frozenset({259}): {164, 92, 167},
             frozenset({261}): {153, 164, 92, 167},
             frozenset({267}): {164, 92, 167},
             frozenset({268}): {153, 164, 92, 167},
             frozenset({271}): {164, 92, 167}, frozenset({272}): {164, 92, 167},
             frozenset({274}): {164, 92, 167}, frozenset({275}): {164, 92, 167},
             frozenset({313}): {112, 164, 92, 167},
             frozenset({314}): {164, 92, 167},
             frozenset({316}): {112, 164, 92, 167},
             frozenset({317}): {112, 164, 92, 167},
             frozenset({318}): {112, 164, 92, 167},
             frozenset({319}): {112, 164, 92, 167},
             frozenset({321}): {164, 92, 167}, frozenset({322}): {164, 92, 167},
             frozenset({323}): {164, 92, 167}, frozenset({324}): {164, 92, 167},
             frozenset({325}): {164, 92, 167},
             frozenset({326}): {164, 92, 167}, frozenset({327}): {164, 92, 167},
             frozenset({329}): {112, 164, 92, 167},
             frozenset({330}): {112, 164, 92, 167},
             frozenset({331}): {164, 92, 167}, frozenset({332}): {164, 92, 167},
             frozenset({477}): {164, 167, 112, 115, 153, 92},
             frozenset({835}): {97, 164, 92, 167},
             frozenset({836}): {97, 164, 92, 167},
             frozenset({837}): {97, 164, 92, 167},
             frozenset({839}): {97, 164, 92, 167},
             frozenset({840}): {97, 164, 92, 167},
             frozenset({841}): {97, 164, 92, 167},
             frozenset({842}): {97, 164, 92, 167},
             frozenset({844}): {97, 164, 92, 167},
             frozenset({846}): {97, 164, 92, 167},
             frozenset({847}): {97, 164, 92, 167},
             frozenset({848}): {97, 164, 92, 167},
             frozenset({850}): {97, 164, 92, 167},
             frozenset({851}): {97, 164, 92, 167},
             frozenset({853}): {97, 164, 92, 167},
             frozenset({855}): {97, 164, 92, 167},
             frozenset({856}): {97, 164, 92, 167},
             frozenset({857}): {97, 164, 92, 167},
             frozenset({858}): {97, 164, 92, 167},
             frozenset({859}): {97, 164, 92, 167},
             frozenset({860}): {97, 164, 92, 167},
             frozenset({861}): {97, 164, 92, 167},
             frozenset({863}): {97, 164, 92, 167},
             frozenset({864}): {97, 164, 92, 167},
             frozenset({865}): {97, 164, 92, 167}, frozenset({593}): {93},
             frozenset({597}): {93},
             frozenset({598}): {93}, frozenset({599}): {93},
             frozenset({600}): {93}, frozenset({601}): {93},
             frozenset({626}): {93}, frozenset({630}): {93},
             frozenset({631}): {93}, frozenset({632}): {93},
             frozenset({633}): {93}, frozenset({634}): {93},
             frozenset({638}): {93}, frozenset({642}): {93},
             frozenset({643}): {93}, frozenset({644}): {93},
             frozenset({645}): {93}, frozenset({646}): {93},
             frozenset({720}): {93, 95}, frozenset({721}): {93, 95},
             frozenset({724}): {93, 95},
             frozenset({810}): {93, 166}, frozenset({811}): {93, 166},
             frozenset({814}): {93, 166},
             frozenset({826}): {93, 127}, frozenset({827}): {93, 127},
             frozenset({828}): {93, 127},
             frozenset({708}): {95}, frozenset({709}): {95},
             frozenset({710}): {95}, frozenset({711}): {95},
             frozenset({712}): {95}, frozenset({713}): {95},
             frozenset({714}): {95}, frozenset({715}): {95},
             frozenset({716}): {95}, frozenset({717}): {95},
             frozenset({718}): {95}, frozenset({719}): {95},
             frozenset({722}): {95}, frozenset({723}): {95},
             frozenset({725}): {95}, frozenset({726}): {95},
             frozenset({727}): {95}, frozenset({728}): {95},
             frozenset({830}): {97}, frozenset({831}): {97},
             frozenset({832}): {97}, frozenset({833}): {97},
             frozenset({834}): {97}, frozenset({843}): {97},
             frozenset({845}): {97}, frozenset({849}): {97},
             frozenset({852}): {97}, frozenset({854}): {97},
             frozenset({862}): {97}, frozenset({567}): {153, 99, 167},
             frozenset({569}): {153, 99, 167},
             frozenset({570}): {153, 99, 167}, frozenset({579}): {153, 99, 167},
             frozenset({694}): {101},
             frozenset({695}): {101}, frozenset({696}): {101},
             frozenset({697}): {101}, frozenset({698}): {101},
             frozenset({699}): {101}, frozenset({700}): {101},
             frozenset({701}): {101}, frozenset({703}): {101},
             frozenset({704}): {101}, frozenset({705}): {101},
             frozenset({706}): {101}, frozenset({707}): {101},
             frozenset({650}): {102}, frozenset({651}): {102},
             frozenset({652}): {102}, frozenset({653}): {102},
             frozenset({654}): {102}, frozenset({655}): {102},
             frozenset({656}): {102}, frozenset({657}): {102},
             frozenset({658}): {102}, frozenset({660}): {102},
             frozenset({661}): {102}, frozenset({662}): {102},
             frozenset({663}): {102}, frozenset({664}): {102},
             frozenset({496}): {107, 167},
             frozenset({497}): {107, 167}, frozenset({498}): {107, 167},
             frozenset({499}): {153, 107, 164, 167},
             frozenset({500}): {107}, frozenset({501}): {107},
             frozenset({502}): {107}, frozenset({503}): {107},
             frozenset({504}): {107}, frozenset({505}): {107, 164},
             frozenset({506}): {107},
             frozenset({507}): {153, 107, 164, 167},
             frozenset({509}): {153, 107, 164, 167},
             frozenset({511}): {153, 107}, frozenset({512}): {153, 107},
             frozenset({513}): {153, 107},
             frozenset({514}): {153, 107}, frozenset({515}): {153, 107},
             frozenset({516}): {153, 107},
             frozenset({517}): {153, 107}, frozenset({518}): {153, 107},
             frozenset({519}): {153, 107},
             frozenset({520}): {153, 107}, frozenset({521}): {153, 107},
             frozenset({522}): {153, 107, 164, 167},
             frozenset({523}): {153, 107}, frozenset({524}): {153, 107},
             frozenset({525}): {153, 107},
             frozenset({526}): {153, 107}, frozenset({527}): {153, 107},
             frozenset({528}): {153, 107},
             frozenset({529}): {153, 107}, frozenset({530}): {153, 107},
             frozenset({531}): {153, 107},
             frozenset({532}): {153, 107}, frozenset({533}): {107, 164, 167},
             frozenset({534}): {153, 107},
             frozenset({535}): {107}, frozenset({536}): {107},
             frozenset({537}): {107}, frozenset({539}): {107},
             frozenset({540}): {107}, frozenset({541}): {153, 107},
             frozenset({542}): {153, 107},
             frozenset({543}): {153, 107}, frozenset({544}): {153, 107},
             frozenset({545}): {153, 107, 164},
             frozenset({546}): {153, 107}, frozenset({547}): {153, 107},
             frozenset({548}): {153, 107, 164},
             frozenset({549}): {153, 107},
             frozenset({550}): {153, 107, 164, 167},
             frozenset({551}): {153, 107},
             frozenset({552}): {153, 107, 164, 167},
             frozenset({553}): {153, 107, 164, 167},
             frozenset({554}): {153, 107, 164, 167},
             frozenset({555}): {153, 107, 164, 167},
             frozenset({556}): {153, 107, 167}, frozenset({557}): {107},
             frozenset({558}): {107},
             frozenset({559}): {107}, frozenset({491}): {153, 164, 108, 167},
             frozenset({755}): {111},
             frozenset({756}): {111}, frozenset({757}): {111},
             frozenset({758}): {111}, frozenset({759}): {111},
             frozenset({760}): {111}, frozenset({761}): {111},
             frozenset({762}): {111}, frozenset({763}): {111},
             frozenset({765}): {111}, frozenset({766}): {111},
             frozenset({767}): {111}, frozenset({768}): {111},
             frozenset({769}): {111}, frozenset({124}): {112, 164, 167},
             frozenset({138}): {112, 153, 164, 167},
             frozenset({183}): {112, 153, 164, 167},
             frozenset({190}): {112, 164},
             frozenset({191}): {112, 153, 164, 167},
             frozenset({193}): {112, 153, 164, 167},
             frozenset({194}): {112, 153, 164, 167},
             frozenset({195}): {112, 153, 164, 167},
             frozenset({210}): {112, 153, 164, 167},
             frozenset({214}): {112, 153, 164, 167},
             frozenset({220}): {112, 164, 167},
             frozenset({302}): {112, 164, 167},
             frozenset({303}): {112, 164, 167},
             frozenset({304}): {112, 164, 167},
             frozenset({310}): {112, 164, 167},
             frozenset({311}): {112, 164, 167},
             frozenset({315}): {112, 167}, frozenset({328}): {112, 164, 167},
             frozenset({356}): {112, 164, 167},
             frozenset({357}): {112, 164, 167},
             frozenset({360}): {112, 164, 167}, frozenset({361}): {112, 167},
             frozenset({177}): {113}, frozenset({178}): {113},
             frozenset({179}): {113},
             frozenset({180}): {113, 164, 167}, frozenset({232}): {114, 167},
             frozenset({233}): {114, 167},
             frozenset({234}): {114, 167}, frozenset({235}): {114, 167},
             frozenset({151}): {115, 164, 167},
             frozenset({239}): {115, 164}, frozenset({246}): {115, 164},
             frozenset({383}): {115, 164},
             frozenset({400}): {153, 115, 164, 167},
             frozenset({401}): {153, 115, 164, 167},
             frozenset({402}): {153, 115, 164, 167},
             frozenset({403}): {153, 115, 164, 167},
             frozenset({404}): {153, 115, 164, 167},
             frozenset({440}): {153, 115, 164, 167},
             frozenset({441}): {153, 115, 164, 167},
             frozenset({462}): {153, 115, 164, 167},
             frozenset({463}): {153, 115, 164, 167},
             frozenset({475}): {153, 115, 164}, frozenset({476}): {153, 115},
             frozenset({784}): {116}, frozenset({785}): {116},
             frozenset({786}): {116}, frozenset({788}): {116},
             frozenset({789}): {116}, frozenset({790}): {116},
             frozenset({791}): {116}, frozenset({793}): {116},
             frozenset({794}): {116}, frozenset({795}): {116},
             frozenset({796}): {116}, frozenset({797}): {116},
             frozenset({740}): {117}, frozenset({741}): {117},
             frozenset({742}): {117}, frozenset({743}): {117},
             frozenset({744}): {117}, frozenset({745}): {117},
             frozenset({746}): {117}, frozenset({747}): {117},
             frozenset({748}): {117}, frozenset({750}): {117},
             frozenset({751}): {117}, frozenset({752}): {117},
             frozenset({753}): {117}, frozenset({754}): {117},
             frozenset({584}): {123}, frozenset({586}): {123},
             frozenset({587}): {123}, frozenset({588}): {123},
             frozenset({589}): {123}, frozenset({590}): {123},
             frozenset({591}): {123}, frozenset({592}): {123},
             frozenset({822}): {127}, frozenset({823}): {127},
             frozenset({824}): {127}, frozenset({825}): {127},
             frozenset({829}): {127}, frozenset({770}): {128},
             frozenset({771}): {128}, frozenset({772}): {128},
             frozenset({774}): {128}, frozenset({775}): {128},
             frozenset({776}): {128}, frozenset({777}): {128},
             frozenset({779}): {128}, frozenset({780}): {128},
             frozenset({781}): {128}, frozenset({782}): {128},
             frozenset({783}): {128},
             frozenset({486}): {153, 130, 164, 167},
             frozenset({84}): {153, 164, 167}, frozenset({85}): {153, 164, 167},
             frozenset({95}): {153}, frozenset({99}): {153, 167},
             frozenset({100}): {153, 167},
             frozenset({101}): {153, 167}, frozenset({103}): {153},
             frozenset({104}): {153},
             frozenset({105}): {153, 167}, frozenset({106}): {153, 167},
             frozenset({107}): {153, 167},
             frozenset({108}): {153, 167}, frozenset({109}): {153},
             frozenset({110}): {153, 167},
             frozenset({111}): {153}, frozenset({112}): {153, 167},
             frozenset({113}): {153}, frozenset({114}): {153},
             frozenset({115}): {153}, frozenset({116}): {153},
             frozenset({117}): {153}, frozenset({118}): {153},
             frozenset({125}): {153, 164, 167},
             frozenset({129}): {153, 164, 167}, frozenset({130}): {153, 164},
             frozenset({131}): {153, 164, 167},
             frozenset({132}): {153, 164, 167},
             frozenset({136}): {153, 164, 167},
             frozenset({139}): {153, 164, 167}, frozenset({163}): {153, 167},
             frozenset({165}): {153, 164, 167},
             frozenset({167}): {153, 164, 167},
             frozenset({168}): {153, 164, 167},
             frozenset({174}): {153, 164, 167},
             frozenset({182}): {153, 167}, frozenset({184}): {153, 167},
             frozenset({185}): {153, 167},
             frozenset({189}): {153, 167}, frozenset({192}): {153, 167},
             frozenset({213}): {153, 164, 167},
             frozenset({221}): {153, 167}, frozenset({222}): {153, 167},
             frozenset({251}): {153, 164, 167},
             frozenset({252}): {153, 164, 167},
             frozenset({253}): {153, 164, 167},
             frozenset({260}): {153, 164, 167},
             frozenset({262}): {153, 164, 167},
             frozenset({263}): {153, 164, 167},
             frozenset({264}): {153, 164, 167},
             frozenset({265}): {153, 164, 167},
             frozenset({266}): {153, 164, 167},
             frozenset({269}): {153, 164, 167},
             frozenset({270}): {153, 164, 167},
             frozenset({371}): {153, 164, 167},
             frozenset({373}): {153, 164, 167},
             frozenset({398}): {153, 164, 167}, frozenset({399}): {153, 167},
             frozenset({405}): {153, 164, 167},
             frozenset({406}): {153, 164, 167},
             frozenset({408}): {153, 164, 167},
             frozenset({409}): {153, 164, 167},
             frozenset({412}): {153, 164, 167},
             frozenset({413}): {153, 164, 167}, frozenset({415}): {153, 167},
             frozenset({416}): {153, 167}, frozenset({418}): {153, 167},
             frozenset({419}): {153, 167},
             frozenset({432}): {153}, frozenset({433}): {153, 167},
             frozenset({434}): {153},
             frozenset({437}): {153, 167}, frozenset({439}): {153, 164, 167},
             frozenset({442}): {153, 167},
             frozenset({443}): {153, 167}, frozenset({444}): {153, 167},
             frozenset({445}): {153, 167},
             frozenset({448}): {153, 167}, frozenset({449}): {153, 167},
             frozenset({450}): {153, 167},
             frozenset({451}): {153, 167}, frozenset({454}): {153, 167},
             frozenset({455}): {153, 167},
             frozenset({456}): {153, 167}, frozenset({459}): {153, 167},
             frozenset({460}): {153, 167},
             frozenset({461}): {153, 164, 167}, frozenset({464}): {153},
             frozenset({465}): {153},
             frozenset({466}): {153}, frozenset({467}): {153},
             frozenset({470}): {153, 167},
             frozenset({471}): {153, 167}, frozenset({472}): {153, 167},
             frozenset({473}): {153, 167},
             frozenset({474}): {153, 164}, frozenset({487}): {153, 164, 167},
             frozenset({492}): {153},
             frozenset({617}): {155}, frozenset({619}): {155},
             frozenset({620}): {155}, frozenset({621}): {155},
             frozenset({622}): {155}, frozenset({623}): {155},
             frozenset({624}): {155}, frozenset({625}): {155},
             frozenset({73}): {164}, frozenset({74}): {164},
             frozenset({75}): {164}, frozenset({76}): {164},
             frozenset({123}): {164, 167}, frozenset({137}): {164, 167},
             frozenset({144}): {164, 167},
             frozenset({153}): {164}, frozenset({154}): {164, 167},
             frozenset({156}): {164},
             frozenset({157}): {164, 167}, frozenset({158}): {164, 167},
             frozenset({159}): {164, 167},
             frozenset({160}): {164, 167}, frozenset({166}): {164},
             frozenset({169}): {164}, frozenset({170}): {164},
             frozenset({171}): {164}, frozenset({172}): {164},
             frozenset({173}): {164}, frozenset({175}): {164, 167},
             frozenset({176}): {164, 167}, frozenset({200}): {164},
             frozenset({201}): {164, 167},
             frozenset({202}): {164, 167}, frozenset({204}): {164, 167},
             frozenset({205}): {164},
             frozenset({212}): {164}, frozenset({216}): {164, 167},
             frozenset({219}): {164},
             frozenset({236}): {164, 167}, frozenset({244}): {164},
             frozenset({280}): {164}, frozenset({281}): {164},
             frozenset({282}): {164}, frozenset({283}): {164},
             frozenset({285}): {164}, frozenset({286}): {164},
             frozenset({287}): {164}, frozenset({289}): {164},
             frozenset({297}): {164}, frozenset({299}): {164},
             frozenset({300}): {164}, frozenset({306}): {164},
             frozenset({307}): {164}, frozenset({309}): {164},
             frozenset({320}): {164, 167}, frozenset({355}): {164, 167},
             frozenset({359}): {164, 167},
             frozenset({372}): {164}, frozenset({376}): {164},
             frozenset({381}): {164}, frozenset({382}): {164},
             frozenset({386}): {164}, frozenset({388}): {164},
             frozenset({397}): {164}, frozenset({407}): {164, 167},
             frozenset({410}): {164}, frozenset({478}): {164},
             frozenset({866}): {164}, frozenset({867}): {164},
             frozenset({868}): {164}, frozenset({869}): {164},
             frozenset({870}): {164}, frozenset({871}): {164},
             frozenset({872}): {164}, frozenset({873}): {164},
             frozenset({875}): {164}, frozenset({876}): {164},
             frozenset({877}): {164}, frozenset({878}): {164},
             frozenset({879}): {164}, frozenset({881}): {164},
             frozenset({884}): {164}, frozenset({888}): {164},
             frozenset({889}): {164}, frozenset({890}): {164},
             frozenset({891}): {164}, frozenset({892}): {164},
             frozenset({893}): {164}, frozenset({894}): {164},
             frozenset({895}): {164}, frozenset({896}): {164},
             frozenset({897}): {164}, frozenset({898}): {164},
             frozenset({899}): {164}, frozenset({900}): {164},
             frozenset({902}): {164}, frozenset({903}): {164},
             frozenset({904}): {164}, frozenset({907}): {164},
             frozenset({912}): {164}, frozenset({913}): {164},
             frozenset({914}): {164}, frozenset({915}): {164},
             frozenset({916}): {164}, frozenset({917}): {164},
             frozenset({918}): {164}, frozenset({919}): {164},
             frozenset({923}): {164}, frozenset({924}): {164},
             frozenset({925}): {164}, frozenset({926}): {164},
             frozenset({931}): {164}, frozenset({932}): {164},
             frozenset({933}): {164}, frozenset({934}): {164},
             frozenset({935}): {164}, frozenset({936}): {164},
             frozenset({937}): {164}, frozenset({938}): {164},
             frozenset({939}): {164}, frozenset({940}): {164},
             frozenset({941}): {164}, frozenset({942}): {164},
             frozenset({943}): {164}, frozenset({957}): {164},
             frozenset({958}): {164}, frozenset({959}): {164},
             frozenset({960}): {164}, frozenset({961}): {164},
             frozenset({962}): {164}, frozenset({963}): {164},
             frozenset({964}): {164}, frozenset({965}): {164},
             frozenset({966}): {164}, frozenset({967}): {164},
             frozenset({968}): {164}, frozenset({969}): {164},
             frozenset({970}): {164}, frozenset({971}): {164},
             frozenset({972}): {164}, frozenset({973}): {164},
             frozenset({974}): {164}, frozenset({975}): {164},
             frozenset({976}): {164}, frozenset({977}): {164},
             frozenset({978}): {164}, frozenset({979}): {164},
             frozenset({980}): {164}, frozenset({981}): {164},
             frozenset({982}): {164}, frozenset({983}): {164},
             frozenset({984}): {164}, frozenset({985}): {164},
             frozenset({987}): {164}, frozenset({988}): {164},
             frozenset({989}): {164}, frozenset({990}): {164},
             frozenset({991}): {164}, frozenset({992}): {164},
             frozenset({993}): {164}, frozenset({994}): {164},
             frozenset({995}): {164}, frozenset({996}): {164},
             frozenset({999}): {164}, frozenset({1000}): {164},
             frozenset({1001}): {164}, frozenset({1003}): {164},
             frozenset({1009}): {164}, frozenset({1010}): {164},
             frozenset({1011}): {164}, frozenset({1017}): {164},
             frozenset({1018}): {164}, frozenset({1019}): {164},
             frozenset({1021}): {164}, frozenset({1023}): {164},
             frozenset({1024}): {164}, frozenset({1026}): {164},
             frozenset({1027}): {164}, frozenset({1029}): {164},
             frozenset({1030}): {164}, frozenset({1031}): {164},
             frozenset({1032}): {164}, frozenset({1033}): {164},
             frozenset({1034}): {164}, frozenset({1035}): {164},
             frozenset({1036}): {164}, frozenset({1037}): {164},
             frozenset({1038}): {164}, frozenset({1040}): {164},
             frozenset({1044}): {164}, frozenset({1045}): {164},
             frozenset({1047}): {164}, frozenset({1048}): {164},
             frozenset({1049}): {164}, frozenset({1050}): {164},
             frozenset({1051}): {164}, frozenset({1052}): {164},
             frozenset({1053}): {164}, frozenset({1054}): {164},
             frozenset({1056}): {164}, frozenset({1057}): {164},
             frozenset({1058}): {164}, frozenset({1059}): {164},
             frozenset({1060}): {164}, frozenset({1064}): {164},
             frozenset({1065}): {164}, frozenset({1066}): {164},
             frozenset({1070}): {164}, frozenset({1072}): {164},
             frozenset({1073}): {164}, frozenset({1074}): {164},
             frozenset({1075}): {164}, frozenset({1076}): {164},
             frozenset({1084}): {164}, frozenset({1086}): {164},
             frozenset({1089}): {164}, frozenset({1092}): {164},
             frozenset({1098}): {164}, frozenset({1099}): {164},
             frozenset({1100}): {164}, frozenset({1101}): {164},
             frozenset({1102}): {164}, frozenset({1103}): {164},
             frozenset({1107}): {164}, frozenset({1111}): {164},
             frozenset({1112}): {164}, frozenset({1113}): {164},
             frozenset({1114}): {164}, frozenset({1118}): {164},
             frozenset({1119}): {164}, frozenset({1120}): {164},
             frozenset({1121}): {164}, frozenset({1122}): {164},
             frozenset({1123}): {164}, frozenset({1124}): {164},
             frozenset({1125}): {164}, frozenset({1126}): {164},
             frozenset({1127}): {164}, frozenset({1128}): {164},
             frozenset({1129}): {164}, frozenset({1130}): {164},
             frozenset({1131}): {164}, frozenset({801}): {166},
             frozenset({802}): {166}, frozenset({803}): {166},
             frozenset({804}): {166}, frozenset({805}): {166},
             frozenset({806}): {166}, frozenset({807}): {166},
             frozenset({808}): {166}, frozenset({809}): {166},
             frozenset({812}): {166}, frozenset({813}): {166},
             frozenset({815}): {166}, frozenset({816}): {166},
             frozenset({817}): {166}, frozenset({818}): {166},
             frozenset({91}): {167}, frozenset({93}): {167},
             frozenset({187}): {167}, frozenset({188}): {167},
             frozenset({435}): {167}, frozenset({446}): {167},
             frozenset({447}): {167}}
            , result)

    def test_compare_dominant_mutant_txt_vs_csv(self):
        result = txt_to_dominator_mutants.import_mutant_relation(
            "test-data/groups_test0.txt")
        result2 = txt_to_dominator_mutants. \
            generate_dominator_mutants(result[0], result[1])[0]
        result3 = dominator_mutants.generate_dominator_set_with_csv_3_col(
            "test-data/killMap_lang_16.csv")

        self.assertEquals(result2, result3[1])
