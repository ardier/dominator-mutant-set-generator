from typing import Optional

import numpy as np

import naturalworkevaluation as nwe


def mutants_average(results_dir, type, number_of_trials=10):
    """ Runs evaluate_traditional_mutants_randomly for given number of times
    and averages the results before returning it. See documenation for
    evaluate_traditional_mutants_randomly

    :param results_dir: str
                    The directory containing the results files from tailored
                    mutant data
    :param type:

    :param number_of_trials: int
                the number of random trails that will conducted and then
                averaged for a given bug
    :return: tuple (list[int], int)
                    A tuple containing a list of y-cordinates (as a percentage)
                    for the work evaluation for random traditional mutants.
                    and the number of mutants for the evaluation
    """

    results_list: Optional[list] = list()
    results_list_shortened: Optional[list] = list()
    results_list_length_holder: Optional[list] = list()

    min_size = np.inf
    max_size = 0
    for i in range(0, number_of_trials):
        temp_result = nwe.bestcase_generator(results_dir, type)[0]
        results_list.append(temp_result)
        if min_size > len(temp_result):
            min_size = len(temp_result)

    for i in range(0, number_of_trials):
        results_list_shortened.append(results_list[i][:min_size])

        if len(results_list[i]) > min_size:
            results_list_length_holder.append(
                (i, len(results_list[i]) - min_size))
            if max_size < len(results_list[i]) - min_size:
                max_size = len(results_list[i]) - min_size

    # print("results list length holder",results_list_length_holder)
    results_list_additional_sums = [0] * max_size
    results_list_length_count = [0] * max_size
    # print(max_size, len(results_list_additional_sums))

    for row, random_result_length in results_list_length_holder:
        for col in range(min_size, min_size + random_result_length):
            # print(row, col, col - min_size, random_result_length)
            results_list_length_count[col - min_size] = 1 + \
                                                        results_list_length_count[
                                                            col - min_size]
            results_list_additional_sums[col - min_size] += \
                results_list[row][col]

    # print(results_list_length_count)
    # print("sums", results_list_additional_sums)
    result = np.mean([i for i in results_list_shortened], axis=0)
    # print(result)

    # adding the extra part at the end
    for i in range(len(results_list_length_count)):
        result = np.append(result, results_list_additional_sums[
            i] / results_list_length_count[i])

    # print(result)

    return result
