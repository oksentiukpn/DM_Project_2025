import random
from typing import Sequence
#from hla_types import HLAPerson
#from scoring import pair_score

# NOTE: In production, pair_score would be imported.
# For the function to work without the import active,
# pair_score must be defined in the global scope (see main block).

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
        >>> # 1. Mock pair_score to return a predictable number (sum of inputs)
        >>> # We use 'global' so the function sees this mock, not the random one.
        >>> global pair_score
        >>> def pair_score(r, d):
        ...     return (0, 0, r + d)

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
            # Accessing index 2 as per requirement
            similarity_matrix[i][j] = pair_score(rec, don)[2]

    return similarity_matrix


# /----------TESTING environment-----/
def pair_score(a, b):
    # This random version is used when running the script normally
    # (outside of doctest)
    ans = random.random()
    return (0, 0, ans)


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
