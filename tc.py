import csv
import pandas as pd
import matplotlib.pyplot as plt


def read_csv(csv_filename):
    """This function reads CSV files containing killMaps and outputs the killMap as a dictionary of mutants to a set of
     tests that fail when that mutant is presented..

    Parameters:
        csv_filename (Path): The killMap passed in as a CSV file.

    Returns:
        completeness_in_reader: A dictionary of mutants to a set of tests that fail when that mutant is presented.
    """

    # TODO fix assert
    assert csv_filename.__contains__(".csv"), 'Invalid input'

    # begin reading the file
    with open(csv_filename, newline='') as File:
        # Create an empty dictionary
        completeness_in_reader = {}
        reader = csv.reader(File)

        # skipping the header
        next(reader)
        for k, y in reader:
            # converting to integers
            k = int(k)
            y = int(y)
            s = completeness_in_reader.get(y, set())
            s.add(k)
            completeness_in_reader[y] = s
        return completeness_in_reader


# Some global variable - may change generate_plot_points to return a tuple instead in the future
# A list of tests explored thus far
tests_explored = set()

# A minimal list of mutants as tuples that maps mutants to the number of unique tests they kill
sorted_count_non_duplicate = []


def count_kill(completeness):
    """Counts how many tests are killed for a presented mutant, and sorts mutants by the number of tests they kill.

    Parameters:
        completeness: A dictionary of mutants to tests that fail when that mutant is presented.

    Returns:
        count_sorted: A sorted list of tuples that stores mutants and the number of tests they kill in descending order

            """
    unsorted_count = {}
    for size in completeness:
        s = len(completeness.get(size))
        unsorted_count[size] = s
    count_sorted = sorted(unsorted_count.items(), key=lambda w: w[1], reverse=True)
    return count_sorted


def create_minimal_dominator_set_to_count_mapping(sorted_count, completeness):
    """Creates a minimal list of tuples that maps dominator mutants to the number of tests they kill
        The mutants that kill the same set of tests or a smaller subset of tests are omitted in this list

    Parameters:
        sorted_count: A sorted list of tuples that stores mutants and the number of tests they kill in descending order
        completeness: An unsorted dictionary that maps mutants to the number tests the fail for

    Returns:
        sorted_count_non_duplicate: A minimal list of mutants as tuples that maps mutants to the number of
        unique tests they kill

            """
    global sorted_count_non_duplicate
    global tests_explored
    for x in sorted_count:

        test_name = x[0]
        failing_test = completeness.get(test_name)

        if failing_test:

            # remove test that are already detected
            failing_test = failing_test - tests_explored
            if failing_test:
                sorted_count_non_duplicate.append((test_name, len(failing_test)))

                tests_explored = tests_explored | failing_test
    sorted_count_non_duplicate = sorted(sorted_count_non_duplicate, key=lambda u: -u[1])
    tests_explored = sorted(tests_explored)
    return sorted_count_non_duplicate


def generate_plot_points(sorted_count_non_duplicate_remover):
    """removes tests that are already killed by a mutant that has a larger set of tests
        from the remaining(smaller or equal) mutants' set of tests

    Parameters:
        sorted_count_non_duplicate_remover: A minimal list of mutants as tuples that maps mutants to the number of
        unique tests they kill

    Returns:
        current_test_completeness: A list of x-y coordinates that represents the test completeness for a minimal set of
        mutants

            """
    current_test_completeness = [[0, 0]]
    summer = 0

    # iterate between two tuples to gather information
    for i, test in zip(range(len(sorted_count_non_duplicate_remover)), sorted_count_non_duplicate_remover):
        summer += test[1]
        current_test_completeness.append([i + 1, summer])
    return current_test_completeness


def export_dominator_set_to_count_mapping_to_csv(sorted_count_non_duplicate):
    """This function writes a CSV file.

    Parameters:
        sorted_count_non_duplicate: A minimal list of mutants as tuples that maps mutants to the number of
        unique tests they kill

                    """
    with open('data/dominator_set.csv', 'w', newline='') as csvfile:
        wr = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        wr.writerow(['Mutant No', 'Number of tests'])
        for x, y in sorted_count_non_duplicate:
            wr.writerow([x, y])


def generate_dominator_set(completeness_in_reader):
    """Calculates a dominating set of mutants.
    Parameters:
        kill_map: A mapping from test identifiers to a set of identifiers for
            mutants killed.
    Returns:
        The set of identifiers of mutants in a dominating set.
    """
    # TODO(ardier): Extend this docstring with details about how it resolves
    #  indistinguishable mutants.
    test_sorted_count_main = count_kill(completeness_in_reader)
    dominator_set_main1 = create_minimal_dominator_set_to_count_mapping(test_sorted_count_main, completeness_in_reader)
    dominator_set = []
    for x in dominator_set_main1:
        dominator_set.append(x[0])
    return dominator_set


def plot(test_completeness_no_duplicates, sorted_count_non_duplicate, tests_explored):
    """plots test completes achieved on the y axis for for each unit of work which is a (dominator) mutant presented,
    where mutants are sorted by the number of unique tests they kill

    Parameters:
        test_completeness_no_duplicates: A sorted list of tuples that stores mutants and the number of tests
        they kill in descending order
        sorted_count_non_duplicate: A minimal list of mutants as tuples that maps mutants to the number of
        unique tests they kill
        tests_explored: A list of all mutants explored

            """
    plotter = pd.DataFrame(
        data=test_completeness_no_duplicates,
        columns=["Work", "Test Completeness"]
    )
    ax = plotter.plot(x='Work', y='Test Completeness', xticks=range(len(sorted_count_non_duplicate)),
                      yticks=range(0, len(tests_explored), 100), legend=False)
    ax.set_ylabel("Test Completeness")
    plt.show()


# putting it altogether
if __name__ == "__main__":
    filename = 'test-data/killMap.csv'
    completeness_main = read_csv(filename)
    print(completeness_main)
    test_sorted_count_main = count_kill(completeness_main)
    dominator_set_main = create_minimal_dominator_set_to_count_mapping(test_sorted_count_main, completeness_main)
    print(dominator_set_main)
    test_completeness_no_duplicates = generate_plot_points(dominator_set_main)
    print(test_completeness_no_duplicates)
    export_dominator_set_to_count_mapping_to_csv(sorted_count_non_duplicate)
    dominator_set = generate_dominator_set(completeness_main)
    print(dominator_set)
    plot(test_completeness_no_duplicates, sorted_count_non_duplicate, tests_explored)
