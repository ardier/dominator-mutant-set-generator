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
        (generate_mutant_to_token_mapping(log_file_path))

    # TODO step 4
    mml_file_path = os.path.join(dirpath, "mml_confidence_data.csv")
    mutant_token_sub_mapping: Optional[dict] = generate_scores(
        mutant_token_sub_mapping, mml_file_path)

def generate_mutant_to_token_mapping(log_file):
    mutant_to_token_mapping: Optional[Dict[int, int[-1, -1]]] = dict()
    tokenization_pattern = re.compile(
        r"([0-9]*);[A-Z]*;([0-9]*);((([0-9]*)[ ]*[a-z]*[A-Z]*[.]*[:]*[-]*[_]*[\"]*[']*)*)")
    with open(log_file, 'r') as fo:
        for line in fo:
            header_match = tokenization_pattern.match(line)
            if header_match:
                subtoken = -1
                if header_match.group(3):
                    subtoken = header_match.group(3)
                mutant_to_token_mapping[int(header_match.group(1))] = [
                    int(header_match.group(2)), subtoken]
            continue
            raise ValueError("No pattern matched line: {}".format(line))
        # TODO remove when done
        # for x in mutant_to_token_mapping:
        #    print(str(x)+" "+str(mutant_to_token_mapping[x]))
        return mutant_to_token_mapping


def generate_scores(mutant_token_mapping, mml_csv):
    token_prob_position_score: Optional[Dict[int[-1, -1], int[-1, -1]]] = dict()
    score_reading_pattern = re.compile(
        r"[A-Z_(]*([\d]*)[)]<([\d]*[\"]*[']*[ ]*[a-z]*[A-Z]*[.]*[:]*["
        r"\_]*[(]*[)]*[>]*)*-> ([\"'\d*[a-z]]*[.a-zA-Z0-9_\"',<> $?\[\]:("
        r")\\-]*)#\d.\d*([A-Z]-[0-9])*#(\d.\d*)([A-Z]-[0-9])*#[a-z]*#("
        r"\d.\d*)([A-Z]-[0-9])*#[a-z]*#[a-z]*#(\d.\d*([A-Z]-[0-9])*)*")

    with open(mml_csv, 'r') as fo:
        for line in fo:
            if line.strip() == "":
                continue
            header2_match = score_reading_pattern.match(line)
            # group 1 -> token number identifier
            # group 3 -> subtoken number identifier
            # group 5 -> ngramProb
            # group 9 -> positionscore
            # mutant_scores_mapping: {[token, subtoken]: []}
            if header2_match:
                token_prob_position_score[int(header2_match.group(1)),
                                          header2_match.group(3)[1:-1]] = \
                    [float(header2_match.group(5)), float(
                        header2_match.group(9))]
            continue
            raise ValueError("No pattern matched line: {}".format(line))

    # TODO create the actual mapping
    mutant_prob_position_score: Optional[
        Dict[int[-1, -1], int[-1, -1]]] = dict()
    return mutant_prob_position_score

if __name__ == "__main__":
    generate_natural_work_evaluation("..\\results")
