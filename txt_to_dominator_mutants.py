import re
from typing import Optional, Set, Dict


# Init nodes because it provides better abstraction
class Node:
    tests: Set[int]
    mutant_name: Set[int]
    children: Set[int]
    parents: Set[int]
    """The node object that represents mutants

    """

    def __init__(self, mutant_name=None, children_string_set=None):
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
        if mutant_name == None:
            mutant_name = set()
        self.mutant_name = mutant_name
        self.tests = set()
        if children_string_set == None:
            children_string_set = set()
        self.children_string_set = children_string_set
        self.children = set()
        self.parents = set()


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
        self.nodes.append(new_node)

    # TODO - also write spec
    def connect_nodes(self):
        for node in self.nodes.copy():
            # match the children by string name and add them
            for child_listed in node.children_string_set:
                for node2 in self.nodes.copy():
                    if node2.mutant_name == frozenset({child_listed}):
                        node.children.add(node2)
                        node2.parents.add(node)

    def generate_dominator_set(self):
        dominator_set: Optional[set()] = set()
        dominator_set_by_name: Optional[set()] = set()
        for node in self.nodes:
            if node.parents == set():
                dominator_set.add(node)
                dominator_set_by_name.add(node.mutant_name)
        return dominator_set, dominator_set_by_name

    # TODO -  create function to rename nodes once all is done


# Credit to Sam Kaufman for rewriting most of the code for the following loop
def txt_to_mutant_relation(txt_file):
    subsumption_header_pattern = re.compile(
        r"\s+group (\d+) subsumes (\d+) groups\s*")
    subsumption_relationship_pattern = re.compile(r"\s+subsumes group (\d+)\s*")

    began_subsumption_section = False
    began_group_to_mutant_section = False
    current_group_id: Optional[int] = None
    relationships2: Optional[Dict[frozenset, frozenset]] = dict()
    group_names: Optional[Dict[frozenset, frozenset]] = dict()

    group_header_pattern = re.compile(
        r"\s+group (\d+) contains \d+ mutants\s*")
    group_id_to_name_pattern = re.compile(r"\s+group ((\d)*) contains mutant ((\d)*)")
    mutant_lives_header_pattern = re.compile(r"\s+group (\d+) contains \d+ mutants  with dominance scores Dl = -1.0")
    mutant_lives_indicator_pattern = re.compile(r"(.*)-1.0")

    # keep track of mutants who live
    living_mutants: Optional[set()] = set()

    # TODO combine
    with open(txt_file, 'r') as fo2:
        for line2 in fo2:
            if line2.strip() == "There are 64 minimal mutant groups.":
                break
            if line2.strip() == "All mutant groups:":
                began_group_to_mutant_section = True
                continue
            if not began_group_to_mutant_section:
                continue
            mutant_lives_header = mutant_lives_header_pattern.match(line2)
            if mutant_lives_header:
                living_mutants.add(int(mutant_lives_header.group(1)))
                continue
            mutant_lives = mutant_lives_indicator_pattern.match(line2)
            if mutant_lives:
                continue
            if not line2.strip():
                # Skip blank lines
                continue

            group_header_match = group_header_pattern.match(line2)
            if group_header_match:
                current_group_id2 = int(group_header_match.group(1))
                continue
            rel_match2 = group_id_to_name_pattern.match(line2)
            if rel_match2:
                assert current_group_id2 is not None
                name_set2 = frozenset({current_group_id2})
                set_holder2 = group_names.get(name_set2, set())
                set_holder2.add(int(rel_match2.group(3)))
                group_names[name_set2] = set_holder2
                # s.add(int(rel_match.group(1)))
                continue

            raise ValueError("No pattern matched line: {}".format(line2))

    with open(txt_file, 'r') as fo:
        for line in fo:
            if line.strip() == "Mutant subsumption:":
                began_subsumption_section = True
                continue
            if not began_subsumption_section:
                continue
            if not line.strip():
                # Skip blank lines
                continue
            header_match = subsumption_header_pattern.match(line)

            if header_match:
                if int(header_match.group(1)) in living_mutants:
                    continue
                current_group_id = int(header_match.group(1))
                subsumed_count = int(header_match.group(2))
                # adding groups that don't subsume other groups
                if subsumed_count == 0:
                    name_set = frozenset({current_group_id})
                    set_holder = relationships2.get(name_set, set())
                    relationships2[name_set] = set_holder
                continue
            rel_match = subsumption_relationship_pattern.match(line)
            if rel_match:
                assert current_group_id is not None
                name_set = frozenset({current_group_id})
                set_holder = relationships2.get(name_set, set())
                set_holder.add(int(rel_match.group(1)))
                relationships2[name_set] = set_holder
                # s.add(int(rel_match.group(1)))
                continue
            raise ValueError("No pattern matched line: {}".format(line))

    this_graph = Graph()
    for relation in relationships2:
        current_node = Node(relation, relationships2[relation])
        this_graph.add_node(current_node)

    this_graph.connect_nodes()
    dominator_set_by_group = this_graph.generate_dominator_set()
    # print("dominator_set_by_group:", dominator_set_by_group[1])

    dominator_set_by_mutant_name: Optional[set()] = set()
    for dominant_node in dominator_set_by_group[1]:
        # print(group_names[dominant_node])
        dominator_set_by_mutant_name.add(frozenset(group_names[dominant_node]))

    return dominator_set_by_mutant_name
