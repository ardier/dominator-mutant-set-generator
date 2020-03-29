class Node:
    """The node object that represents mutants

    Parameters:
        mutant_name: set()
            The mutant's identifier is stored as a set so that when two
            indistinguishable mutants are merged, their name could easily
            be merged (default None).
        tests: set()
            A set of test identifiers that fail for the mutant represented by
            this node (default None).
        children: set()
            A set of mutant identifiers that represent mutants that are
            killed by a superset of tests that kill the mutant represented
            by this node (default None).
        parents: set()
            A set of mutant identifiers that represent mutants that are
            killed by a subset of tests that kill the mutant represented by
            this node (default None).

    Attributes:
        self.mutant_name: set()
            The mutant's identifier is stored as a set so that when two
            indistinguishable mutants are merged their name could easily
            merged (default None)
        self.tests: set()
            A set of test identifiers that fail for the mutant represented
            by this node (default None)
        self.children: set()
            A set of mutant identifiers that represent mutants that are
            killed by a superset of tests that kill the mutant represented
            by this node (default None).
        self.parents: set()
            A set of mutant identifiers that represent mutants that are
            killed by a subset of tests that kill the mutant represented by
            this node (default None)..

    Methods:
        add_relation(self, new_node, graph)
            Creates a relation between self which is node already
            existing in graph object and the new_node
        add_children(self, new_node, graph)
            Adds new_node as self's child. Assumes the children
            aren't the same and are distinguishable
        add_parents(self, new_node, graph)
            Adds new_node as self's child. Assumes the children
            aren't the same and are distinguishable
        is_distinguishable_from(self, n2)
            Determines whether the mutants represented by
            two nodes are distinguishable
        merge_indistinguishable_nodes(self, n2, graph)
            Merges two indistinguishable mutants.
            Assumes they are indistinguishable.

    """

    def __init__(self, mutant_name=None, tests=None, children=None,
                 parents=None):
        self.mutant_name = mutant_name
        self.tests = tests
        self.children = children
        self.parents = parents

    def add_relation(self, new_node, graph, relationship="unknown"):
        """Adds a relation between an existing node in the graph and a new node.
        Assumes that the nodes that are passed in are related.
        If empty, it initiates parents and children member variables as
        empty sets for self and new_node. Checks whether self and new_node
        are distinguishable nodes, and if they are, it relates them recursively.
        If there are no possible nodes in between the two given nodes,
        then they become related as using their child/parent identifiers.
        Otherwise, it compares all the test identifiers for all the nodes in
        children/parents of self.
        If there exists another node between self and new_node whose tests are
        a subset of self/new_node and the superset of the other one,
        add_relation then recursively adds new_node to that node.

        Parameters:
            self: Node
                A node representing a mutant that already exists on the graph
            new_node: Node
                A new node representing a mutant that is being added to the the
                graph
            graph: Graph
                A graph containing nodes that represent mutants
            relationship : str
                A string that indicates the kind of relationship being added
                (default = unknown)

            """

        if self.children is None:
            self.children = set()
        if self.parents is None:
            self.parents = set()
        if new_node.children is None:
            new_node.children = set()
        if new_node.parents is None:
            new_node.parents = set()

        if not self.is_distinguishable_from(new_node):
            if not self == new_node:
                self.merge_indistinguishable_nodes(new_node, graph)
        else:
            if relationship == "child" or self.tests.issubset(new_node.tests):
                relationship = "child"
                self.relation = self.children
                new_node.relation_1 = new_node.parents
                new_node.relation_2 = new_node.children
            else:
                relationship = "parent"
                self.relation = self.parents
                new_node.relation_1 = new_node.children
                new_node.relation_2 = new_node.parents

            relationship_possibility_with_relatives = False
            if self.relation is set():
                new_node.relation_1.add(self)
                self.relation.add(new_node)
                relationship_possibility_with_relatives = True

            elif self.relation is not None and new_node not in self.relation:
                for relative in self.relation.copy():
                    if relationship == "child":
                        relation_edges = relative.parents
                    else:
                        relation_edges = relative.children
                    if relationship == "child" and relative.tests.issubset(
                            new_node.tests):
                        relationship_possibility_with_relatives = True
                        # adding new_node as a child of self's child
                        relative.add_relation(new_node, graph, "child")
                    elif relationship == "parent" and relative.tests.issuperset(
                            new_node.tests):
                        relationship_possibility_with_relatives = True
                        relative.add_relation(new_node, graph, "parent")
                    else:
                        if relationship == "child":
                            if new_node.tests.issubset(relative.tests):
                                new_node.relation_2.add(relative)
                        else:
                            if new_node.tests.issuperset(relative.tests):
                                new_node.relation_2.add(relative)
                        new_node.relation_1.add(self)
                        self.relation.add(new_node)
                        self.relation.remove(relative)
                        relation_edges.add(new_node)
                        relation_edges.remove(self)

            if relationship_possibility_with_relatives is False:
                new_node.relation_1.add(self)
                self.relation.add(new_node)

    def merge_indistinguishable_nodes(self, n2, graph):
        """Merges two nodes that represent mutants in a given graph.
        It renames self to include the n2's identifier by union-ing the sets
        containing each node's identifier. It adds the second node to
        graph.indistinguishable, which is a member variable of graph.
        graph.indistinguishable is a list of indistinguishable nodes
        that will be removed later by graph.connect_node().

        Parameters:
            self: Node
                First mutant
            n2: Node
                Second mutant
            graph: Graph
                The graph containing these mutants

        """
        self.mutant_name = self.mutant_name.union(n2.mutant_name)
        if n2 not in graph.indistinguishable:
            graph.indistinguishable.append(n2)

    def is_distinguishable_from(self, n2):
        """Determines whether two nodes are distinguishable using direct
        comparison, and their test identifiers.


        Parameters:
            self: Node
                First mutant being compared
            n2: Node
                Second mutant being compared

        Return:
            True if the nodes representing mutants are distinguishable,
            False otherwise.

        """
        if self == n2:
            return False

        if self.tests == n2.tests:
            return False

        return True


