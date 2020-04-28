import re
from typing import Optional, Set, Dict


class Node:
    mutant_name: Set[int]
    children: Set[int]
    parents: Set[int]
    children_string_set: Set[int]
    """The node object that represents mutants

        This Node object is different from the one in dominator_mutants. 
        Read specs for details.

    """

    def __init__(self, mutant_name=None, children_string_set=None):
        """ Initiates node object

        Creates a node that represents mutants. If the mutant_name and/or
        children_string_set are passed in, it will set self.mutant_name and
        self.children_string_set to the values passed in. Otherwise,
        the function initiates them as the empty set (Set[int]).


        Parameters:
        mutant_name: set[int]
            The mutant's identifier is stored as a set so that when two
            indistinguishable mutants are merged their name could easily be
            merged (default None)
        children_string_set: set[int]
            A set of children identifiers that are subsumed by the mutant
            represented by this node (default None)

        Attributes:
        self.mutant_name: set[int]
            The mutant's identifier is stored as a set so that when two
            indistinguishable mutants are merged their name could easily be
            merged (default set[int])
        self.children_string_set: set[int]
            A set of children identifiers for the mutant represented
            by this node (default set[int])
        self.children: set[int]
            A set of mutant identifiers that represents mutants that are
            killed by a superset of tests that kill the mutant represented
            by this node (default set[int]).
        self.parents: set[int]
            A set of mutant identifiers that represents mutants that are
            killed by a subset of tests that kill the mutant represented by
            this node (default set[int]).

        """
        if mutant_name == None:
            mutant_name = set()
        self.mutant_name = mutant_name
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
            self.nodes : List[Node]
                A list of nodes that represents mutants that are added to the
                graph by create_edges


        """
        self.nodes = []

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

    def create_edges(self):
        """Creates edges and connects the nodes that are already placed in the
                graph.

                Comparing all possible pairs of nodes in the graph, if a node
                has name identifiers in its children_sting_set field,
                it creates two edges(one in each direction) between the
                child and parent nodes.

        """
        for node in self.nodes.copy():
            # match the children by string name and add them
            for child_listed in node.children_string_set:
                for node2 in self.nodes.copy():
                    if node2.mutant_name == frozenset({child_listed}):
                        node.children.add(node2)
                        node2.parents.add(node)

    def calculate_dominating_mutants(self):
        """Calculates a dominating set of mutants (with group identifiers)

            Calculates the dominating set of mutants in a graph instance by
            determining which one of the nodes in the graph does not have a
            parent.

            It returns two representations of the minimal set of mutants in two
            data types. The first one only contains name identifiers, whereas
            the second one contains node objects.

            Returns:
                (tuple): containing
                    dominator_mutants_set: set[int]
                        The set of name identifiers of mutants in a dominating
                        set.
                    dominator_mutants_set_actual_mutant: set[Node]
                        The set of Node objects representing mutants in a
                        dominating set.
            """

        dominator_mutants_set: Optional[set[int]] = set()
        dominator_mutants_set_actual_mutant: Optional[set[Node]] = set()
        for node in self.nodes:
            if node.parents == set():
                dominator_mutants_set_actual_mutant.add(node)
                dominator_mutants_set.add(node.mutant_name)
        return dominator_mutants_set, dominator_mutants_set_actual_mutant


# Credit to Sam Kaufman for providing most of the starter code for the
# following function most of the code for the following loop

# Due to the length of the .txt files, two different mappings are imported
# by iterating only once over the lines in the file to improve performance.
def import_mutant_relation(txt_file):
    """Imports the subsumpstion relation and mutant to group identifier from txt

        It takes a text file that contains mappings of group name identifiers
        to mutant names, subsumption relationship between groups of
        equivalent mutants, and their status after a test (lived/killed).

        This function uses regular expressions for pattern matching and
        iterates only once over the text file to generate the mappings.

        Parameters:
            txt_file: File (.txt)
                a text file that contains mappings of group name identifiers
                to mutant names, subsumption relationship between groups of
                equivalent mutants, and their status after a test (lived/killed)

        Returns
            (tuple): containing
                relationships : Dict[frozenset, frozenset]
                    A mapping from each mutant group identifier to the group
                    identifiers for the groups that mutant subsumes

                group_names : Dict[frozenset, frozenset]
                    A mapping from each mutant group identifier to its mutant
                    name identifiers

    """
    # Regex Patterns
    subsumption_header_pattern = re.compile(
        r"\s+group (\d+) subsumes (\d+) groups\s*")
    subsumption_relationship_pattern = re.compile(r"\s+subsumes group (\d+)\s*")
    group_header_pattern = re.compile(
        r"\s+group (\d+) contains \d+ mutants\s*")
    group_id_to_name_pattern = re.compile(
        r"\s+group ((\d)*) contains mutant ((\d)*)")
    mutant_lives_header_pattern = re.compile(
        r"\s+group (\d+) contains \d+ mutants  with dominance scores Dl = -1.0")
    mutant_lives_indicator_pattern = re.compile(r"(.*)-1.0")

    # Identifiers that help the program parse the text by letting it know if
    # it has reached a certain section
    began_subsumption_section = False
    began_group_to_mutant_section = False

    # Variable that store desired mappings and information
    current_group_id: Optional[int] = None
    relationships: Optional[Dict[frozenset, frozenset]] = dict()
    group_names: Optional[Dict[frozenset, frozenset]] = dict()

    # keep track of mutants who live
    living_mutants: Optional[Set[int]] = set()

    with open(txt_file, 'r') as fo:
        for line in fo:
            # using strip() where we can because it's easier
            if line.strip() == "There are 64 minimal mutant groups.":
                continue
            if line.strip() == "Mutant subsumption:":
                began_subsumption_section = True
                continue
            if line.strip() == "All mutant groups:":
                began_group_to_mutant_section = True
                continue
            if not began_group_to_mutant_section:
                continue

            # detecting a mutant that lives and should not be included in the
            # dominator list
            mutant_lives_header = mutant_lives_header_pattern.match(line)
            if mutant_lives_header:
                living_mutants.add(int(mutant_lives_header.group(1)))
                continue
            mutant_lives = mutant_lives_indicator_pattern.match(line)
            if mutant_lives:
                continue
            if not line.strip():
                # Skip blank lines
                continue

            # Group name => Mutant name mapping
            group_header_match = group_header_pattern.match(line)
            if group_header_match:
                current_group_id = int(group_header_match.group(1))
                continue
            rel_match2 = group_id_to_name_pattern.match(line)
            if rel_match2:
                assert current_group_id is not None
                name_set2 = frozenset({current_group_id})
                set_holder2 = group_names.get(name_set2, set())
                set_holder2.add(int(rel_match2.group(3)))
                group_names[name_set2] = set_holder2
                continue
            if not began_subsumption_section:
                continue

            # Parent => Children mapping
            header_match = subsumption_header_pattern.match(line)
            if header_match:
                if int(header_match.group(1)) in living_mutants:
                    continue
                current_group_id = int(header_match.group(1))
                subsumed_count = int(header_match.group(2))
                # adding groups that don't subsume other groups
                if subsumed_count == 0:
                    name_set = frozenset({current_group_id})
                    set_holder = relationships.get(name_set, set())
                    relationships[name_set] = set_holder
                continue
            rel_match = subsumption_relationship_pattern.match(line)
            if rel_match:
                assert current_group_id is not None
                name_set = frozenset({current_group_id})
                set_holder = relationships.get(name_set, set())
                set_holder.add(int(rel_match.group(1)))
                relationships[name_set] = set_holder
                continue
            raise ValueError("No pattern matched line: {}".format(line))
        return relationships, group_names


def generate_dominator_mutants(relationships, group_names):
    """Generates the dominator mutant set

        This function takes two mappings:
            1- Parent to children for each mutant in the graph by their
            mutant group identifiers
            2- Group identifier to mutant identifiers

        And generates a minimal dominator set

        Parameters
            relationships : Dict[frozenset, frozenset]
                A mapping from each mutant group identifier to the group
                identifiers for the groups that mutant subsumes

            group_names : Dict[frozenset, frozenset]
                A mapping from each mutant group identifier to its mutant name
                identifiers
        Returns
            (tuple): containing
                dominator_set_by_mutant_name: set[frozenset]
                    The set of mutant name identifiers of mutants in a
                    dominating set.

                dominator_set_by_group: set[int]
                    The set of group name identifiers of mutants in a
                    dominating set.
    """
    this_graph = Graph()
    for relation in relationships:
        current_node = Node(relation, relationships[relation])
        this_graph.add_node(current_node)

    this_graph.create_edges()
    dominator_set_by_group = this_graph.calculate_dominating_mutants()[0]

    dominator_set_by_mutant_name: Optional[set[frozenset]] = set()
    for dominant_node in dominator_set_by_group:
        dominator_set_by_mutant_name.add(frozenset(group_names[
                                                       dominant_node]))

    return dominator_set_by_mutant_name, dominator_set_by_group
