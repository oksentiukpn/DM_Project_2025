'''
Matching module
'''
import collections
from sys import exit as system32_termination
import random
from scipy.optimize import linear_sum_assignment

MIN_ACCEPT = 60
INF = float('inf')
BIGM = [[float(f'0.{n}') for n in random.choices(range(0, 100), k = 120)] for _ in range(90)]


def square(matrix: list[list]) -> list:
    '''
    Pads a rectangular matrix with 0.0 to make it square.

    If Donors (cols) > Recipients (rows):
        Adds dummy columns filled with 0.0.
        Donors assigned to these columns are effectively "unmatched".
    '''
    rows = len(matrix)
    cols = len(matrix[0])

    if rows == cols:
        return matrix
    if rows < cols:
        # Add dummy columns (Recipients)
        matrix.extend([[0 for _ in range(cols)] for _ in range((cols - rows))])
    else:
        print("\033[91mDonors must be >= recipients \033[0m")
        system32_termination()
    return matrix


def convert_similarity(arr: list) -> list:
    '''
    Converting similarity to cost
    like similarity 0.7 to 1-0.7 = cost
    Also converting to int and * 100 for easier working with ints
    >>> similarity = [
    ... [0.5, 0.2, 0.7],
    ... [0.1, 0.6, 1.0],
    ... [0.4, 0.5, 0.9]]

    >>> convert_similarity(similarity)
    [[50, 80, 30], [90, 40, 0], [60, 50, 10]]
    '''

    return [[int(round(1-value, 2)*100) for value in row] for row in arr]


def remove_not_accepted(arr: list) -> list:
    '''
    Make cost INF if similarity < 60%

    >>> similarity = [
    ... [0.5, 0.2, 0.7],
    ... [0.1, 0.6, 1.0],
    ... [0.4, 0.5, 0.9]]

    >>> similarity = convert_similarity(similarity)
    >>> remove_not_accepted(similarity)
    [[inf, inf, 30], [inf, 40, 0], [inf, inf, 10]]
    '''
    return [[(value if value <= 100-MIN_ACCEPT else INF) for value in row] for row in arr]


