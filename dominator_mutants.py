import csv
from typing import Set

import matplotlib.pyplot as plt
import pandas as pd


class Node:
    tests: Set[int]
    mutant_name: Set[int]
    children: Set[int]
    parents: Set[int]
    """The node object that represents mutants

    """

    def __init__(self, mutant_name=None, tests=None):
        """ Initiates node object

        Creates a node that represents mutants. If the mutant_name and/or
        tests are passed in, it will set self.mutant_name and self.tests
        to the values passed in. Otherwise, the function initiates them as the
        empty set (Set[int]).

        Additionally, it initiates self.children and self.parents as empty
        sets (Set[int]).

        Parameters:
        mutant_name: set[int]
            The mutant's identifier is stored as a set so that when two
            indistinguishable mutants are merged their name could easily be
            merged (default None)
        tests: set[int]
            A set of test identifiers that fail for the mutant represented
            by this node (default None)

        Attributes:
        self.mutant_name: set[int]
            The mutant's identifier is stored as a set so that when two
            indistinguishable mutants are merged their name could easily be
            merged (default set[int])
        self.tests: set[int]
            A set of test identifiers that fail for the mutant represented
            by this node (default set[int])
        self.children: set[int]
            A set of mutant identifiers that represent mutants that are
            killed by a superset of tests that kill the mutant represented
            by this node (default set[int]).
        self.parents: set[int]
            A set of mutant identifiers that represent mutants that are
            killed by a subset of tests that kill the mutant represented by
            this node (default set[int]).

        """
        if mutant_name is None:
            mutant_name = set()
        self.mutant_name = mutant_name
        if tests is None:
            tests = set()
        self.tests = tests
        self.children = set()
        self.parents = set()

    def determine_mutant_subsumption(self, new_node, graph):

        """Determines whether new_node's placement compared to this node.

        Assumes that the nodes that are passed in are related.

        Checks whether this node and new_node are distinguishable nodes.

        If the nodes are distinguishable, and if the test identifiers in this
        node are a subset of the test identifiers in new_node, it will call
        update_dominant on this node. Otherwise, it will call update_subsumed.


        Parameters:
            new_node: Node
                A new node representing a mutant that is being added to the the
                graph
            graph: Graph
                A graph containing nodes that represent mutants


        """

        # This may seem redundant, but it is required because sometimes adding
        # new nodes to the graph will result in multiple edges being re-drawn.
        # This may result in discovery of new indistinguishable nodes.
        # if not self.is_distinguishable_from(new_node):
        #     print("they are not distinguishable")
        #     if not self == new_node:
        #         self.merge_indistinguishable_nodes(new_node, graph)

        # Determining dominance vs. subsumption using test identifiers
        if self.tests.issubset(new_node.tests):
            self.update_dominant(new_node, graph)

        else:
            self.update_subsumed(new_node, graph)

    def update_dominant(self, new_node, graph):
        """Updates the dominant node on the graph with new_node
        If this node has any children, for any given child of this node, if the
        child's set of test identifiers is a subset of new_node's set of test
        identifiers, this function calls determine_mutant_subsumption on the
        child. Otherwise, add_children_in_between is called on this node.
        If this node doesn't have any children, the function calls
        add_children on this node.
        Parameters:
            new_node: Node
                A new node representing a mutant that is being added to the the
                graph and is subsumed by this node
            graph: Graph
                A graph containing nodes that represent mutants
        """
        # Check whether this node has children, and if yes, explore the
        # possibility of placing new_node relative to those children on the
        # graph
        # In a large graph, this case is more likely. Therefore, it is the
        # first possible choice in the conditional

        if len(self.children):
            children_can_relate = False
            for child in self.children.copy():
                if child.tests.issubset(new_node.tests):
                    children_can_relate = True
                    if child == new_node:
                        continue
                    else:
                        # Determining where new_node is going to be on the graph
                        # relative to the self's child
                        child.determine_mutant_subsumption(new_node, graph)
                elif child.tests.issuperset(new_node.tests):
                    children_can_relate = True
                    # Adding node
                    self.add_children_in_between(new_node, child)
            if not children_can_relate:
                self.add_children(new_node)
        # Base case: if this node doesn't have children, just add new_node as
        # its child
        else:
            self.add_children(new_node)

    def update_subsumed(self, new_node, graph):
        """Updates the subsumed node on the graph with new_node
        If this node has any parents, for any given child of this node, if the
        child's set of test identifiers is a superset of new_node's set of test
        identifiers, this functions calls determine_mutant_subsumption on the
        parent. Otherwise, add_children_in_between is called on the parent.
        If this node doesn't have any parents, the function calls
        add_children on new_node.
       Parameters:
            new_node: Node
                A new node representing a mutant that is being added to the the
                graph and is dominated by this node
            graph: Graph
                A graph containing nodes that represent mutants
        """
        # Check whether this node has parents, and if yes, explore the
        # possibility of placing new_node relative to those parents on the
        # graph
        # In a large graph, this case is more likely. Therefore, it is the
        # first possible choice in the conditional
        if len(self.parents):
            parents_can_relate = False
            for parent in self.parents.copy():
                if parent.tests.issuperset(new_node.tests):
                    parents_can_relate = True
                    if parent == new_node:
                        continue
                    else:
                        # adding new_node as a relative of self's child
                        parent.determine_mutant_subsumption(new_node, graph)
                elif parent.tests.issubset(new_node.tests):
                    parents_can_relate = True
                    parent.add_children_in_between(new_node, self)
            if not parents_can_relate:
                new_node.add_children(self)

        # Base case: if self doesn't have parents, just add new_node as its
        # parent (or add self as new_node's child)
        else:
            new_node.add_children(self)

    def add_children(self, new_node):
        """Adds a child to this node

        Parameters:
            new_node: Node
                A new node representing a mutant that is being added to the
                graph

        """
        self.children.add(new_node)
        new_node.parents.add(self)

    def add_children_in_between(self, new_node, child):
        """Splits the edges between this node and its child to add new_node in
        between

        It changes and adds edges to the graph such that this node becomes
        the parent for new_node, and new_node becomes the parent of the child
        while preserving all other existing edges

        To do so, the function removes direct edges between this node and its
        child and adds a pair of edges between new_node and this node and
        another pair of edges between new_node and child

        Parameters:
            new_node: Node
                A new node representing a mutant that is being added to the
                graph
            child: Node
                A child node of this node that already exists on the graph

        """
        new_node.parents.add(self)
        new_node.children.add(child)
        self.children.add(new_node)
        self.children.remove(child)
        child.parents.add(new_node)
        child.parents.remove(self)

    # TODO update specs
    def merge_indistinguishable_nodes(self, n2, graph):
        """Merges two nodes that represent mutants in a given graph

        It renames this node to include the n2's identifier by union-ing the
        sets containing each node's identifier.

        It adds the second node to graph.indistinguishable, which is a member
        variable of graph. graph.indistinguishable is a list of
        indistinguishable nodes that will be removed later by
        graph.connect_node().

        Parameters:
            n2: Node
                Second mutant
            graph: Graph
                The graph containing these mutants

        """
        self.mutant_name = self.mutant_name.union(n2.mutant_name)

    def is_distinguishable_from(self, n2):
        """Determines whether two nodes are distinguishable using direct
        comparison and their test identifiers.


        Parameters:
            n2: Node
                The mutant being compared to this mutant

        Return:
            True if the nodes representing mutants are distinguishable;
            False otherwise.

        """

        return (self != n2) and (self.tests != n2.tests)


