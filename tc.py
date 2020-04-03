from typing import Optional, Set


class Node:
    tests: Optional[Set[int]]
    mutant_name: Optional[Set[int]]
    children: Optional[Set[int]]
    parents: Optional[Set[int]]
    """The node object that represents mutants

    Parameters:
        mutant_name: set[int]
            The mutant's identifier is stored as a set so that when two
            indistinguishable mutants are merged, their name could easily
            be merged (default None).
        tests: set[int]
            A set of test identifiers that fail for the mutant represented by
            this node (default None).
        children: set[int]
            A set of mutant identifiers that represent mutants that are
            killed by a superset of tests that kill the mutant represented
            by this node (default None).
        parents: set[int]
            A set of mutant identifiers that represent mutants that are
            killed by a subset of tests that kill the mutant represented by
            this node (default None).

    Attributes:
        self.mutant_name: set[int]
            The mutant's identifier is stored as a set so that when two
            indistinguishable mutants are merged their name could easily
            merged (default None)
        self.tests: set[int]
            A set of test identifiers that fail for the mutant represented
            by this node (default None)
        self.children: set[int]
            A set of mutant identifiers that represent mutants that are
            killed by a superset of tests that kill the mutant represented
            by this node (default None).
        self.parents: set[int]
            A set of mutant identifiers that represent mutants that are
            killed by a subset of tests that kill the mutant represented by
            this node (default None)..

    """

    def __init__(self, mutant_name=None, tests=None, children=None,
                 parents=None):
        self.mutant_name = mutant_name
        self.tests = tests
        self.children = children
        self.parents = parents

    def place_mutant_in_graph(self, new_node, graph, relationship="unknown"):

        """Places new_node relative to this node in the graph.

        Assumes that the nodes that are passed in are related.
        If empty, it initiates parents and children member variables as
        empty sets for this node and new_node.

        Checks whether this node and new_node are distinguishable nodes, and if
        they are, it relates them recursively.
        If there are no possible nodes in between the two given nodes,
        then they become related as using their child/parent identifiers.

        Otherwise, it compares all the test identifiers for all the nodes in
        children/parents of this node.

        If there exists another node between this node and new_node whose
        tests are a subset of this node/new_node and the superset of the other
        one, place_mutant_in_graph then recursively adds new_node to that node.

        Parameters:
            new_node: Node
                A new node representing a mutant that is being added to the the
                graph
            graph: Graph
                A graph containing nodes that represent mutants
            relationship : str
                A string that indicates the kind of relationship being added.
                Possible inputs are"subsumed", "dominant", or "unknown".
                (default = unknown)

            """
        # TODO figure out why the program break when we delete this chunk of
        #  code
        if self.children == None:
            self.children = set()
        if self.parents == None:
            self.parents = set()
        if new_node.children == None:
            new_node.children = set()
        if new_node.parents == None:
            new_node.parents = set()

        if not self.is_distinguishable_from(new_node):
            if not self == new_node:
                self.merge_indistinguishable_nodes(new_node, graph)

        else:
            relation, relationship = self.build_relation_list(new_node,
                                                              relationship)

            relationship_possibility_with_relatives = False
            if relation[0] == set():
                relation[3].add_children(relation[4])
                relationship_possibility_with_relatives = True

            elif relation[0] != None and new_node not in relation[0]:
                relationship_possibility_with_relatives = True
                for relative in relation[0]:
                    if relationship == "subsumed":
                        relation.append(relative.parents)
                    else:
                        relation.append(relative.children)

                    if relationship == "subsumed" and relative.tests.issubset(
                            new_node.tests):

                        # adding new_node as a relative of self's child
                        relative.place_mutant_in_graph(new_node, graph,
                                                       "subsumed")

                    elif relative.tests.issuperset(
                            new_node.tests):
                        # adding new_node as a relative of self's parent
                        relative.place_mutant_in_graph(new_node, graph,
                                                       "dominant")

                    else:
                        self.add_children_in_between(new_node, relation,
                                                     relative)

            if relationship_possibility_with_relatives is False:
                relation[3].add_children(relation[4])

    def add_children(self, new_node):
        self.children.add(new_node)
        new_node.parents.add(self)

    def add_children_in_between(self, new_node, relation, relative):
        relation[2].add(relative)
        relation[1].add(self)
        relation[0].add(new_node)
        relation[0].remove(relative)
        relation[5].add(new_node)
        relation[5].remove(self)

    def build_relation_list(self, new_node, relationship):
        relation = list()
        if self.tests.issubset(
                new_node.tests):
            relationship = "subsumed"
            relation.append(self.children)
            relation.append(new_node.parents)
            relation.append(new_node.children)
            relation.append(self)
            relation.append(new_node)

        else:
            relationship = "dominant"
            relation.append(self.parents)
            relation.append(new_node.children)
            relation.append(new_node.parents)
            relation.append(new_node)
            relation.append(self)

        return relation, relationship

    def merge_indistinguishable_nodes(self, n2, graph):
        """Merges two nodes that represent mutants in a given graph.

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
        comparison, and their test identifiers.


        Parameters:
            n2: Node
                The mutant being compared to this mutant

        Return:
            True if the nodes representing mutants are distinguishable,
            False otherwise.

        """

        return (self != n2) and (self.tests != n2.tests)


class Graph:
    """The graph object that represents the mutant domination graph

    Attributes:
        self.nodes_added : list()
            A list of nodes that represents mutants that are added to the graph
        self.indistinguishable : list()
            A list of nodes that represents indistinguishable mutants that
            are going to be removed

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
            node: Node
                Node that is being added to this graph

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

        Finally, it removes indistinguishable nodes, keeping only one node
        out of each set of indistinguishable nodes.

            """
        for n1 in range(0, len(self.nodes)):

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
                        self.nodes[n2].place_mutant_in_graph(self.nodes[n1],
                                                             self)

        for node in self.indistinguishable:
            self.nodes.remove(node)


def calculate_dominating_mutants(kill_map):
    """Calculates a dominating set of mutants.

    Calculates the dominating set of mutants in a graph given a mapping from
    mutant identifiers to a set of identifiers of tests that kill each mutant.

    This function initializes a graph and adds all the mutant identifiers
    with their test identifiers in the kill map as initialized nodes to the
    graph.

    It then connects these nodes by establishing relationships between
    nodes that contain test identifiers that are subset or superset of each
    other.

    Finally, it returns a set of mutant identifiers with which contain a
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
    # create nodes containing children and add them to the graph
    for mutant in kill_map:
        node = Node(mutant, kill_map.get(mutant))
        graph.add_node(node)

    graph.connect_nodes()

    dominator_mutants_set = set()
    for mutants in graph.nodes:
        if mutants.parents == None or len(mutants.parents) == 0:
            dominator_mutants_set.add(mutants.mutant_name)

    return graph, dominator_mutants_set
