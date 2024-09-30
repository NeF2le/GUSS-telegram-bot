from fuzzywuzzy import fuzz


def find_best_matched_person(person_full_name: str, persons_full_names: dict[int, str]) -> (int, int):
    """
    This function finds the best match for a given full name from a list of Person objects.
    It uses the fuzzywuzzy library to calculate the token sort ratio between the full names of the database
    and the input names. The function returns the best match Person object and the highest ratio found.

    :param person_full_name: The full name to find a match for.
    :param persons_full_names:
    :return:
    """
    best_match = None
    highest_ratio = 0
    for id_, full_name in persons_full_names.items():
        ratio = fuzz.WRatio(full_name, person_full_name)
        if ratio > highest_ratio:
            highest_ratio = ratio
            best_match = id_

    if best_match is not None:
        return best_match, highest_ratio
    else:
        return None, None
