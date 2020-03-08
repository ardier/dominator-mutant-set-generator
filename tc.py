import csv
import pandas as pd
import matplotlib.pyplot as plt


def csv_reader(csv_filename):
    """This function reads CSV files containing killMaps.

        Parameters:
            csv_filename (Path): The killmap passed in as a CSV file.

        Returns:
            completeness_in_reader: A dictionary that of mutants to tests that fail when that mutant is presented.
                """
    assert csv_filename.__contains__(".csv"), 'Invalid input'

    # begin reading the file
    with open(csv_filename, newline='') as File:
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


def kill_count(completeness):
    """Count how many tests are killed for a presented mutant.

    Parameters:
        completeness: A dictionary of mutants to tests that fail when that mutant is presented.

    Returns:
        unsorted_weight: An unsorted dictionary that maps mutants to the number tests the fail for

            """
    unsorted_weight = {}
    for size in completeness:
        s = len(completeness.get(size))
        unsorted_weight[size] = s
    return unsorted_weight


def sorter(unsorted_weight):
    """Sorts mutants by the number of tests they kill.

    Parameters:
        unsorted_weight: A dictionary of mutants to the number of tests that fail when that mutant is presented.

    Returns:
        weight_sorted: A sorted list of tuples that stores mutants and the number of tests they kill in descending order

            """
    weight_sorted = sorted(unsorted_weight.items(), key=lambda w: w[1], reverse=True)
    return weight_sorted


# Some global variable - may change duplicate_remover to return a tuple instead in the future
# A list of tests explored thus far
tests_explored = set()

# A minimal list of mutants as tuples that maps mutants to the number of unique tests they kill
sorted_weight_non_duplicate = []


def duplicate_remover(sorted_weight_non_duplicate_remover):
    """removes tests that are already killed by a mutant that has a larger set of tests
        from the remaining(smaller or equal) mutants' set of tests

    Parameters:
        sorted_weight_non_duplicate_remover: A minimal list of mutants as tuples that maps mutants to the number of
        unique tests they kill

    Returns:
        current_test_completeness: A list of x-y coordinates that represents the test completeness for a minimal set of
        mutants

            """
    current_test_completeness = [[0, 0]]
    summer = 0

    # iterate between two tuples to gather information
    for i, test in zip(range(len(sorted_weight_non_duplicate_remover)), sorted_weight_non_duplicate_remover):
        summer += test[1]
        current_test_completeness.append([i + 1, summer])
    return current_test_completeness


def dominator_setter(sorted_weight, completeness):
    """Creates a minimal list of tuples that maps dominator mutants to the number of tests they kill
        The mutants the kill the same set of tests or a smaller subset of tests are omitted in this list

    Parameters:
        sorted_weight: A sorted list of tuples that stores mutants and the number of tests they kill in descending order
        completeness: An unsorted dictionary that maps mutants to the number tests the fail for

    Returns:
        sorted_weight_non_duplicate: A minimal list of mutants as tuples that maps mutants to the number of
        unique tests they kill

            """
    global sorted_weight_non_duplicate
    global tests_explored
    for x in sorted_weight:

        test_name = x[0]
        failing_test = completeness.get(test_name)

        if failing_test:

            # remove test that are already detected
            failing_test = failing_test - tests_explored
            if failing_test:
                sorted_weight_non_duplicate.append((test_name, len(failing_test)))
                tests_explored = tests_explored | failing_test

    sorted_weight_non_duplicate = sorted(sorted_weight_non_duplicate, key=lambda u: -u[1])
    tests_explored = sorted(tests_explored)
    return sorted_weight_non_duplicate


def dominator_export(sorted_weight_non_duplicate):
    """This function writes a CSV file.

    Parameters:
        sorted_weight_non_duplicate: A minimal list of mutants as tuples that maps mutants to the number of
        unique tests they kill

                    """
    with open('data/dominator_set.csv', 'w', newline='') as csvfile:
        wr = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        wr.writerow(['Mutant No', 'Number of tests'])
        for x, y in sorted_weight_non_duplicate:
            wr.writerow([x, y])


def plot(completeness, sorted_weight_non_duplicate, mutants_explored):
    """plots test completes achieved on the y axis for for each unit of work which is a (dominator) mutant presented,
    where mutants are sorted by the number of unique tests they kill

    Parameters:
        completeness: A sorted list of tuples that stores mutants and the number of tests they kill in descending order
        sorted_weight_non_duplicate: A minimal list of mutants as tuples that maps mutants to the number of
        unique tests they kill
        mutants_explored: A list of all mutants explored

            """
    plotter = pd.DataFrame(
        data=completeness,
        columns=["Work", "Test Completeness"]
    )
    ax = plotter.plot(x='Work', y='Test Completeness', xticks=range(len(sorted_weight_non_duplicate)),
                      yticks=range(0, len(mutants_explored), 100), legend=False)
    ax.set_ylabel("Test Completeness")
    plt.show()


# putting it altogether
if __name__ == "__main__":
    filename = 'test-data/killMap.csv'
    completeness_main = csv_reader(filename)
    unsorted_weights_main = kill_count(completeness_main)
    test_sorted_weight_main = sorter(unsorted_weights_main)
    dominator_set_main = dominator_setter(test_sorted_weight_main, completeness_main)
    print(dominator_set_main)
    test_completeness_main = duplicate_remover(dominator_set_main)
    dominator_export(sorted_weight_non_duplicate)
    plot(test_completeness_main, sorted_weight_non_duplicate, tests_explored)
