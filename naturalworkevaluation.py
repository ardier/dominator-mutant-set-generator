import os.path
import re
from typing import Optional, Dict

from dominator_mutants import convert_csv_to_killmap


# results_dir is the directory where the results are stored is

def generate_natural_work_evaluation(results_dir):
    # TODO have to run the same analysis for each bug

    dirpath = "..\Lang\\1\killmatrix\\natural-mutants\\non-triggering"
    # step 2 fetch the killmap
    killmap = convert_csv_to_killmap(os.path.join(dirpath, "killMap.csv"))

    # step 3 in a dictionary (may have to change this) containing from the mutant identifier to token identifiers:
    #  {mutantID: token, sub-token} . the sub-token would be -1 if it’s the default subtoken.

    log_file_path = os.path.join(dirpath, "mutants.log")
    mutant_token_sub_mapping: Optional[dict] = \
        generate_mutant_to_token_mapping(generate_mutant_to_token_mapping(
            log_file_path))

    # TODO step 4


def generate_mutant_to_token_mapping(log_file):
    mutant_to_token_mapping: Optional[Dict[int, int[-1, -1]]] = dict()
    tokenization_pattern = re.compile(
        r"([0-9]*);[A-Z]*;([0-9]*);(([0-9]*)[A-Z]*)")
    with open(log_file, 'r') as fo:
        for line in fo:

            header_match = tokenization_pattern.match(line)
            if header_match:
                subtoken = -1
                if header_match.group(3) and str(header_match.group(3)) != \
                        "0L":
                    subtoken = int(header_match.group(3))
                mutant_to_token_mapping[int(header_match.group(1))] = [
                    int(header_match.group(2)), subtoken]
            continue
            raise ValueError("No pattern matched line: {}".format(line))
        return mutant_to_token_mapping


def generate_scores(mml_csv, mutant_token_mapping):
    print("placeholder")


if __name__ == "__main__":
    generate_natural_work_evaluation("..\\results")