def match(arr: list):
    '''
    Func

    # >>> matrix = [
    # ... [40, 60, 15],
    # ... [25, 30, 45],
    # ... [55, 30, 25]]
    # >>> match(matrix)
    # [2, 0, 1]
    # >>> B = [[0.34, 0.6, 0.38, 0.82, 0.5, 0.76, 0.41, 0.38, 0.51, 0.69], [0.76, 0.57, 0.52, 0.73, 0.89, 0.5, 0.56, 0.96, 0.67, 0.5], [0.82, 0.8, 0.0, 0.6, 0.14, 0.0, 0.43, 0.61, 0.19, 0.31], [0.78, 0.55, 0.21, 0.51, 0.19, 0.92, 0.57, 0.65, 0.97, 0.11], [0.51, 0.47, 0.28, 0.83, 0.23, 0.4, 0.22, 0.27, 0.39, 0.84], [0.4, 0.58, 0.88, 0.63, 0.1, 0.52, 0.58, 0.13, 0.59, 0.11], [0.96, 0.34, 0.53, 0.69, 0.55, 0.88, 0.54, 0.28, 0.93, 0.64], [0.38, 0.6, 0.16, 0.7, 0.43, 0.69, 0.88, 0.97, 0.69, 0.28], [0.59, 0.4, 0.12, 0.41, 0.3, 0.15, 0.81, 0.93, 0.15, 0.1], [0.13, 0.19, 0.68, 0.97, 0.82, 0.7, 0.61, 0.65, 0.72, 0.9]]
    # >>> B = [n*100 for n in B]
    # >>> match(B)
    # [0, 3, 5, 9, 6, 4, 7, 2, 8, 1]
    '''
    # if len(arr) > len(arr[0]):
    #     pass
    n = len(arr)
    m = len(arr[0])

    valid = []
    dead = set()

    for i in range(n):
        if all(x == INF for x in arr[i]):
            dead.add(i)
        else:
            valid.append(i)

    if not valid:
        return [-1] * n # If everyone is dead
    sub_arr = [arr[i].copy() for i in valid]


    n = len(arr)
    for _ in range(m - n):
        arr.append([0]*m)
    n = len(arr)
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
        arr_copy = [[arr_copy[r][c] - col_mins[c] for c in range(n)] for r in range(n)]
        return [[value for value in row] for row in arr_copy]

    # Step 3
    def find_lines(matrix: list[list], prev: list = None):
        '''
        Func

        Was taken from 2-year algos studetns lecture
        '''
        # Building graph
        adj = [[] for _ in range(n)]
        for i, row in enumerate(matrix):
            for k, value in enumerate(row):
                if value == 0:
                    adj[i].append(k)

        # Hopcroft algorithm
        pair_u = prev.copy() if prev else [-1] * n
        pair_v = [-1] * n

        for u, v in enumerate(pair_u):
            if v != -1:
                pair_v[v] = u

        dist = [-1] * n

        def bfs():
            queue = collections.deque()
            for u in range(n):
                if pair_u[u] == -1:
                    dist[u] = 0
                    queue.append(u)
                else:
                    dist[u] = INF
            dist_null = INF

            while queue:
                u = queue.popleft()
                if dist[u] < dist_null:
                    for v in adj[u]:
                        if pair_v[v] == -1:
                            if dist_null == INF:
                                dist_null = dist[u] + 1
                        elif dist[pair_v[v]] == INF:
                            dist[pair_v[v]] = dist[u] + 1
                            queue.append(pair_v[v])
            return dist_null != INF

        def dfs(u):
            if u != -1:
                for v in adj[u]:
                    if pair_v[v] == -1 or (dist[pair_v[v]] == dist[u] + 1 and dfs(pair_v[v])):
                        pair_v[v] = u
                        pair_u[u] = v
                        return True
                dist[u] = INF
                return False
            return True

        while bfs():
            for u in range(n):
                if pair_u[u] == -1:
                    dfs(u)

        # Koning theorem

        free_rows = [i for i in range(n) if pair_u[i] == -1]
        visited_rows = set(free_rows)
        visited_cols = set()
        queue = collections.deque(free_rows)

        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if v not in visited_cols:
                    visited_cols.add(v)

                    matched_row = pair_v[v]
                    if matched_row != -1 and matched_row not in visited_rows:
                        visited_rows.add(matched_row)
                        queue.append(matched_row)
        selected_rows = [i for i in range(n) if i not in visited_rows]
        selected_cols = sorted(list(visited_cols))
        # Step 5 is not needed, becase pair_u is what we wanna find
        return {'rows': selected_rows, 'cols': selected_cols, 'count': len([x for x in pair_u if x != -1]), 'matching': pair_u}

    # Step 4
    def shift(matrix: list[list], dels: dict):
        '''
        Docstring for shift

        :param matrix: Description
        :type matrix: list[list]
        :param dels: Description
        :type dels: dict
        '''
        min_v = INF
        check = [i for i in range(n) if i not in dels['rows']]
        for row in check:
            for i in range(n):
                if i not in dels['cols']:
                    if matrix[row][i] < min_v:
                        min_v = matrix[row][i]
        if min_v == INF:
            return '\033[91mERROR in shifting, no possible shift\033[0m'
        for index, row in enumerate(matrix):
            if index in dels['rows']: # adding to crossed number
                matrix[index] = [(n + min_v if n != INF else INF) if i in dels['cols'] else n for i, n in enumerate(row)]
                continue
            matrix[index] = [n if i in dels['cols'] else (n - min_v if n != INF else INF) for i, n in enumerate(row)] # removing for all another
        return matrix

    arr2 = reduction(arr)
    lines = find_lines(arr2)
    k = 0
    while lines['count'] != n:
        k += 1
        if k == 100:
            return 'Broken'
        arr2 = shift(arr2, lines)
        lines = find_lines(arr2, prev=lines['matching'])

    result = [-1] * n
    for i, idx in enumerate(valid):
        c = lines['matching'][i]
        if arr[idx][c] == INF:
            result[idx] = -1
        else:
            result[idx] = c
    return result




if __name__ == "__main__":
    import doctest
    from time import perf_counter
    print(doctest.testmod())
    start = perf_counter()
    ma = BIGM
    if not ma:
        print('WRONG MATRIX')
        system32_termination()
    ma = convert_similarity(ma)
    ma = remove_not_accepted(ma)
    ma = square(ma)
    test = linear_sum_assignment(ma)[1]
    ma = match(ma)
    print(ma == list(test))
    end = perf_counter()
    sum1 = 0
    sum2 = 0
    original_rows = len(BIGM)

    # Calculate sum1 (for your 'match' result)
    sum1 = 0
    for i in range(original_rows): # <-- Only iterate up to original_rows
        v = ma[i] # Column index from your result
        if v == -1:
            continue
        sum1 += BIGM[i][v] # i is now guaranteed to be < 100

    # Calculate sum2 (for the 'linear_sum_assignment' result)
    sum2 = 0
    for i in range(original_rows): # <-- Only iterate up to original_rows
        v = test[i] # Column index from scipy's result
        if v == -1: # The scipy result should not have -1, but keep the check for safety
            continue
        sum2 += BIGM[i][v] # i is now guaranteed to be < 100
    print(ma)
    print(test)
    print(sum1)
    print(sum2)
    print(f"Time taken = {round(end-start, 3)}s")