class Graph:
    """The graph object that represents the mutant domination graph

        """

    def __init__(self):
        """Initiates the graph object

        Attributes:
            self.nodes_added : List[Node]
                A list of nodes that represents mutants that are going to be
                added to the graph if create_edges is called on it
            self.nodes_added : List[Node]
                A list of nodes that represents mutants that are added to the
                graph by create_edges
            self.indistinguishable : List[Node]
                A list of nodes that represents indistinguishable mutants that
                are going to be removed

        """
        self.nodes = []
        self.nodes_added = []
        self.indistinguishable = []

    def add_node(self, new_node):
        """Adds a given node to the list of the nodes on the graph

        If the node that is passed in is a valid instance of Node class,
        this function adds the given node to the graph, but it doesn't create
        a relation between the existing nodes and the newly added node.

        Parameters:
            new_node: Node
                Node that is being added to this graph

        """
        if new_node not in self.nodes:

            for node in self.nodes:
                if not new_node.is_distinguishable_from(node):
                    node.merge_indistinguishable_nodes(new_node, self)
                    break


            else:
                self.nodes.append(new_node)

    def create_edges(self):
        """Creates edge and connects the nodes that are already placed in the
        graph.

        Comparing all the nodes in the graph, it determines whether a
        relationship could exist between them by checking
        whether they are the same or that the sets of their test identifiers
        are a subset or superset of each other.

        Finally, it removes indistinguishable nodes, keeping only one node
        out of each set of indistinguishable nodes.

            """
        for n1 in range(0, len(self.nodes)):

            # self.nodes_added.append(self.nodes[n1])
            for n2 in range(0, n1):

                # If the nodes are the same
                # or if at least the set of test identifiers in one of them is
                # not a subset of the other one, move on to the next node

                if not (self.nodes[n2].tests.issubset(
                        self.nodes[n1].tests) or
                        self.nodes[n2].tests.issuperset(
                            self.nodes[n1].tests)):
                    continue

                # If the nodes can have edges between them, determine their
                # subsumption relation
                else:
                    self.nodes[n2].determine_mutant_subsumption(
                        self.nodes[n1],
                        self)

        # for node in self.indistinguishable:
        #     self.nodes.remove(node)

    def get_tests_covered(self, node):
        """Returns all the tests covered by a mutant

        Recursively iterates from a node representing a dominator mutant to
        nodes with no children identifiers at the bottom of the subsumpsion
        graph.

        It then returns all the tests identifiers for the nodes with no
        children identifiers that are subsumed by the first node that was
        passed in.

        If a node has no children identifiers, then its tests identifiers are
        returned.

        Parameters:
            node: Node
                A node on the graph

        Returns:
            tests_covered: set[int]



        """
        if node.children == set():
            return node.tests
        else:
            tests_covered = set()
            for child in node.children:
                tests_covered = tests_covered.union(
                    self.get_tests_covered(child))

            return tests_covered


