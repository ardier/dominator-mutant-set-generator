import unittest

import tc


class TestCase(unittest.TestCase):

    def test_create_simple_node_with_just_tests(self):
        test_node = tc.Node({1}, {1, 2})
        self.assertEqual(test_node.mutant_name, {1})
        self.assertEqual(test_node.tests, {1, 2})

    def test_create_simple_node_with_all_attributes(self):
        test_node = tc.Node({1}, {1, 2}, {3, 4}, {5, 6})
        self.assertEqual(test_node.mutant_name, {1})
        self.assertEqual(test_node.tests, {1, 2})
        self.assertEqual(test_node.children, {3, 4})
        self.assertEqual(test_node.parents, {5, 6})

    def test_create_node_from_with_tests_only_from_kill_map(self):
        kill_map = {frozenset({1}): {1, 2}, frozenset({2}): {1, 4},
                    frozenset({3}): {2}, frozenset({4}): {1, 2, 3, 4}}
        test_graph = tc.calculate_dominating_mutants(kill_map)[0]
        self.assertEqual(test_graph.nodes[0].mutant_name,
                         list(kill_map.keys())[0])
        self.assertEqual(test_graph.nodes[0].tests,
                         kill_map.get(list(kill_map)[0]))
        self.assertEqual(test_graph.nodes[3].mutant_name,
                         list(kill_map.keys())[3])
        self.assertEqual(test_graph.nodes[3].tests,
                         kill_map.get(list(kill_map)[3]))

    def test_is_distinguishable(self):
        mutant_2 = tc.Node({2}, {1, 4})
        mutant_5 = tc.Node({5}, {1, 4})
        mutant_1 = tc.Node({1}, {1, 2})
        self.assertTrue(tc.Node.is_distinguishable_from(mutant_2, mutant_1))
        self.assertFalse(tc.Node.is_distinguishable_from(mutant_1, mutant_1))
        self.assertFalse(tc.Node.is_distinguishable_from(mutant_2, mutant_5))

    def test_merge_indistinguishable(self):

        mutant_2 = tc.Node({2}, {1, 4})
        mutant_5 = tc.Node({5}, {1, 4})

        test_graph = tc.Graph()
        tc.Graph.add_node(test_graph, mutant_2)
        tc.Graph.add_node(test_graph, mutant_5)
        test_graph.connect_nodes()

        result = []
        for node in test_graph.nodes:
            result.append(node)

        self.assertEqual(result[0].mutant_name, {2, 5})

    def test_add_node(self):
        mutant_1 = tc.Node({1}, {1, 2})
        test_graph = tc.Graph()
        self.assertTrue(tc.Graph.add_node(test_graph, mutant_1))

    def test_connect_the_same_node_to_itself(self):
        mutant_2 = tc.Node({2}, {1, 4})
        test_graph = tc.Graph()
        tc.Graph.add_node(test_graph, mutant_2)
        tc.Graph.connect_nodes(test_graph)
        test_graph_nodes = test_graph.nodes
        result = []
        for nodes in test_graph_nodes:
            result.append(nodes.mutant_name)

        self.assertEqual([{2}], result)

    def test_connect_nodes_indistinguishable(self):
        mutant_2 = tc.Node({2}, {1, 4})
        mutant_5 = tc.Node({5}, {1, 4})
        test_graph = tc.Graph()
        tc.Graph.add_node(test_graph, mutant_2)
        tc.Graph.add_node(test_graph, mutant_5)
        tc.Graph.connect_nodes(test_graph)
        test_graph_nodes = test_graph.nodes
        result = []
        for nodes in test_graph_nodes:
            result.append(nodes.mutant_name)
        self.assertEqual([{2, 5}], result)

    def test_connect_two_nodes_distinguishable(self):
        mutant_1 = tc.Node({1}, {1, 2})
        mutant_2 = tc.Node({2}, {1, 4})
        test_graph = tc.Graph()
        tc.Graph.add_node(test_graph, mutant_1)
        tc.Graph.add_node(test_graph, mutant_2)

        tc.Graph.connect_nodes(test_graph)
        test_graph_nodes = test_graph.nodes
        result = []
        for nodes in test_graph_nodes:
            result.append(nodes.mutant_name)
        self.assertEqual([{1}, {2}], result)

    def test_add_relation_just_two_nodes_children(self):
        mutant_3 = tc.Node({3}, {2})
        mutant_1 = tc.Node({1}, {1, 2})
        test_graph = tc.Graph()
        tc.Graph.add_node(test_graph, mutant_3)
        tc.Graph.add_node(test_graph, mutant_1)
        tc.Graph.connect_nodes(test_graph)

        result = []
        result_parent = []

        if mutant_3.parents is None:
            mutant_3.parents = set()
        for nodes in mutant_3.parents:
            result.append(nodes.mutant_name)
        self.assertEqual([], result)
        if mutant_3.children is None:
            mutant_3.children = set()
        for parents in mutant_3.children:
            result_parent.append(parents.mutant_name)
        self.assertEqual([{1}], result_parent)

        result2 = []
        result_parent2 = []

        if mutant_1.parents is None:
            mutant_1.parents = set()
        for nodes2 in mutant_1.parents:
            result2.append(nodes2.mutant_name)
        self.assertEqual([{3}], result2)
        if mutant_1.parents is None:
            mutant_1.parents = set()
        for parents in mutant_1.parents:
            result_parent2.append(parents.mutant_name)
        self.assertEqual([{3}], result_parent2)

    def test_add_relation_for_children_with_3_level_graph(self):
        mutant_3 = tc.Node({3}, {2})
        mutant_1 = tc.Node({1}, {1, 2})
        mutant_4 = tc.Node({4}, {1, 2, 3, 4})

        test_graph = tc.Graph()
        tc.Graph.add_node(test_graph, mutant_3)
        tc.Graph.add_node(test_graph, mutant_1)
        tc.Graph.add_node(test_graph, mutant_4)

        tc.Graph.connect_nodes(test_graph)

        # mutant 3
        result = []
        result_parent = []

        if test_graph.nodes[0].children is None:
            test_graph.nodes[0].children = set()
        for nodes in test_graph.nodes[0].children:
            result.append(nodes.mutant_name)
        self.assertEqual([{1}], result)

        if test_graph.nodes[0].parents is None:
            test_graph.nodes[0].parents = set()
        for parents in test_graph.nodes[0].parents:
            result_parent.append(parents.mutant_name)
        self.assertEqual([], result_parent)

        # mutant 1
        result2 = []
        result_parent2 = []

        if test_graph.nodes[1].parents is None:
            test_graph.nodes[1].parents = set()
        for parents2 in test_graph.nodes[1].parents:
            result_parent2.append(parents2.mutant_name)
        self.assertEqual([{3}], result_parent2)

        if test_graph.nodes[1].children is None:
            test_graph.nodes[1].children = set()
        for nodes2 in test_graph.nodes[1].children:
            result2.append(nodes2.mutant_name)
        self.assertEqual([{4}], result2)

        # mutant 4
        result4 = []
        result_parent4 = []

        if test_graph.nodes[2].parents is None:
            test_graph.nodes[2].parents = set()
        for parents4 in test_graph.nodes[2].parents:
            result_parent4.append(parents4.mutant_name)
        self.assertEqual([{1}], result_parent4)

        if test_graph.nodes[2].children is None:
            test_graph.nodes[2].children = set()
        for nodes4 in test_graph.nodes[2].children:
            result4.append(nodes4.mutant_name)
        self.assertEqual([], result4)

    def test_add_relation_for_children_with_4_level_graph(self):
        mutant_3 = tc.Node({3}, {2})
        mutant_1 = tc.Node({1}, {1, 2})
        mutant_6 = tc.Node({6}, {1, 2, 3})
        mutant_4 = tc.Node({4}, {1, 2, 3, 4})

        test_graph = tc.Graph()
        tc.Graph.add_node(test_graph, mutant_3)
        tc.Graph.add_node(test_graph, mutant_1)
        tc.Graph.add_node(test_graph, mutant_6)
        tc.Graph.add_node(test_graph, mutant_4)

        tc.Graph.connect_nodes(test_graph)

        # mutant 3
        result = []
        result_parent = []

        if test_graph.nodes[0].children is None:
            test_graph.nodes[0].children = set()
        for nodes in test_graph.nodes[0].children:
            result.append(nodes.mutant_name)
        self.assertEqual([{1}], result)

        if test_graph.nodes[0].parents is None:
            test_graph.nodes[0].parents = set()
        for parents in test_graph.nodes[0].parents:
            result_parent.append(parents.mutant_name)
        self.assertEqual([], result_parent)

        # mutant 1
        result2 = []
        result_parent2 = []

        if test_graph.nodes[1].parents is None:
            test_graph.nodes[1].parents = set()
        for parents2 in test_graph.nodes[1].parents:
            result_parent2.append(parents2.mutant_name)
        self.assertEqual([{3}], result_parent2)

        if test_graph.nodes[1].children is None:
            test_graph.nodes[1].children = set()
        for nodes2 in test_graph.nodes[1].children:
            result2.append(nodes2.mutant_name)
        self.assertEqual([{6}], result2)

        # mutant 6
        result3 = []
        result_parent3 = []

        if test_graph.nodes[2].parents is None:
            test_graph.nodes[2].parents = set()
        for parents3 in test_graph.nodes[2].parents:
            result_parent3.append(parents3.mutant_name)
        self.assertEqual([{1}], result_parent3)

        if test_graph.nodes[2].children is None:
            test_graph.nodes[2].children = set()
        for nodes3 in test_graph.nodes[2].children:
            result3.append(nodes3.mutant_name)
        self.assertEqual([{4}], result3)

        # mutant 4
        result4 = []
        result_parent4 = []

        if test_graph.nodes[3].parents is None:
            test_graph.nodes[3].parents = set()
        for parents4 in test_graph.nodes[3].parents:
            result_parent4.append(parents4.mutant_name)
        self.assertEqual([{6}], result_parent4)

        if test_graph.nodes[3].children is None:
            test_graph.nodes[3].children = set()
        for nodes4 in test_graph.nodes[3].children:
            result4.append(nodes4.mutant_name)
        self.assertEqual([], result4)

    def test_add_relation_just_two_nodes_parents(self):
        mutant_3 = tc.Node({3}, {2})
        mutant_1 = tc.Node({1}, {1, 2})
        test_graph = tc.Graph()
        tc.Graph.add_node(test_graph, mutant_1)
        tc.Graph.add_node(test_graph, mutant_3)
        tc.Graph.connect_nodes(test_graph)

        result = []
        result_parent = []

        if mutant_3.parents is None:
            mutant_3.parents = set()
        for nodes in mutant_3.parents:
            result.append(nodes.mutant_name)
        self.assertEqual([], result)
        if mutant_3.children is None:
            mutant_3.children = set()
        for parents in mutant_3.children:
            result_parent.append(parents.mutant_name)
        self.assertEqual([{1}], result_parent)

        result2 = []
        result_parent2 = []

        if mutant_1.parents is None:
            mutant_1.parents = set()
        for nodes2 in mutant_1.parents:
            result2.append(nodes2.mutant_name)
        self.assertEqual([{3}], result2)
        if mutant_1.parents is None:
            mutant_1.parents = set()
        for parents in mutant_1.parents:
            result_parent2.append(parents.mutant_name)
        self.assertEqual([{3}], result_parent2)

    def test_add_relation_for_parents_with_3_level_graph(self):
        mutant_4 = tc.Node({4}, {1, 2, 3, 4})
        mutant_1 = tc.Node({1}, {1, 2})
        mutant_3 = tc.Node({3}, {2})

        test_graph = tc.Graph()
        tc.Graph.add_node(test_graph, mutant_4)
        tc.Graph.add_node(test_graph, mutant_1)
        tc.Graph.add_node(test_graph, mutant_3)

        tc.Graph.connect_nodes(test_graph)

        # mutant 3
        result = []
        result_parent = []

        if test_graph.nodes[2].children is None:
            test_graph.nodes[2].children = set()
        for nodes in test_graph.nodes[2].children:
            result.append(nodes.mutant_name)
        self.assertEqual([{1}], result)

        if test_graph.nodes[2].parents is None:
            test_graph.nodes[2].parents = set()
        for parents in test_graph.nodes[2].parents:
            result_parent.append(parents.mutant_name)
        self.assertEqual([], result_parent)

        # mutant 1
        result2 = []
        result_parent2 = []

        if test_graph.nodes[1].parents is None:
            test_graph.nodes[1].parents = set()
        for parents2 in test_graph.nodes[1].parents:
            result_parent2.append(parents2.mutant_name)
        self.assertEqual([{3}], result_parent2)

        if test_graph.nodes[1].children is None:
            test_graph.nodes[1].children = set()
        for nodes2 in test_graph.nodes[1].children:
            result2.append(nodes2.mutant_name)
        self.assertEqual([{4}], result2)

        # mutant 4
        result4 = []
        result_parent4 = []

        if test_graph.nodes[0].parents is None:
            test_graph.nodes[0].parents = set()
        for parents4 in test_graph.nodes[0].parents:
            result_parent4.append(parents4.mutant_name)
        self.assertEqual([{1}], result_parent4)

        if test_graph.nodes[0].children is None:
            test_graph.nodes[0].children = set()
        for nodes4 in test_graph.nodes[0].children:
            result4.append(nodes4.mutant_name)
        self.assertEqual([], result4)

    def test_add_relation_for_parents_with_3_level_graph_one_indistinguishable(
            self):
        mutant_4 = tc.Node({4}, {1, 2, 3, 4})
        mutant_1 = tc.Node({1}, {1, 2})
        mutant_3 = tc.Node({3}, {2})
        mutant_6 = tc.Node({6}, {1, 2})

        test_graph = tc.Graph()
        tc.Graph.add_node(test_graph, mutant_4)
        tc.Graph.add_node(test_graph, mutant_1)
        tc.Graph.add_node(test_graph, mutant_3)
        tc.Graph.add_node(test_graph, mutant_6)

        tc.Graph.connect_nodes(test_graph)

        # mutant 3
        result2 = []
        result_parent2 = []

        if test_graph.nodes[2].parents is None:
            test_graph.nodes[2].parents = set()
        for parents2 in test_graph.nodes[2].parents:
            result_parent2.append(parents2.mutant_name)
        self.assertEqual([], result_parent2)

        if test_graph.nodes[2].children is None:
            test_graph.nodes[2].children = set()
        for nodes2 in test_graph.nodes[2].children:
            result2.append(nodes2.mutant_name)
        self.assertEqual([{1, 6}], result2)

        # mutant 1, 6
        result3 = []
        result_parent3 = []

        if test_graph.nodes[1].parents is None:
            test_graph.nodes[1].parents = set()
        for parents3 in test_graph.nodes[1].parents:
            result_parent3.append(parents3.mutant_name)
        self.assertEqual([{3}], result_parent3)

        if test_graph.nodes[1].children is None:
            test_graph.nodes[1].children = set()
        for nodes3 in test_graph.nodes[1].children:
            result3.append(nodes3.mutant_name)
        self.assertEqual([{4}], result3)

        # mutant 4
        result4 = []
        result_parent4 = []

        if test_graph.nodes[0].parents is None:
            test_graph.nodes[0].parents = set()
        for parents4 in test_graph.nodes[0].parents:
            result_parent4.append(parents4.mutant_name)
        self.assertEqual([{1, 6}], result_parent4)

        if test_graph.nodes[0].children is None:
            test_graph.nodes[0].children = set()
        for nodes4 in test_graph.nodes[0].children:
            result4.append(nodes4.mutant_name)
        self.assertEqual([], result4)

        def test_add_relation_for_parents_with_4_level_graph(self):
            mutant_4 = tc.Node({4}, {1, 2, 3, 4})
            mutant_6 = tc.Node({6}, {1, 2, 3})
            mutant_1 = tc.Node({1}, {1, 2})
            mutant_3 = tc.Node({3}, {2})

            test_graph = tc.Graph()
            tc.Graph.add_node(test_graph, mutant_4)
            tc.Graph.add_node(test_graph, mutant_6)
            tc.Graph.add_node(test_graph, mutant_1)
            tc.Graph.add_node(test_graph, mutant_3)

            tc.Graph.connect_nodes(test_graph)

            # mutant 3
            result = []
            result_parent = []

            if test_graph.nodes[3].children is None:
                test_graph.nodes[3].children = set()
            for nodes in test_graph.nodes[3].children:
                result.append(nodes.mutant_name)
            self.assertEqual([{1}], result)

            if test_graph.nodes[3].parents is None:
                test_graph.nodes[3].parents = set()
            for parents in test_graph.nodes[3].parents:
                result_parent.append(parents.mutant_name)
            self.assertEqual([], result_parent)

            # mutant 1
            result2 = []
            result_parent2 = []

            if test_graph.nodes[2].parents is None:
                test_graph.nodes[2].parents = set()
            for parents2 in test_graph.nodes[2].parents:
                result_parent2.append(parents2.mutant_name)
            self.assertEqual([{3}], result_parent2)

            if test_graph.nodes[2].children is None:
                test_graph.nodes[2].children = set()
            for nodes2 in test_graph.nodes[2].children:
                result2.append(nodes2.mutant_name)
            self.assertEqual([{6}], result2)

            # mutant 6
            result3 = []
            result_parent3 = []

            if test_graph.nodes[1].parents is None:
                test_graph.nodes[1].parents = set()
            for parents3 in test_graph.nodes[1].parents:
                result_parent3.append(parents3.mutant_name)
            self.assertEqual([{1}], result_parent3)

            if test_graph.nodes[1].children is None:
                test_graph.nodes[1].children = set()
            for nodes3 in test_graph.nodes[1].children:
                result3.append(nodes3.mutant_name)
            self.assertEqual([{4}], result3)

            # mutant 4
            result4 = []
            result_parent4 = []

            if test_graph.nodes[0].parents is None:
                test_graph.nodes[0].parents = set()
            for parents4 in test_graph.nodes[0].parents:
                result_parent4.append(parents4.mutant_name)
            self.assertEqual([{6}], result_parent4)

            if test_graph.nodes[0].children is None:
                test_graph.nodes[0].children = set()
            for nodes4 in test_graph.nodes[0].children:
                result4.append(nodes4.mutant_name)
            self.assertEqual([], result4)

    def test_add_relation_for_parents_and_children_with_3_level_graph(self):
        mutant_4 = tc.Node({4}, {1, 2, 3, 4})
        mutant_3 = tc.Node({3}, {2})
        mutant_1 = tc.Node({1}, {1, 2})

        test_graph = tc.Graph()
        tc.Graph.add_node(test_graph, mutant_4)
        tc.Graph.add_node(test_graph, mutant_3)
        tc.Graph.add_node(test_graph, mutant_1)

        tc.Graph.connect_nodes(test_graph)

        # mutant 3
        result = []
        result_parent = []

        if test_graph.nodes[1].children is None:
            test_graph.nodes[1].children = set()
        for nodes in test_graph.nodes[1].children:
            result.append(nodes.mutant_name)
        self.assertEqual([{1}], result)

        if test_graph.nodes[1].parents is None:
            test_graph.nodes[1].parents = set()
        for parents in test_graph.nodes[1].parents:
            result_parent.append(parents.mutant_name)
        self.assertEqual([], result_parent)

        # mutant 1
        result2 = []
        result_parent2 = []

        if test_graph.nodes[2].parents is None:
            test_graph.nodes[2].parents = set()
        for parents2 in test_graph.nodes[2].parents:
            result_parent2.append(parents2.mutant_name)
        self.assertEqual([{3}], result_parent2)

        if test_graph.nodes[2].children is None:
            test_graph.nodes[2].children = set()
        for nodes2 in test_graph.nodes[2].children:
            result2.append(nodes2.mutant_name)
        self.assertEqual([{4}], result2)

        # mutant 4
        result4 = []
        result_parent4 = []

        if test_graph.nodes[0].parents is None:
            test_graph.nodes[0].parents = set()
        for parents4 in test_graph.nodes[0].parents:
            result_parent4.append(parents4.mutant_name)
        self.assertEqual([{1}], result_parent4)

        if test_graph.nodes[0].children is None:
            test_graph.nodes[0].children = set()
        for nodes4 in test_graph.nodes[0].children:
            result4.append(nodes4.mutant_name)
        self.assertEqual([], result4)

    def test_add_relation_for_parents_and_children_with_4_level_graph(self):
        mutant_6 = tc.Node({6}, {1, 2, 3})
        mutant_4 = tc.Node({4}, {1, 2, 3, 4})
        mutant_1 = tc.Node({1}, {1, 2})
        mutant_3 = tc.Node({3}, {2})

        test_graph = tc.Graph()
        tc.Graph.add_node(test_graph, mutant_6)
        tc.Graph.add_node(test_graph, mutant_4)
        tc.Graph.add_node(test_graph, mutant_1)
        tc.Graph.add_node(test_graph, mutant_3)

        tc.Graph.connect_nodes(test_graph)

        # mutant 3
        result = []
        result_parent = []

        if test_graph.nodes[3].children is None:
            test_graph.nodes[3].children = set()
        for nodes in test_graph.nodes[3].children:
            result.append(nodes.mutant_name)
        self.assertEqual([{1}], result)

        if test_graph.nodes[3].parents is None:
            test_graph.nodes[3].parents = set()
        for parents in test_graph.nodes[3].parents:
            result_parent.append(parents.mutant_name)
        self.assertEqual([], result_parent)

        # mutant 1
        result2 = []
        result_parent2 = []

        if test_graph.nodes[2].parents is None:
            test_graph.nodes[2].parents = set()
        for parents2 in test_graph.nodes[2].parents:
            result_parent2.append(parents2.mutant_name)
        self.assertEqual([{3}], result_parent2)

        if test_graph.nodes[2].children is None:
            test_graph.nodes[2].children = set()
        for nodes2 in test_graph.nodes[2].children:
            result2.append(nodes2.mutant_name)
        self.assertEqual([{6}], result2)

        # mutant 6
        result3 = []
        result_parent3 = []

        if test_graph.nodes[0].parents is None:
            test_graph.nodes[0].parents = set()
        for parents3 in test_graph.nodes[0].parents:
            result_parent3.append(parents3.mutant_name)
        self.assertEqual([{1}], result_parent3)

        if test_graph.nodes[0].children is None:
            test_graph.nodes[0].children = set()
        for nodes3 in test_graph.nodes[0].children:
            result3.append(nodes3.mutant_name)
        self.assertEqual([{4}], result3)

        # mutant 4
        result4 = []
        result_parent4 = []

        if test_graph.nodes[1].parents is None:
            test_graph.nodes[1].parents = set()
        for parents4 in test_graph.nodes[1].parents:
            result_parent4.append(parents4.mutant_name)
        self.assertEqual([{6}], result_parent4)

        if test_graph.nodes[1].children is None:
            test_graph.nodes[1].children = set()
        for nodes4 in test_graph.nodes[1].children:
            result4.append(nodes4.mutant_name)
        self.assertEqual([], result4)

    def test_calculate_dominating_mutants_two_mutants(self):
        kill_map = {frozenset({1}): {1, 2}, frozenset({4}): {1, 2, 3, 4}}
        result = tc.calculate_dominating_mutants(kill_map)
        self.assertEqual({frozenset({1})}, result[1])

    def test_calculate_dominating_mutants_three_mutants_two_branches(self):
        kill_map = {frozenset({1}): {1, 2}, frozenset({2}): {1, 4},
                    frozenset({4}): {1, 2, 3, 4}}
        result = tc.calculate_dominating_mutants(kill_map)
        self.assertEqual({frozenset({2}), frozenset({1})}, result[1])

    def test_calculate_dominating_mutants_three_mutants_one_branches(self):
        kill_map = {frozenset({1}): {1, 2}, frozenset({3}): {2},
                    frozenset({4}): {1, 2, 3, 4}}
        result = tc.calculate_dominating_mutants(kill_map)
        self.assertEqual({frozenset({3})}, result[1])

    def test_calculate_dominating_mutants_four_mutants_two_branches_2_indistinguishable(
            self):
        kill_map = {frozenset({5}): {1, 4}, frozenset({3}): {2},
                    frozenset({4}): {1, 2, 3, 4}, frozenset({2}): {1, 4}}
        result = tc.calculate_dominating_mutants(kill_map)
        self.assertEqual({frozenset({3}), frozenset({2, 5})}, result[1])

    def test_calculate_dominating_mutants_five_three_layers_mutants_two_branches_2_indistinguishable(
            self):
        kill_map = {frozenset({1}): {1, 2},
                    frozenset({5}): {1, 4}, frozenset({2}): {1, 4},
                    frozenset({3}): {2}, frozenset({4}): {1, 2, 3, 4}}
        result = tc.calculate_dominating_mutants(kill_map)
        self.assertEqual({frozenset({3}), frozenset({2, 5})}, result[1])
