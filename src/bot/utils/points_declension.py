def points_declension(points: int) -> str:
    """
    Declines the word 'балл' according to the Russian grammatical rules for numbers.
    :param points: The number of points for which the declension is needed.
    :return: The declined form of the word 'балл' based on the given number of points.
    """
    if points % 10 == 1 and points % 100 != 11:
        return "балл"
    elif 2 <= points % 10 <= 4 and not (12 <= points % 100 <= 14):
        return "балла"
    else:
        return "баллов"
