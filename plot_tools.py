import random
from turtle import pd
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd

from dominator_mutants import calculate_dominating_mutants
from graph_tools import total_subsumed_size
from statistics import import_all_pickles


def generate_eval_plot(sorted_mutants, killmap, rev_killmap,
                       total_number_of_mutants):
    """

    :param sorted_mutants: list [int]
            A pre-sorted list of mutant identifiers
    :param killmap: dict[frozenset: set()]
        A mapping from a set of identifiers from mutants killed to a
        set of identifiers for tests that kill each mutant.
    :param rev_killmap: dict[frozenset: set()]
        A mapping from a set of identifiers of tests to the
        set of identifiers for mutant that they kill.
    :param total_number_of_mutants: int
        The total number of mutants that were generated for this bug for this
        evaluation
    :return: list[float]
        A list of y-coordinates for the plot points representing work
        evaluation for a given type of mutants.
    """

    mutants_killed_so_far = set()
    plot: Optional[list[list]] = []
    plot.append(0)

    killmap_size = len(killmap)

    while True:
        # check if we are done whether it is by reaching the end or the plot
        # limit

        # Considers the total number of mutants
        if len(mutants_killed_so_far) == killmap_size:
            break

        # for the first mutant on the list of remaining mutants mutant select a test
        mutant_formatted_in_frozenset = sorted_mutants[0]

        # check whether the mutant was killed
        if mutant_formatted_in_frozenset in killmap.keys():
            # randomly select a test from the set off tests that kill that mutant
            randomly_selected_test = \
                random.sample(killmap[mutant_formatted_in_frozenset], 1)[0]
            # popping the key: test that kills all the value: mutant rev_killmap
            new_kills = rev_killmap.pop(randomly_selected_test)
            # popping all the mutants killed from killmap
            for mutant in new_kills:
                if mutant in killmap:
                    del killmap[mutant]
                    sorted_mutants.remove(mutant)

            # Remove the tests from all mutants.
            # this has to be done in a round about way
            for mutant in killmap.copy():
                # get all the remaining tests for that mutant minus the
                # currently randomly selected test
                randomly_selected_test_set = set()
                randomly_selected_test_set.add(randomly_selected_test)
                temp_mutant_test_set = killmap[mutant].difference(
                    randomly_selected_test_set)

                # if the test set is empty just break out of this inner loop
                if temp_mutant_test_set == set():
                    break
                # otherwise add the remaining tests back in
                else:
                    killmap[mutant] = temp_mutant_test_set

            mutants_killed_so_far = mutants_killed_so_far.union(new_kills)
            count = 0
            for mutant in mutants_killed_so_far:
                count += len(mutant)

            plot.append((count / total_number_of_mutants) * 100)
        else:

            sorted_mutants = sorted_mutants[1:]

    return plot, count


# TODO fix documentation
# TODO add title for each graph
def plot(plots):
    """Plots the test completeness graph


    Parameters:
         plot1: List[tuple(int, int)]
            A list of plot points that could used to plot test completeness
            """
    # traditional_random,
    # traditional_bestcase,
    # natural_naturalness[0][0],
    # natural_bestcase,
    # natural_random,
    # all_bestcase,
    # all_random,
    # all_naturalness,

    plot_names = ["Traditional Mutants -- Best Case (TB)",
                  "Traditional Mutants -- Random (TR)",
                  "Natural Mutants -- Best Case (NB)",
                  "Natural Mutants -- Random (NR)",
                  "Natural Mutants -- Naturalness  (NN)",
                  "All Mutants -- Best Case  (AB)",
                  "All Mutants -- Random (AR)",
                  "All Mutants -- Naturalness (AN)",
                  ]

    plots_info = [pd.DataFrame(data=d, columns=[n]) for n, d in zip(
        plot_names, plots)]
    maxi = max(len(i) for i in plots_info)
    increment = int(max(maxi, 1) / 10)
    if increment == 0:
        increment = 1

    # TODO factor out code here
    ax = plots_info[0].plot(fontsize=4,
                            xticks=(range(0, maxi, increment)),
                            yticks=range(0, 105, 25),
                            legend=False)

    for j in range(1, len(plots_info)):
        plots_info[j].plot(fontsize=4,
                           xticks=(range(0, maxi, increment)),
                           yticks=(range(0, 105, 25)),
                           legend=False, ax=ax)

    plt.legend()
    ax.set_xlabel("Work")
    ax.set_ylabel("Test Completeness")

    return plt


