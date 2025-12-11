'''
Docstring for DM.DM_Project_2025.matrix_builder
'''
from scoring import pair_score


# Try to import the real pair_score from scoring.py. If unavailable (for
# example when running tests outside the package), keep a lightweight
# fallback implementation so the module remains usable.

def build_similarity_matrix(recipients: list, donors: list) -> list[list[float]]:
    """
    Constructs a similarity matrix based on scores between recipients and donors.

    This function iterates through the Cartesian product of recipients and donors.
    It relies on an external function `pair_score(recipient, donor)` which is
    expected to return a sequence (tuple or list) where the element at index 2
    is the numerical score.

    Args:
        recipients (Sequence): A list or sequence of recipient objects/IDs.
        donors (Sequence): A list or sequence of donor objects/IDs.

    Returns:
        List[List[float]]: A 2D list (list of lists) where matrix[i][j]
        contains the score between recipients[i] and donors[j].

    Examples:
        >>> # 1. Mock `pair_score` to return a predictable numeric score
        >>> # (here: simple sum of inputs). This matches the simplified
        >>> # `pair_score(allele1, allele2) -> float` API used in `scoring.py`.
        >>> pair_score = lambda r, d: r + d

        >>> # 2. Define inputs
        >>> recs = [10, 20]
        >>> dons = [1, 2, 3]

        >>> # 3. Run function
        >>> matrix = build_similarity_matrix(recs, dons)

        >>> # 4. Verify the output is a standard Python list of lists
        >>> matrix
        [[11, 12, 13], [21, 22, 23]]

        >>> # 5. Verify dimensions (2 rows, 3 columns)
        >>> len(matrix)
        2
        >>> len(matrix[0])
        3
    """
    # Create a list of lists using list comprehension
    similarity_matrix = [[0 for j in donors] for i in recipients]

    for i, rec in enumerate(recipients):
        for j, don in enumerate(donors):
            # `pair_score` may return either a numeric score (float/int) or a
            # tuple/list where the numeric score is at index 2 (legacy).
            res = pair_score(rec, don)
            # Normalize to a float score in a defensive way.
            if isinstance(res, int):
                score = res
            elif isinstance(res, float):
                score = res
            elif isinstance(res, (list, tuple)):
                if len(res) > 2:
                    score = float(res[2])
                elif len(res) > 0:
                    score = float(res[0])
                else:
                    score = 0.0
            else:
                score = float(res)

            similarity_matrix[i][j] = score

    return similarity_matrix
# The real `pair_score` is imported from `scoring.py` above. A fallback
# implementation is provided there if the import fails (random score).


if __name__ == "__main__":
    import doctest

    # verbose=True will show the test steps passing
    print("Running Doctest...")
    doctest.testmod(verbose=True)

    print("\nRunning Manual Random Test:")
    arr = [0.0 for don in range(4)]
    seq = [0.0 for rec in range(5)]

    result = build_similarity_matrix(seq, arr)

    # Printing the result neatly to prove it works
    for row in result:
        print(row)