class Graph:
    """The graph object that represents the mutant domination graph

    Attributes:
        self.nodes : list()
            A list of nodes that represents mutants that are going to be
            placed in the graph
        self.nodes_added : list()
            A list of nodes that represents mutants that are added to the graph
        self.indistinguishable : list()
            A list of nodes that represents indistinguishable mutants that
            are going to be removed

    Methods:
        add_node(self, node)
            Adds the given node to the graph
        connect_nodes(self)
            Connects all the related nodes in the graph
        get_minimal_mutant_list(self)
            Gets the minimal mutant list

        """

    def __init__(self):
        self.nodes = []
        self.nodes_added = []
        self.indistinguishable = []

    def add_node(self, node):
        """Adds a given node to the list of the nodes on the graph.
        If the node that is passed in is a valid instance of Node class,
        this function adds the given node to the graph, but it doesn't create
        a relation between the existing nodes and the newly added node.

        Parameters:
            self: Graph
                Graph containing all the nodes representing mutants
            node: Node
                Node that is being added to the graph

        Returns:
            True if the node is added to the graph, False otherwise.

        """
        if isinstance(node, Node) and node not in self.nodes:
            self.nodes.append(node)
            return True
        else:
            return False

    def connect_nodes(self):
        """Connects the nodes that are already placed in the graph.
        Comparing all the nodes in the graph, it determines whether a
        relationship could exist between them by checking
        whether they are the same or that the sets of their test identifiers
        are a subset or superset of each other.
        Finally, it removes indistinguishable nodes, keeping only the one node
        out of each set of indistinguishable nodes.


        Parameters:
            self: Graph

            """
        for n1 in range(0, len(self.nodes.copy())):

            self.nodes_added.append(self.nodes[n1])
            for n2 in range(0, len(self.nodes_added)):

                # if the nodes are indistinguishable
                # or the indistinguishable node doesn't already exist,
                # group them

                if n1 == n2:
                    continue

                # other cases
                else:
                    if not (self.nodes[n2].tests.issubset(
                            self.nodes[n1].tests) or self.nodes[
                                n2].tests.issuperset(self.nodes[n1].tests)):
                        continue

                    else:
                        self.nodes[n2].add_relation(self.nodes[n1], self)

        for node in self.indistinguishable:
            self.nodes.remove(node)


def calculate_dominating_mutants(kill_map):
    """Calculates a dominating set of mutants.
    Calculates the dominating set of mutants in a graph given a mapping from
    mutant identifiers to a set of identifiers of tests that kill each mutant.
    This function initializes a graph and adds all the mutant identifiers
    with their test identifiers in the kill map as initialized nodes to the
    graph. It then connects these nodes by establishing relationships between
    nodes that contain test identifiers that are subset or superset of each
    other. Finally, it returns a set of mutant identifiers with which contain a
    minimal set of test identifiers which would kill all the mutants in the
    kill map.


    Parameters:
        kill_map: A mapping from a set of identifiers from mutants killed to a
        set of identifiers for tests that kill each mutant.

    Returns:
        (tuple): containing
            graph : Graph
                The graph containing nodes that represent mutants
            dominator_mutants_set: set()
                The set of identifiers of mutants in a dominating set.
    """

    graph = Graph()
    # create nodes containing children and add them to the graph
    for mutant in kill_map:
        node = Node(mutant, kill_map.get(mutant))
        graph.add_node(node)

    graph.connect_nodes()

    dominator_mutants_set = set()
    for mutants in graph.nodes:
        if mutants.parents is None or len(mutants.parents) == 0:
            dominator_mutants_set.add(mutants.mutant_name)

    return graph, dominator_mutants_set
