'''
Docstring for DM.DM_Project_2025.matrix_builder
'''
from scoring import pair_score

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
    #generate matrix
    similarity_matrix = [[0 for j in donors] for i in recipients]

    for i, rec in enumerate(recipients):
        for j, don in enumerate(donors):
            #calculate pair comparison
            res = pair_score(rec, don)
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

            #assign
            similarity_matrix[i][j] = score

    return similarity_matrix


if __name__ == "__main__":
    import doctest


    arr = [0.0 for don in range(4)]
    seq = [0.0 for rec in range(5)]



    result = build_similarity_matrix(seq, arr)

    for row in result:
        print(row)