def calculate_dominating_mutants(kill_map):
    """Calculates a dominating set of mutants

    Calculates the dominating set of mutants in a graph given a mapping from
    mutant identifiers to a set of identifiers of tests that kill each mutant.

    This function initializes a graph and adds all the mutant identifiers
    with their test identifiers in the kill map as initialized nodes to the
    graph.

    It then connects these nodes by establishing relationships between
    nodes that contain test identifiers that are a subset or superset of each
    other.

    Finally, it returns the graph containing these mutants and two minimal
    sets of mutants which contain a minimal set of test identifiers. One of
    these sets only contains name identifiers, whereas the second one
    contains node objects.


    Parameters:
        kill_map: A mapping from a set of identifiers from mutants killed to a
        set of identifiers for tests that kill each mutant.

    Returns:
        (tuple): containing
            graph : Graph
                The graph containing nodes that represent mutants
            dominator_mutants_set: set[int]
                The set of name identifiers of mutants in a dominating set.
            dominator_mutants_set_actual_mutant: set[Node]
                The set of Node objects representing mutants in a dominating
                set.
    """

    graph = Graph()

    # initiate nodes and add them to the graph
    for mutant in kill_map:
        node = Node(mutant, kill_map.get(mutant))
        graph.add_node(node)

    # If possible, create edges between the nodes in the graph
    graph.create_edges()

    # Create a set of dominator mutants.
    # Any mutant(node) that doesn't have a parent is a dominator mutant
    dominator_mutants_set = set()
    dominator_mutants_set_actual_mutant = list()
    for mutants in graph.nodes:
        if mutants.parents == None or len(mutants.parents) == 0:
            dominator_mutants_set.add(mutants.mutant_name)
            dominator_mutants_set_actual_mutant.append(mutants)

    return graph, dominator_mutants_set, dominator_mutants_set_actual_mutant


