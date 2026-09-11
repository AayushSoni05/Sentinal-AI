from .text_normalization import normalize_text

def levenshtein_distance(first: str, second: str) -> int:
    """
    Calculate the Levenshtein edit distance between two strings.
    """

    first = normalize_text(first)
    second = normalize_text(second)

    if first == second:
        return 0

    if not first:
        return len(second)

    if not second:
        return len(first)

    previous_row = list(range(len(second) + 1))

    for i, first_char in enumerate(first, start=1):
        current_row = [i]

        for j, second_char in enumerate(second, start=1):
            insert_cost = current_row[j - 1] + 1
            delete_cost = previous_row[j] + 1
            replace_cost = previous_row[j - 1] + (
                first_char != second_char
            )

            current_row.append(
                min(insert_cost, delete_cost, replace_cost)
            )

        previous_row = current_row

    return previous_row[-1]


def levenshtein_similarity(first: str, second: str) -> float:
    """
    Convert Levenshtein distance into a normalized 0.0-1.0 similarity.
    """

    first = normalize_text(first)
    second = normalize_text(second)

    if not first and not second:
        return 1.0

    maximum_length = max(len(first), len(second))

    if maximum_length == 0:
        return 1.0

    distance = levenshtein_distance(first, second)

    return 1.0 - (distance / maximum_length)


def jaro_similarity(first: str, second: str) -> float:
    """
    Calculate the Jaro similarity between two strings.
    """

    first = normalize_text(first)
    second = normalize_text(second)

    if first == second:
        return 1.0

    if not first or not second:
        return 0.0

    first_length = len(first)
    second_length = len(second)

    match_distance = max(first_length, second_length) // 2 - 1

    if match_distance < 0:
        match_distance = 0

    first_matches = [False] * first_length
    second_matches = [False] * second_length

    matches = 0

    for i in range(first_length):
        start = max(0, i - match_distance)
        end = min(i + match_distance + 1, second_length)

        for j in range(start, end):
            if second_matches[j]:
                continue

            if first[i] != second[j]:
                continue

            first_matches[i] = True
            second_matches[j] = True
            matches += 1
            break

    if matches == 0:
        return 0.0

    first_sequence = [
        first[i]
        for i in range(first_length)
        if first_matches[i]
    ]

    second_sequence = [
        second[j]
        for j in range(second_length)
        if second_matches[j]
    ]

    transpositions = sum(
        first_char != second_char
        for first_char, second_char in zip(
            first_sequence,
            second_sequence,
        )
    ) / 2

    return (
        (matches / first_length)
        + (matches / second_length)
        + ((matches - transpositions) / matches)
    ) / 3


def jaro_winkler_similarity(
    first: str,
    second: str,
    prefix_scale: float = 0.1,
) -> float:
    """
    Calculate Jaro-Winkler similarity.
    """

    first = normalize_text(first)
    second = normalize_text(second)

    jaro_score = jaro_similarity(first, second)

    prefix_length = 0

    for first_char, second_char in zip(first, second):
        if first_char != second_char:
            break

        prefix_length += 1

        if prefix_length == 4:
            break

    return jaro_score + (
        prefix_length
        * prefix_scale
        * (1.0 - jaro_score)
    )


def name_similarity(first: str, second: str) -> dict[str, float]:
    """
    Calculate the required name similarity signals.

    The combined score is the arithmetic mean of the
    Jaro-Winkler and Levenshtein similarities.
    """

    jaro_winkler = jaro_winkler_similarity(first, second)
    levenshtein = levenshtein_similarity(first, second)

    combined = (jaro_winkler + levenshtein) / 2

    return {
        "jaro_winkler": round(jaro_winkler, 6),
        "levenshtein": round(levenshtein, 6),
        "combined": round(combined, 6),
    }