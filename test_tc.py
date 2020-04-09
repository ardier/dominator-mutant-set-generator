import unittest

import tc


class TestCase(unittest.TestCase):

    def test_create_empty_node_with_no_name_and_tests(self):
        test_node = tc.Node()
        self.assertEquals(set(), test_node.mutant_name)
        self.assertEquals(set(), test_node.tests)
        self.assertEquals(set(), test_node.children)
        self.assertEquals(set(), test_node.parents)

    def test_create_simple_node_with_all_attributes(self):
        test_node = tc.Node({1}, {1, 2})
        self.assertEquals(test_node.mutant_name, {1})
        self.assertEquals(test_node.tests, {1, 2})
        self.assertEquals(set(), test_node.children)
        self.assertEquals(set(), test_node.parents)

    def test_create_node_from_with_tests_only_from_kill_map(self):
        kill_map = {frozenset({1}): {1, 2}, frozenset({2}): {1, 4},
                    frozenset({3}): {2}, frozenset({4}): {1, 2, 3, 4}}
        test_graph = tc.calculate_dominating_mutants(kill_map)[0]
        self.assertEquals(test_graph.nodes[0].mutant_name,
                          list(kill_map.keys())[0])
        self.assertEquals(test_graph.nodes[0].tests,
                          kill_map.get(list(kill_map)[0]))
        self.assertEquals(test_graph.nodes[3].mutant_name,
                          list(kill_map.keys())[3])
        self.assertEquals(test_graph.nodes[3].tests,
                          kill_map.get(list(kill_map)[3]))

    def test_is_distinguishable(self):
        mutant_2 = tc.Node(frozenset({2}), {1, 4})
        mutant_5 = tc.Node(frozenset({5}), {1, 4})
        mutant_1 = tc.Node(frozenset({1}), {1, 2})
        self.assertTrue(mutant_2.is_distinguishable_from(mutant_1))
        self.assertFalse(mutant_1.is_distinguishable_from(mutant_1))
        self.assertFalse(mutant_2.is_distinguishable_from(mutant_5))

    def test_merge_indistinguishable(self):

        mutant_2 = tc.Node({2}, {1, 4})
        mutant_5 = tc.Node({5}, {1, 4})

        test_graph = tc.Graph()
        test_graph.add_node(mutant_2)
        test_graph.add_node(mutant_5)
        test_graph.create_edges()

        result = []
        for node in test_graph.nodes:
            result.append(node)

        self.assertEquals(result[0].mutant_name, {2, 5})

    def test_add_node(self):
        mutant_1 = tc.Node({1}, {1, 2})
        test_graph = tc.Graph()
        test_graph.add_node(mutant_1)
        self.assertEquals(mutant_1, test_graph.nodes[0])

    def test_connect_the_same_node_to_itself(self):
        mutant_2 = tc.Node({2}, {1, 4})
        test_graph = tc.Graph()
        test_graph.add_node(mutant_2)
        test_graph.create_edges()
        test_graph_nodes = test_graph.nodes
        result = []
        for nodes in test_graph_nodes:
            result.append(nodes.mutant_name)

        self.assertEquals([{2}], result)

    def test_connect_nodes_indistinguishable(self):
        mutant_2 = tc.Node({2}, {1, 4})
        mutant_5 = tc.Node({5}, {1, 4})
        test_graph = tc.Graph()
        test_graph.add_node(mutant_2)
        test_graph.add_node(mutant_5)
        test_graph.create_edges()
        test_graph_nodes = test_graph.nodes
        result = []
        for nodes in test_graph_nodes:
            result.append(nodes.mutant_name)
        self.assertEquals([{2, 5}], result)

    def test_connect_two_nodes_distinguishable(self):
        mutant_1 = tc.Node({1}, {1, 2})
        mutant_2 = tc.Node({2}, {1, 4})
        test_graph = tc.Graph()
        test_graph.add_node(mutant_1)
        test_graph.add_node(mutant_2)

        test_graph.create_edges()
        test_graph_nodes = test_graph.nodes
        result = []
        for nodes in test_graph_nodes:
            result.append(nodes.mutant_name)
        self.assertEquals([{1}, {2}], result)

    def test_add_relation_just_two_nodes_children(self):
        mutant_3 = tc.Node({3}, {2})
        mutant_1 = tc.Node({1}, {1, 2})
        test_graph = tc.Graph()
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
        mutant_3 = tc.Node({3}, {2})
        mutant_1 = tc.Node({1}, {1, 2})
        mutant_4 = tc.Node({4}, {1, 2, 3, 4})

        test_graph = tc.Graph()
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
        mutant_3 = tc.Node({3}, {2})
        mutant_1 = tc.Node({1}, {1, 2})
        mutant_6 = tc.Node({6}, {1, 2, 3})
        mutant_4 = tc.Node({4}, {1, 2, 3, 4})

        test_graph = tc.Graph()
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
        mutant_3 = tc.Node({3}, {2})
        mutant_1 = tc.Node({1}, {1, 2})
        test_graph = tc.Graph()
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
        mutant_4 = tc.Node({4}, {1, 2, 3, 4})
        mutant_1 = tc.Node({1}, {1, 2})
        mutant_3 = tc.Node({3}, {2})

        test_graph = tc.Graph()
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
        mutant_4 = tc.Node({4}, {1, 2, 3, 4})
        mutant_1 = tc.Node({1}, {1, 2})
        mutant_3 = tc.Node({3}, {2})
        mutant_6 = tc.Node({6}, {1, 2})

        test_graph = tc.Graph()
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
        mutant_4 = tc.Node({4}, {1, 2, 3, 4})
        mutant_6 = tc.Node({6}, {1, 2, 3})
        mutant_1 = tc.Node({1}, {1, 2})
        mutant_3 = tc.Node({3}, {2})

        test_graph = tc.Graph()
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
        mutant_4 = tc.Node({4}, {1, 2, 3, 4})
        mutant_3 = tc.Node({3}, {2})
        mutant_1 = tc.Node({1}, {1, 2})

        test_graph = tc.Graph()
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
        mutant_1 = tc.Node({1}, {1, 2})
        mutant_4 = tc.Node({4}, {1, 2, 3, 4})
        mutant_3 = tc.Node({3}, {2})

        test_graph = tc.Graph()

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
        mutant_6 = tc.Node({6}, {1, 2, 3})
        mutant_4 = tc.Node({4}, {1, 2, 3, 4})
        mutant_1 = tc.Node({1}, {1, 2})
        mutant_3 = tc.Node({3}, {2})

        test_graph = tc.Graph()
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
        result = tc.calculate_dominating_mutants(kill_map)
        self.assertEquals({frozenset({1})}, result[1])

    def test_calculate_dominating_mutants_three_mutants_two_branches(self):
        kill_map = {frozenset({1}): {1, 2}, frozenset({2}): {1, 4},
                    frozenset({4}): {1, 2, 3, 4}}
        result = tc.calculate_dominating_mutants(kill_map)
        self.assertEquals({frozenset({2}), frozenset({1})}, result[1])

    def test_calculate_dominating_mutants_three_mutants_one_branches(self):
        kill_map = {frozenset({1}): {1, 2}, frozenset({3}): {2},
                    frozenset({4}): {1, 2, 3, 4}}
        result = tc.calculate_dominating_mutants(kill_map)
        self.assertEquals({frozenset({3})}, result[1])

    def test_calculate_dominating_mutants_four_mutants_two_branches_2_indistinguishable(
            self):
        kill_map = {frozenset({5}): {1, 4}, frozenset({3}): {2},
                    frozenset({4}): {1, 2, 3, 4}, frozenset({2}): {1, 4}}
        result = tc.calculate_dominating_mutants(kill_map)
        self.assertEquals({frozenset({3}), frozenset({2, 5})}, result[1])

    def test_calculate_dominating_mutants_five_three_layers_mutants_two_branches_2_indistinguishable(
            self):
        kill_map = {frozenset({1}): {1, 2},
                    frozenset({5}): {1, 4}, frozenset({2}): {1, 4},
                    frozenset({3}): {2}, frozenset({4}): {1, 2, 3, 4}}
        result = tc.calculate_dominating_mutants(kill_map)
        self.assertEquals({frozenset({3}), frozenset({2, 5})}, result[1])

    def test_tests_covered(self):
        mutant_6 = tc.Node({6}, {1, 2, 3})
        mutant_4 = tc.Node({4}, {1, 2, 3, 4})
        mutant_1 = tc.Node({1}, {1, 2})
        mutant_3 = tc.Node({3}, {2})

        test_graph = tc.Graph()
        test_graph.add_node(mutant_6)
        test_graph.add_node(mutant_4)
        test_graph.add_node(mutant_1)
        test_graph.add_node(mutant_3)

        test_graph.create_edges()

        # mutant 3
        result = []

        self.assertEquals({1, 2, 3, 4}, test_graph.get_tests_covered(
            test_graph.nodes[3]))

    def test_completeness_plot_single_mutant(self):
        kill_map = {frozenset({1}): {1, 2}}
        result = tc.generate_test_completeness_plot(kill_map)
        self.assertEquals([(0, 0), (1, 2)], result)

    def test_completeness_plot_single_parent_single_child(self):
        kill_map = {frozenset({1}): {1, 2},
                    frozenset({4}): {1, 2, 3, 4}}

        result = tc.generate_test_completeness_plot(kill_map)
        self.assertEquals([(0, 0), (1, 4)], result)

    def test_completeness_plot_single_branch_three_mutants(self):
        kill_map = {frozenset({1}): {1, 2},
                    frozenset({1}): {1, 2, 3},
                    frozenset({4}): {1, 2, 3, 4}}

        result = tc.generate_test_completeness_plot(kill_map)
        self.assertEquals([(0, 0), (1, 4)], result)

    def test_completeness_plot_two_parents_one_child(self):
        kill_map = {frozenset({1}): {1, 2}, frozenset({2}): {1, 4},
                    frozenset({4}): {1, 2, 3, 4}}
        result = tc.generate_test_completeness_plot(kill_map)
        self.assertEquals([(0, 0), (1, 4), (2, 4)], result)

    def test_completeness_plot_one_parent_two_children(self):
        kill_map = {frozenset({1}): {1, 2}, frozenset({2}): {1, 4},
                    frozenset({4}): {1}}
        result = tc.generate_test_completeness_plot(kill_map)
        self.assertEquals([(0, 0), (1, 3)], result)

    def test_completeness_plot_two_separate_branches(self):
        kill_map = {frozenset({1}): {1, 2}, frozenset({2}): {1, 4},
                    frozenset({4}): {1, 2, 3, 4},
                    frozenset({6}): {5, 6, 7, 8, 9}}
        result = tc.generate_test_completeness_plot(kill_map)
        self.assertEquals([(0, 0), (1, 5), (2, 9), (3, 9)], result)

    def test_completeness_plot_two_separate_branches_with_plotting(self):
        kill_map = {frozenset({1}): {1, 2}, frozenset({2}): {1, 4},
                    frozenset({4}): {1, 2, 3, 4},
                    frozenset({6}): {5, 6, 7, 8, 9}}
        result = tc.generate_test_completeness_plot(kill_map)
        self.assertEquals([(0, 0), (1, 5), (2, 9), (3, 9)], result)
        tc.plot(result)

    def test_csv_reader(self):
        result = tc.convert_csv_to_killmap("test-data/killMap.csv")
        self.assertEquals({frozenset({68}): {736, 737, 738, 739, 729, 730, 731,
                                             732, 733, 734, 735},
                           frozenset({69}): {680, 681, 682, 683, 684, 685, 686,
                                             687, 689, 690, 691, 692, 693},
                           frozenset({78}): {672, 673, 675, 676, 677, 678, 679,
                                             665, 666, 667, 668, 669, 670, 671},
                           frozenset({92}): {256, 257, 258, 255, 259, 133, 134,
                                             261, 841, 865, 267, 140, 141, 268,
                                             271, 272, 842, 274, 275, 150, 844,
                                             152, 856, 853, 848, 313, 314, 851,
                                             316, 317, 318, 319, 857, 321, 322,
                                             323, 324, 325, 326, 327, 835, 329,
                                             330, 331, 332, 836, 78, 79, 80,
                                             840, 82, 83, 254, 839, 846, 847,
                                             88, 89, 90, 850, 92, 477, 94, 855,
                                             96, 225, 98, 227, 858, 859, 102,
                                             860, 863, 864, 250, 861, 837, 119,
                                             120, 121, 122, 126, 127},
                           frozenset({93}): {642, 643, 644, 645, 646, 810, 811,
                                             814, 826, 827, 828, 720, 593, 721,
                                             724, 597, 598, 599, 600, 601, 736,
                                             737, 738, 626, 630, 631, 632, 633,
                                             634, 638},
                           frozenset({95}): {708, 709, 710, 711, 712, 713, 714,
                                             715, 716, 717, 718, 719, 720, 721,
                                             722, 723, 724, 725, 726, 727, 728},
                           frozenset({97}): {830, 831, 832, 833, 834, 835, 836,
                                             837, 839, 840, 841, 842, 843, 844,
                                             845, 846, 847, 848, 849, 850, 851,
                                             852, 853, 854, 855, 856, 857, 858,
                                             859, 860, 861, 862, 863, 864, 865},
                           frozenset({99}): {569, 570, 579, 567},
                           frozenset({101}): {704, 705, 706, 707, 694, 695, 696,
                                              697, 698, 699, 700, 701, 703},
                           frozenset({102}): {650, 651, 652, 653, 654, 655, 656,
                                              657, 658, 660, 661, 662, 663,
                                              664},
                           frozenset({107}): {512, 513, 514, 515, 516, 517, 518,
                                              519, 520, 521, 522, 523, 524, 525,
                                              526, 527, 528, 529, 530, 531, 532,
                                              533, 534, 535, 536, 537, 539, 540,
                                              541, 542, 543, 544, 545, 546, 547,
                                              548, 549, 550, 551, 552, 553, 554,
                                              555, 556, 557, 558, 559, 496, 497,
                                              498, 499, 500, 501, 502, 503, 504,
                                              505, 506, 507, 509, 511},
                           frozenset({108}): {491},
                           frozenset({111}): {768, 769, 755, 756, 757, 758, 759,
                                              760, 761, 762, 763, 765, 766,
                                              767},
                           frozenset({112}): {133, 134, 138, 140, 141, 302, 303,
                                              304, 310, 183, 311, 313, 315, 316,
                                              317, 190, 191, 318, 193, 194, 195,
                                              319, 328, 329, 330, 210, 214, 220,
                                              477, 356, 357, 360, 361, 119, 120,
                                              124, 126, 127},
                           frozenset({113}): {133, 134, 140, 141, 177, 178, 179,
                                              180, 119, 120, 126, 127},
                           frozenset({114}): {133, 134, 232, 233, 234, 235, 140,
                                              141, 119, 120, 126, 127},
                           frozenset({115}): {133, 134, 140, 141, 400, 401, 402,
                                              403, 404, 150, 151, 152, 440, 441,
                                              462, 463, 475, 476, 477, 239, 246,
                                              119, 120, 127, 126, 383},
                           frozenset({116}): {784, 785, 786, 788, 789, 790, 791,
                                              793, 794, 795, 796, 797},
                           frozenset({117}): {740, 741, 742, 743, 744, 745, 746,
                                              747, 748, 750, 751, 752, 753,
                                              754},
                           frozenset({123}): {584, 586, 587, 588, 589, 590, 591,
                                              592},
                           frozenset({127}): {822, 823, 824, 825, 826, 827, 828,
                                              829},
                           frozenset({128}): {770, 771, 772, 774, 775, 776, 777,
                                              779, 780, 781, 782, 783},
                           frozenset({130}): {486},
                           frozenset({153}): {512, 513, 514, 515, 516, 517, 518,
                                              519, 520, 521, 522, 523, 524, 525,
                                              526, 527, 528, 529, 530, 531, 532,
                                              534, 541, 542, 543, 544, 545, 546,
                                              547, 548, 549, 550, 551, 552, 553,
                                              554, 555, 556, 567, 569, 570, 579,
                                              78, 79, 80, 82, 83, 84, 85, 88,
                                              89, 90, 92, 94, 95, 96, 98, 99,
                                              100, 101, 102, 103, 104, 105, 106,
                                              107, 108, 109, 110, 111, 112, 113,
                                              114, 115, 116, 117, 118, 119, 120,
                                              122, 125, 126, 127, 129, 130, 131,
                                              132, 133, 134, 136, 138, 139, 140,
                                              141, 150, 152, 163, 165, 167, 168,
                                              174, 182, 183, 184, 185, 189, 191,
                                              192, 193, 194, 195, 210, 213, 214,
                                              221, 222, 225, 227, 251, 252, 253,
                                              255, 256, 258, 260, 261, 262, 263,
                                              264, 265, 266, 268, 269, 270, 371,
                                              373, 398, 399, 400, 401, 402, 403,
                                              404, 405, 406, 408, 409, 412, 413,
                                              415, 416, 418, 419, 432, 433, 434,
                                              437, 439, 440, 441, 442, 443, 444,
                                              445, 448, 449, 450, 451, 454, 455,
                                              456, 459, 460, 461, 462, 463, 464,
                                              465, 466, 467, 470, 471, 472, 473,
                                              474, 475, 476, 477, 486, 487, 491,
                                              492, 499, 507, 509, 511},
                           frozenset({155}): {617, 619, 620, 621, 622, 623, 624,
                                              625},
                           frozenset({164}): {73, 74, 75, 76, 78, 79, 80, 82,
                                              83, 84, 85, 88, 89, 90, 92, 94,
                                              96, 98, 102, 119, 120, 121, 122,
                                              123, 124, 125, 126, 127, 129, 130,
                                              131, 132, 133, 134, 136, 137, 138,
                                              139, 140, 141, 144, 150, 151, 152,
                                              153, 154, 156, 157, 158, 159, 160,
                                              165, 166, 167, 168, 169, 170, 171,
                                              172, 173, 174, 175, 176, 180, 183,
                                              190, 191, 193, 194, 195, 200, 201,
                                              202, 204, 205, 210, 212, 213, 214,
                                              216, 219, 220, 225, 227, 236, 239,
                                              244, 246, 250, 251, 252, 253, 254,
                                              255, 256, 257, 258, 259, 260, 261,
                                              262, 263, 264, 265, 266, 267, 268,
                                              269, 270, 271, 272, 274, 275, 280,
                                              281, 282, 283, 285, 286, 287, 289,
                                              297, 299, 300, 302, 303, 304, 306,
                                              307, 309, 310, 311, 313, 314, 316,
                                              317, 318, 319, 320, 321, 322, 323,
                                              324, 325, 326, 327, 328, 329, 330,
                                              331, 332, 355, 356, 357, 359, 360,
                                              371, 372, 373, 376, 381, 382, 383,
                                              386, 388, 397, 398, 400, 401, 402,
                                              403, 404, 405, 406, 407, 408, 409,
                                              410, 412, 413, 439, 440, 441, 461,
                                              462, 463, 474, 475, 477, 478, 486,
                                              487, 491, 499, 505, 507, 509, 522,
                                              533, 545, 548, 550, 552, 553, 554,
                                              555, 835, 836, 837, 839, 840, 841,
                                              842, 844, 846, 847, 848, 850, 851,
                                              853, 855, 856, 857, 858, 859, 860,
                                              861, 863, 864, 865, 866, 867, 868,
                                              869, 870, 871, 872, 873, 875, 876,
                                              877, 878, 879, 881, 884, 888, 889,
                                              890, 891, 892, 893, 894, 895, 896,
                                              897, 898, 899, 900, 902, 903, 904,
                                              907, 912, 913, 914, 915, 916, 917,
                                              918, 919, 923, 924, 925, 926, 931,
                                              932, 933, 934, 935, 936, 937, 938,
                                              939, 940, 941, 942, 943, 957, 958,
                                              959, 960, 961, 962, 963, 964, 965,
                                              966, 967, 968, 969, 970, 971, 972,
                                              973, 974, 975, 976, 977, 978, 979,
                                              980, 981, 982, 983, 984, 985, 987,
                                              988, 989, 990, 991, 992, 993, 994,
                                              995, 996, 999, 1000, 1001, 1003,
                                              1009, 1010, 1011, 1017, 1018,
                                              1019, 1021, 1023, 1024, 1026,
                                              1027, 1029, 1030, 1031, 1032,
                                              1033, 1034, 1035, 1036, 1037,
                                              1038, 1040, 1044, 1045, 1047,
                                              1048, 1049, 1050, 1051, 1052,
                                              1053, 1054, 1056, 1057, 1058,
                                              1059, 1060, 1064, 1065, 1066,
                                              1070, 1072, 1073, 1074, 1075,
                                              1076, 1084, 1086, 1089, 1092,
                                              1098, 1099, 1100, 1101, 1102,
                                              1103, 1107, 1111, 1112, 1113,
                                              1114, 1118, 1119, 1120, 1121,
                                              1122, 1123, 1124, 1125, 1126,
                                              1127, 1128, 1129, 1130, 1131},
                           frozenset({166}): {801, 802, 803, 804, 805, 806, 807,
                                              808, 809, 810, 811, 812, 813, 814,
                                              815, 816, 817, 818},
                           frozenset({167}): {522, 533, 550, 552, 553, 554, 555,
                                              556, 567, 569, 570, 579, 78, 79,
                                              80, 82, 83, 84, 85, 88, 89, 90,
                                              91, 92, 93, 94, 96, 98, 99, 100,
                                              101, 102, 105, 106, 107, 108, 835,
                                              110, 112, 119, 120, 121, 122, 123,
                                              124, 125, 126, 127, 129, 131, 132,
                                              133, 134, 136, 137, 138, 139, 140,
                                              141, 144, 150, 151, 152, 154, 157,
                                              158, 159, 160, 163, 165, 167, 168,
                                              174, 175, 176, 180, 182, 183, 184,
                                              185, 187, 188, 189, 191, 192, 193,
                                              194, 195, 201, 202, 204, 210, 213,
                                              214, 216, 220, 221, 222, 225, 227,
                                              232, 233, 234, 235, 236, 250, 251,
                                              252, 253, 254, 255, 256, 257, 258,
                                              259, 260, 261, 262, 263, 264, 265,
                                              266, 267, 268, 269, 270, 271, 272,
                                              274, 275, 302, 303, 304, 310, 311,
                                              313, 314, 315, 316, 317, 318, 319,
                                              320, 321, 322, 323, 324, 325, 326,
                                              327, 328, 329, 330, 331, 332, 836,
                                              837, 839, 840, 841, 842, 844, 846,
                                              847, 848, 850, 851, 853, 855, 856,
                                              857, 858, 859, 860, 861, 863, 864,
                                              355, 356, 357, 865, 359, 360, 361,
                                              371, 373, 398, 399, 400, 401, 402,
                                              403, 404, 405, 406, 407, 408, 409,
                                              412, 413, 415, 416, 418, 419, 433,
                                              435, 437, 439, 440, 441, 442, 443,
                                              444, 445, 446, 447, 448, 449, 450,
                                              451, 454, 455, 456, 459, 460, 461,
                                              462, 463, 470, 471, 472, 473, 477,
                                              486, 487, 491, 496, 497, 498, 499,
                                              507, 509}}
                          , result)

    def test_generate_dominator_set_with_csv(self):
        result = tc.generate_dominator_set_with_csv("test-data/killMap.csv")
        self.assertEquals({frozenset({99}), frozenset({127}), frozenset({116}),
                           frozenset({78}), frozenset({108}), frozenset({117}),
                           frozenset({111}), frozenset({130}), frozenset({115}),
                           frozenset({92}), frozenset({114}), frozenset({69}),
                           frozenset({101}), frozenset({93}), frozenset({113}),
                           frozenset({112}), frozenset({68}), frozenset({107}),
                           frozenset({166}), frozenset({97}), frozenset({95}),
                           frozenset({102}), frozenset({155}), frozenset({123}),
                           frozenset({128})}
                          , result[1])

    def test_generate_test_completeness_plot_with_csv(self):
        result = tc.generate_test_completeness_plot_from_csv(
            "test-data/killMap.csv")
        self.assertEquals(
            [(0, 0), (1, 196), (2, 231), (3, 261), (4, 282), (5, 301), (6, 319),
             (7, 334), (8, 348), (9, 362), (10, 376), (11, 390), (12, 403),
             (13, 416), (14, 428), (15, 440), (16, 448), (17, 456), (18, 464),
             (19, 469), (20, 473), (21, 477), (22, 477), (23, 477), (24, 477),
             (25, 477)]
            , result)
