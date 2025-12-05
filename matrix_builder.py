import numpy as np
from typing import Sequence
#from hla_types import HLAPerson
#from scoring import pair_score


def build_similarity_matrix(recipients : Sequence , donors : Sequence) -> np.ndarray:
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
        np.ndarray: A 2D float array of shape (len(recipients), len(donors)),
            where matrix[i, j] contains the score between recipients[i] and donors[j].

    Examples:
        >>> import numpy as np
        >>> recs = [10, 20]
        >>> dons = [1, 2, 3]
        >>> matrix = build_similarity_matrix(recs, dons)
        >>> matrix.shape
        (2, 3)
    """
    similarity_matrix = [[0 for j in donors] for i in recipients]
    for i,rec in enumerate(recipients):
        for j,don in enumerate(donors):
            similarity_matrix[i][j] = pair_score(rec , don)[2]
    return similarity_matrix



#/----------TESTING-----/
def pair_score(a,b):
    ans = np.random.random()
    return (0,0,ans)


if __name__ == "__main__":
    import doctest
    print(doctest.testmod())
    arr = [0.0 for don in range(4)]
    seq = [0.0 for rec in range(5)]
    print(build_similarity_matrix(arr,seq))