def generate_test_completeness_plot(kill_map):
    """Generates test completeness plot

    Takes a mapping of mutants to tests they cover. Calls
    calculate_dominating_mutants on the kill_map to store a dominating set of
    mutants.

    This set is then used to all the tests that are subsumed by each of these
    mutants by calling get_tests_covered. This creates a mapping of each
    mutant to tests they kill through their subsumed mutants.

    This mapping is then used generate the test completeness plot. First,
    the mapping is sorted by the number of tests each mutant subsumes and
    those tests are added to the list of tests that are explored thus far.

    Then, the set of tests explored so far is subtracted from the test
    identifiers of each dominating mutant in the mapping, and the remaning
    mutants are re-sorted based on the number of remaining test identifiers.

    The above process is repeated until all dominating mutants are considered.



    Parameters:
        kill_map: A mapping from a set of identifiers from mutants killed to a
        set of identifiers for tests that kill each mutant.

    Returns:
        plot: List[tuple(int, int)]
            A list of plot points that could used to plot test completeness
    """

    # Get the dominator set of mutants and their graph
    result = calculate_dominating_mutants(kill_map)
    dominator_set = result[2]
    graph = result[0]
    plot = [(0, 0)]

    # Initialize a a dictionary to keep track of test completeness
    test_completeness_dict = dict()

    # Add dominator mutants and their covered tests to the list
    # Create a mapping of mutant -> {tests}
    for mutants in dominator_set:
        test_completeness_dict[mutants.mutant_name] = graph.get_tests_covered(
            mutants)

    # Create a sorted list of dominator mutants based on the number of tests
    # they cover

    tests_added_plotted_so_far = set()

    # Add its tests so far to the list
    for mutants_counter in (range(len(test_completeness_dict.copy().items()))):
        # 1.3 generate new sorted list (resort list)
        sorted_list = sorted(test_completeness_dict,
                             key=lambda k: len(test_completeness_dict[k]),
                             reverse=True)

        # Add the tests from the latest mutant to the set of tests already
        # visited

        tests_added_plotted_so_far = tests_added_plotted_so_far.union(
            test_completeness_dict.get(
                sorted_list[0]))

        # Add new point to the plot using the x = muntants counter and
        # y = len(# tests) as

        plot.append((mutants_counter + 1, len(tests_added_plotted_so_far)))

        # Remove tests added so far from the rest of the list (DO need to
        # use a for loop inside this for loop for the rest of the mutants on the
        # list)

        for other_mutants in range(1, len(sorted_list)):
            temp = test_completeness_dict.get(sorted_list[other_mutants])
            temp = temp - tests_added_plotted_so_far
            test_completeness_dict[sorted_list[other_mutants]] = temp
        # Remove the current mutant from the dict
        test_completeness_dict.pop(sorted_list[0])

    return plot


# TODO Improve this
def plot(plot):
    """Plots the test completeness graph

    Plots the test completes achieved on the y axis for for each unit of work
    which is a (dominator) mutant presented.

    Parameters:
         plot: List[tuple(int, int)]
            A list of plot points that could used to plot test completeness

            """
    plotter = pd.DataFrame(
        data=plot,
        columns=["Work", "Test Completeness"]
    )
    ax = plotter.plot(x='Work', y='Test Completeness',
                      xticks=range(len(plot)),
                      yticks=range(0, plot[(len(plot) - 1)][1], 100),
                      legend=False)
    ax.set_ylabel("Test Completeness")
    plt.show()


