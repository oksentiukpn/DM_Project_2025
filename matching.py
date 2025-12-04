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
    ... [40, 60, 15],
    ... [25, 30, 45],
    ... [55, 30, 25]]
    >>> match(matrix)
    '''
    arr_copy = deepcopy(arr)
    n = len(arr_copy)

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
    def find_lines(matrix: list[list], dels: tuple[list, list]):
        '''
        Func
        '''
        rows_zeros = []
        col_zeros = []
        for row in matrix:
            rows_zeros.append(row.count(0))
        for i in range(n):
            col = []
            for row in matrix:
                col.append(row[i])
            col_zeros.append(col.count(0))
        zeros = rows_zeros + col_zeros
        max_zeros = zeros.index(max(zeros))
        if max_zeros < n:
            dels[0][max_zeros] = True
            matrix[max_zeros] = [-1 for n in matrix[max_zeros]]
        else:
            dels[1][max_zeros - n] = True
            for row in matrix:
                row[max_zeros - n] = -1
        a, b = dels
        if sum(row.count(0) for row in matrix) == 0:
            return (a.count(True) + b.count(True) == n, dels)
        return find_lines(matrix, dels)
    arr2 = reduction(arr_copy)
    lines = find_lines(deepcopy(arr2), ([False for _ in range(n)], [False for _ in range(n)]))


    # Step 4
    def shift(matrix: list[list], dels: tuple[bool, list]):
        min_v = min(min(row) for row in matrix)
        for index, row in enumerate(matrix):
            if dels[0][index]:
                row = [n + min_v if dels[0][i] else n for i, n in enumerate(row)]
                continue
            row = [n - min_v for n in row]
        return matrix

    while not lines[0]:
        arr2 = shift(arr2, lines[1])
        lines = find_lines(deepcopy(arr2), ([False for _ in range(n)], [False for _ in range(n)]))
    # Step 5!
    def choose_zeros(matrix: list[list]):
        '''
        Docstring for choose_zeros

        :param matrix: Description
        '''
        chosen = []
        while len(chosen) != n:
            for i, row in enumerate(matrix):
                if row.count(0) == 1:
                    j = row.index(0)
                    chosen.append((i, j))
                    row = [-1 for _ in row]
                    for _row in matrix:
                        _row[j] = -1
        return chosen

    return choose_zeros(arr2)

if __name__ == "__main__":
    import doctest
    print(doctest.testmod())
