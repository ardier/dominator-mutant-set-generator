from typing import Set


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
        if not self.is_distinguishable_from(new_node):
            if not self == new_node:
                self.merge_indistinguishable_nodes(new_node, graph)

        # Determining dominance vs. subsumption using test identifiers
        else:
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
        if self.children != set():
            for child in self.children:

                if child.tests.issubset(new_node.tests):

                    # Determining where new_node is going to be on the graph
                    # relative to the self's child
                    child.determine_mutant_subsumption(new_node, graph)

                else:
                    # Adding node
                    self.add_children_in_between(new_node, child)

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
        if self.parents != set():
            for parent in self.parents:

                if parent.tests.issuperset(new_node.tests):

                    # adding new_node as a relative of self's child
                    parent.determine_mutant_subsumption(new_node, graph)

                else:
                    parent.add_children_in_between(new_node, self)

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
        if n2 not in graph.indistinguishable:
            graph.indistinguishable.append(n2)

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

    def add_node(self, node):
        """Adds a given node to the list of the nodes on the graph

        If the node that is passed in is a valid instance of Node class,
        this function adds the given node to the graph, but it doesn't create
        a relation between the existing nodes and the newly added node.

        Parameters:
            node: Node
                Node that is being added to this graph

        """
        if isinstance(node, Node) and node not in self.nodes:
            self.nodes.append(node)

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

            self.nodes_added.append(self.nodes[n1])
            for n2 in range(0, len(self.nodes_added)):

                # If the nodes are the same
                # or if at least the set of test identifiers in one of them is
                # not a subset of the other one, move on to the next node

                if n1 == n2 or \
                        not (self.nodes[n2].tests.issubset(
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

        for node in self.indistinguishable:
            self.nodes.remove(node)


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

    Finally, it returns a set of mutant identifiers which contain a
    minimal set of test identifiers which would kill all the mutants in the
    kill map.


    Parameters:
        kill_map: A mapping from a set of identifiers from mutants killed to a
        set of identifiers for tests that kill each mutant.

    Returns:
        (tuple): containing
            graph : Graph
                The graph containing nodes that represent mutants
            dominator_mutants_set: set[int]
                The set of identifiers of mutants in a dominating set.
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
    for mutants in graph.nodes:
        if mutants.parents == None or len(mutants.parents) == 0:
            dominator_mutants_set.add(mutants.mutant_name)

    return graph, dominator_mutants_set
