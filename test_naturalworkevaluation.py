from unittest import TestCase

# TODO achieve %100 code coverage
import naturalworkevaluation


# TODO use test.txt and test2.txt for tests


class Test(TestCase):
    def test_traditional_naturalness(self):
        print(naturalworkevaluation.plot_traditional_naturalness(
            "..\\Pojo\\Lang\\1\\killmatrix"))
