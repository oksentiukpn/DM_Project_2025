'''
Matching module
'''
from copy import deepcopy
MIN_ACCEPT = 0.6
INF = 1e9

# similarity = [
#     [0.5, 0.2, 0.7],
#     [0.1, 0.6, 1.0],
#     [0.4, 0.5, 0.3]
# ]

def convert_similarity(arr: list) -> list:
    '''
    Converting similarity to cost
    like similarity 0.7 to 1-0.7 = cost

    >>> similarity = [
    ... [0.5, 0.2, 0.7],
    ... [0.1, 0.6, 1.0],
    ... [0.4, 0.5, 0.9]]

    >>> convert_similarity(similarity)
    [[0.5, 0.8, 0.3], [0.9, 0.4, 0.0], [0.6, 0.5, 0.1]]
    '''

    return [[round(1-value, 1) for value in row] for row in arr]


def remove_not_accepted(arr: list) -> list:
    '''
    Make cost INF if similarity < 60%

    >>> similarity = [
    ... [0.5, 0.2, 0.7],
    ... [0.1, 0.6, 1.0],
    ... [0.4, 0.5, 0.9]]

    >>> similarity = convert_similarity(similarity)
    >>> remove_not_accepted(similarity)
    [[1000000000.0, 1000000000.0, 0.3], [1000000000.0, 0.4, 0.0], [1000000000.0, 1000000000.0, 0.1]]
    '''
    return [[(value if value <= 1-MIN_ACCEPT else INF) for value in row] for row in arr]


def match(arr: list):
    '''
    Func

    >>> matrix = [
    ... [5, 7, 8],
    ... [9, 5, 10],
    ... [6, 9, 5]]
    >>> match(matrix)
    '''
    arr2 = deepcopy(arr)
    n = len(arr2)

    # Step 1 & 2
    def reduction(arr_copy: list):
        '''
        Func

        >>> matrix = [
        ... [0.5, 0.2, 0.7],
        ... [0.1, 0.6, 1.0],
        ... [0.4, 0.5, 0.9]]
        >>> reduction(matrix)
        '''
        # First we reducing rows
        arr_copy = [[value - min(row) for value in row] for row in arr_copy]
        # Finding mins for columns
        col_mins = [min(row[i] for row in arr_copy) for i in range(len(arr_copy[0]))]
        # Reducing columns
        arr_copy = [[arr_copy[r][c] - col_mins[c] for c in range(len(col_mins))] for r in range(n)]
        return [[round(value, 2) for value in row] for row in arr_copy]

    # Step 3
    def cover_zeros(matrix: list):
        '''
        Func
        '''
        assigned = [-1] * n

        for r in range(n):
            for c in range(n):
                if matrix[r][c] == 0 and c not in assigned:
                    assigned[r] = c
                    break

        marked_rows = {r for r in range(n) if assigned[r] == -1}
        marked_cols = set()

        changed = True
        while changed:
            changed = False
            for r in list(marked_rows):
                for c in range(n):
                    if matrix[r][c] == 0 and c not in marked_cols:
                        marked_cols.add(c)
                        changed = True
            for r in range(n):
                if assigned[r] in marked_cols and r not in marked_rows:
                    marked_rows.add(r)
                    changed = True

        line_rows = [r for r in range(n) if r not in marked_rows]
        line_cols = list(marked_cols)

        return line_rows, line_cols

    lines = cover_zeros(reduction(arr2))

    def adjust_matrix(matrix: list, covers: tuple[list, list]) -> list:
        '''
        Func
        '''
        row_cover, col_cover = covers
        row_cover = [i in row_cover for i in range(n)]
        col_cover = [i in col_cover for i in range(n)]
        min_uncovered = float('inf')
        for r in range(n):
            if not row_cover[r]:
                for c in range(n):
                    if not col_cover[c]:
                        min_uncovered = min(min_uncovered, matrix[r][c])
        k = min_uncovered
        for r in range(n):
            for c in range(n):
                if not row_cover[r] and not col_cover[c]:
                    matrix[r][c] -= k
                elif row_cover[r] and col_cover[c]:
                    matrix[r][c] += k

        return matrix




    if len(lines[0]) + len(lines[1]) != n:
        return adjust_matrix(reduction(arr2), lines)
    else:
        return lines
if __name__ == "__main__":
    import doctest
    print(doctest.testmod())