def generate_test_completeness_plot(kill_map):
    """Generates the test completeness plot

    Takes a mapping of mutants to the tests that kill them.
    Calls calculate_dominating_mutants on the given kill_map to store a
    dominator set of mutants.

    get_tests_covered is called on each of the mutants in the dominator
    set to generate a mapping of each dominator mutant to the set of tests
    (mutant test set) that kill that mutant.

    For each point plotted (each iteration) the tests that are used in the
    plot (tests that kill the presented mutant) are subtracted from the
    remaining mutants' test set. That is, if test t_A kills mutants m1, m2,
    and m3, once we explore mutant m1 and count test t_A towards one plotted
    point, we can no longer count it for m2, and m3 in subsequent plotted
    points.

    After each iteration the remaining mutants are re-sorted based on the
    number of remaining tests that kill them.

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
    plot = [0]

    dominator_to_subsumed_mapping: Optional[dict()] = dict()

    for dominator_mutant in dominator_set:
        temp = dominator_mutant.get_descendents()
        dominator_to_subsumed_mapping[dominator_mutant] = temp

    sorted_dominator_mutants = sorted(dominator_to_subsumed_mapping.keys(),
                                      key=lambda i:
                                      total_subsumed_size(i),
                                      reverse=True)

    # making sure each subsumed mutant is removed once using a triangular
    # double-loop
    mutants_considered_so_far: Optional[set()] = set()
    for dominator_mutant_index in range(0, len(sorted_dominator_mutants) - 1):
        for dominator_mutant_index2 in range(dominator_mutant_index + 1,
                                             len(sorted_dominator_mutants)):
            if dominator_to_subsumed_mapping[sorted_dominator_mutants[
                dominator_mutant_index2]] != set() and not \
                    sorted_dominator_mutants[
                        dominator_mutant_index2] in mutants_considered_so_far:
                dominator_to_subsumed_mapping[sorted_dominator_mutants[
                    dominator_mutant_index2]] = \
                    dominator_to_subsumed_mapping[sorted_dominator_mutants[
                        dominator_mutant_index2]].difference(
                        dominator_to_subsumed_mapping[sorted_dominator_mutants[
                            dominator_mutant_index]])

        # re-sort
        sorted_dominator_mutants = sorted(dominator_to_subsumed_mapping.keys(),
                                          key=lambda i:
                                          total_subsumed_size(i),
                                          reverse=True)
        mutants_considered_so_far.add(
            sorted_dominator_mutants[dominator_mutant_index])

    # we are now guaranteed to have unique subsumed mutants for each dominator
    # therefore, we can just plot the test completeness
    # Count the size of each node

    current_count = 0
    for dominator_mutant in sorted_dominator_mutants:
        current_count += dominator_mutant.size
        for mutant in dominator_to_subsumed_mapping[dominator_mutant]:
            current_count = current_count + mutant.size
        plot.append((current_count / len(kill_map)) * 100)

    return plot


def plots_all(all_data):
    for i in range(len(all_data)):
        graph = plot(all_data[i][1])
        print("Outputting the graph")
        graph.savefig("images2\\" + "lang_" + str(i) + ".png", dpi=800)


def plot_traditional(all_data):
    for i in range(len(all_data)):
        plots = all_data[i][1][0:2]
        plots.append(all_data[i][1][-1])
        graph = generate_traditional_plot(plots)
        print("Outputting the graph")
        graph.savefig("images2\\" + "lang_traditonal_" + str(i) + ".png",
                      dpi=800)


# TODO add documentation
def generate_traditional_plot(plots):
    """Plots the test completeness graph


        Parameters:
             plot1: List[tuple(int, int)]
                A list of plot points that could used to plot test completeness
                """
    # traditional_random,
    # traditional_bestcase,
    # natural_naturalness[0][0],
    # natural_bestcase,
    # natural_random,
    # all_bestcase,
    # all_random,
    # all_naturalness,

    plot_names = ["Traditional Mutants -- Best Case (TB)",
                  "Traditional Mutants -- Random (TR)",
                  "Traditional Mutants -- Naturalness (TN)"]

    plots_info = [pd.DataFrame(data=d, columns=[n]) for n, d in zip(
        plot_names, plots)]
    maxi = max(len(i) for i in plots_info)
    increment = int(max(maxi, 1) / 10)
    if increment == 0:
        increment = 1

    # TODO factor out code here
    ax = plots_info[0].plot(fontsize=4,
                            xticks=(range(0, maxi, increment)),
                            yticks=range(0, 105, 25),
                            legend=False)

    for j in range(1, len(plots_info)):
        plots_info[j].plot(fontsize=4,
                           xticks=(range(0, maxi, increment)),
                           yticks=(range(0, 105, 25)),
                           legend=False, ax=ax)
        # y1 = plots_info[0]
        # y2 = plots_info[1]
        # y3 = plots_info[2]

    plt.legend()
    ax.set_xlabel("Work")
    ax.set_ylabel("Test Completeness")
    plt.show()

    return plt


def plot_natural(all_data):
    for i in range(len(all_data)):
        graph = plot(all_data[i][1])
        print("Outputting the graph")
        graph.savefig("images2\\" + "lang_" + str(i) + ".png", dpi=800)


def plots_all(all_data):
    for i in range(len(all_data)):
        graph = plot(all_data[i][1])
        print("Outputting the graph")
        graph.savefig("images2\\" + "lang_" + str(i) + ".png", dpi=800)


def plot_all(all_data):
    for i in range(len(all_data)):
        graph = plot(all_data[i][1])
        print("Outputting the graph")
        graph.savefig("images2\\" + "lang_" + str(i) + ".png", dpi=800)


if __name__ == "__main__":
    all_data = import_all_pickles()
    # plots_all(all_data)
    plot_traditional(all_data)
    # plot_natural(all_data)
    # plot_all(all_data)
    print("test")