def convert_csv_to_killmap(csv_filename):
    """Converts a CSV file generated in Major framework to a killmap

    Parameters:
        csv_filename: .csv document
            A csv document generated by the Major framework containing a
            mapping from mutants to the tests they kill

    Returns:
        kill_map: A mapping from a set of identifiers from mutants killed to a
        set of identifiers for tests that kill each mutant.
    """
    with open(csv_filename, newline='') as File:
        kill_map = {}
        reader = csv.reader(File)

        # skipping the header
        next(reader)
        for k, y in reader:
            # converting to integers
            k = int(k)
            y = int(y)
            j = frozenset({y})
            s = kill_map.get(j, set())
            s.add(k)
            kill_map[j] = s

        return kill_map


def generate_dominator_set_with_csv(csv_filename):
    """Calculates a dominating set of mutants given a CSV file containing the
    mapping from mutants to tests the kill

    See documentation for convert_csv_to_killmap and
    calculate_dominating_mutants.

    Parameters:
        csv_filename: .csv document
        A csv document generated by the Major framework containing a
        mapping from mutants to the tests they kill

    Returns:
    (tuple): containing
        graph : Graph
            The graph containing nodes that represent mutants
        dominator_mutants_set: set[int]
            The set of name identifiers of mutants in a dominating set.
        dominator_mutants_set_actual_mutant: set[Node]
            The set of Node objects representing mutants in a dominating
            set.
        """
    kill_map = convert_csv_to_killmap(csv_filename)
    return calculate_dominating_mutants(kill_map)


def generate_test_completeness_plot_from_csv(csv_filename):
    """Generates the test completeness plot given a CSV file containing the
    mapping from mutants to tests the kill

    See documentation for convert_csv_to_killmap,
    generate_test_completeness_plot, and plot

    Parameters:
        csv_filename: .csv document
            A csv document generated by the Major framework containing a
            mapping from mutants to the tests they kill

    Returns:
        plotted_points: List[tuple(int, int)]
            A list of plot points that could used to plot test completeness
    """
    kill_map = convert_csv_to_killmap(csv_filename)
    plotted_points = generate_test_completeness_plot(kill_map)
    plot(plotted_points)
    return plotted_points


def convert_csv_to_killmap_3_columns(csv_filename):
    """Converts a CSV(with 3 columns) file generated in Major framework to a killmap

    Parameters:
        csv_filename: .csv document
            A csv document generated by the Major framework containing a
            mapping from mutants to the tests they kill

    Returns:
        kill_map: A mapping from a set of identifiers from mutants killed to a
        set of identifiers for tests that kill each mutant.
    """
    with open(csv_filename, newline='') as File:
        kill_map = {}
        reader = csv.reader(File)

        # skipping the header
        next(reader)
        for k, y, extra_column in reader:
            # converting to integers
            k = int(k)
            y = int(y)
            j = frozenset({y})
            s = kill_map.get(j, set())
            s.add(k)
            kill_map[j] = s
        return kill_map


def generate_dominator_set_with_csv_3_col(csv_filename):
    """Calculates a dominating set of mutants given a CSV(3 columns) file containing the
    mapping from mutants to tests the kill

    See documentation for convert_csv_to_killmap and
    calculate_dominating_mutants.

    Parameters:
        csv_filename: .csv document
        A csv document generated by the Major framework containing a
        mapping from mutants to the tests they kill

    Returns:
    (tuple): containing
        graph : Graph
            The graph containing nodes that represent mutants
        dominator_mutants_set: set[int]
            The set of name identifiers of mutants in a dominating set.
        dominator_mutants_set_actual_mutant: set[Node]
            The set of Node objects representing mutants in a dominating
            set.
        """
    kill_map = convert_csv_to_killmap_3_columns(csv_filename)
    return calculate_dominating_mutants(kill_map)
