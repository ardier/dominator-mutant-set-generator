from _ast import Assert
from unittest import TestCase
import cv2
import numpy as np
import tc


class Test(TestCase):

    def test_csv_reader_printing(self):
        """This function tests whether the CSV reader can read the csv file.

                       """

        filename = "test-data/test.csv"
        result = tc.read_csv(filename)
        print(result)

    def test_csv_reader_empty_input(self):
        """This function tests whether the read_csv can handle invalid input.

                       """

        filename = "nonsense"
        with self.assertRaises(Exception) as context:
            tc.read_csv(filename)

        self.assertTrue('Invalid input' in str(context.exception))

    def test_csv_reader_basic_results_check(self):
        """This function tests whether the read_csv outputs a valid dictionary.

                               """
        filename = "test-data/test.csv"
        result = tc.read_csv(filename)
        expected_result = {1: {1, 2}, 2: {1, 2}, 3: {1, 3}, 4: {4}}
        self.assertEqual(expected_result, result)

    def test_kill_count(self):
        """This function tests whether the kill_count outputs a valid dictionary.

                               """
        test_input = {1: {1, 2}, 2: {1, 2}, 3: {1, 3}, 4: {4}}
        result = tc.count_kill(test_input)
        expected_result = {1: 2, 2: 2, 3: 2, 4: 1}
        self.assertEqual(expected_result, result)

    def test_sorter(self):
        """This function tests whether the sort_ outputs a valid list of tuples.

                               """
        test_input = {1: 2, 2: 2, 3: 2, 4: 1}
        result = tc.sort_(test_input)
        expected_result = [(1, 2), (2, 2), (3, 2), (4, 1)]
        self.assertEqual(expected_result, result)

    def test_plot(self):
        """This function tests whether the plot actually plots the input coordinates.
                                      """
        test_input = ([[0, 0], [1, 2], [2, 3], [3, 4]])
        test_input2 = {1: {1, 2}, 2: {1, 2}, 3: {1, 3}, 4: {4}}
        test_input3 = [1, 2, 3, 4]

        # Assert
        # open("test-data/test-1.png", "rb").read() == tc.plot(test_input, test_input2, test_input3),
        # 'The output is invalid'
        # actual = cv2.imread(tc.plot(test_input, test_input2, test_input3))
