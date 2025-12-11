'''
Matching module
'''
import collections
import sys
from sys import exit as system32_termination
# import random

# INF = float('inf')
INF = 1e12

# BIGM = [[float(f'0.{n}') for n in random.choices(range(0, 100), k = 120)] for _ in range(90)]
# for i in range(120):
#     BIGM[5][i] = 0



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
        print("\033[91mDonors must be >= recipients \033[0m", file=sys.stderr)
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


def remove_not_accepted(arr: list, min_accept: int = 60) -> list:
    '''
    Removing not accepted values from cost matrix
    by setting them to INF
    60 means 60% similarity accepted
    :param arr: cost matrix
    :type arr: list
    :param min_accept: minimum accepted similarity percentage
    :type min_accept: int
    :return: cost matrix with not accepted values set to INF
    :rtype: list

    # >>> similarity = [
    # ... [0.5, 0.2, 0.7],
    # ... [0.1, 0.6, 1.0],
    # ... [0.4, 0.5, 0.9]]

    # >>> similarity = convert_similarity(similarity)
    # >>> remove_not_accepted(similarity)
    # [[1e12, 1e12, 30], [1e12, 40, 0], [1e12, 1e12, 10]]
    '''
    return [[(value if value <= 100-min_accept else INF) for value in row] for row in arr]


def match(arr: list):
    '''
    Hungarian algorithm implementation for assignment problem
    Returns list indexed by recipient rows with assigned donor column index or -1 if no assignment
    Using Hopcroft-Karp for finding maximum matching in bipartite graph
    :param arr: cost matrix
    :type arr: list
    :return: list of assigned donor indices per recipient
    :rtype: list
    '''
    # if len(arr) > len(arr[0]):
    #     pass
    n = len(arr)
    m = len(arr[0])
    original_n = n

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
    rows_to_match = len(sub_arr)
    cols = m

    n = len(arr)
    if rows_to_match < cols:
        # Add dummy rows (Recipients) to make it square
        sub_arr.extend([[0] * cols for _ in range(cols - rows_to_match)])
    n = len(sub_arr)
    arr = sub_arr
    # Step 1 & 2
    def reduction(arr_copy: list):
        '''
        Reduction step of Hungarian algorithm

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
        Finding minimum number of lines to cover all zeros in matrix
        Using Hopcroft-Karp algorithm for maximum matching
        :param matrix: Matrix to find lines in
        :type matrix: list[list]
        :param prev: Previous matching to start from
        :type prev: list
        :return: Dictionary with rows and columns to be crossed
        :rtype: dict
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
        return {'rows': selected_rows, 'cols': selected_cols, \
        'count': len([x for x in pair_u if x != -1]), 'matching': pair_u}

    # Step 4
    def shift(matrix: list[list], dels: dict):
        ''''
        Shifting step of Hungarian algorithm
        Decreases uncovered elements by minimum uncovered value
        Increases elements covered twice by minimum uncovered value

        :param matrix: Description
        :type matrix: list[list]
        :param dels: Description
        :type dels: dict
        '''
        min_v = INF
        check = [i for i in range(n) if i not in dels['rows']]
        print(matrix, file=sys.stderr)
        for row in check:
            for i in range(n):
                if i not in dels['cols']:
                    if matrix[row][i] < min_v:
                        min_v = matrix[row][i]
        if min_v == INF:
            print('\033[91mERROR in shifting, no possible shift\033[0m')
            system32_termination()
        for index, row in enumerate(matrix):
            if index in dels['rows']: # adding to crossed number
                matrix[index] = [(n + min_v if INF not in (n, min_v)else INF) if i in dels['cols']\
                                 else n for i, n in enumerate(row)]
                continue
            matrix[index] = [n if i in dels['cols'] else \
                            (n - min_v if INF not in (n, min_v) else INF) \
                            for i, n in enumerate(row)]
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

    # Return a list indexed by original recipient rows
    result = [-1] * original_n
    for i, idx in enumerate(valid):
        c = lines['matching'][i]
        if arr[i][c] == INF:
            result[idx] = -1
        else:
            result[idx] = c
    return result




if __name__ == "__main__":
    import doctest
    # from time import perf_counter
    print(doctest.testmod())
    # start = perf_counter()
    # ma = BIGM
    # if not ma:
    #     print('WRONG MATRIX')
    #     system32_termination()
    # ma = convert_similarity(ma)
    # ma = remove_not_accepted(ma)
    # ma = square(ma)
    # #test = linear_sum_assignment(ma)[1]
    # ma = match(ma)
    # #print(ma == list(test))
    # end = perf_counter()
    # sum1 = 0
    # sum2 = 0
    # original_rows = len(BIGM)

    # # Calculate sum1 (for your 'match' result)
    # sum1 = 0
    # for i in range(original_rows): # <-- Only iterate up to original_rows
    #     v = ma[i] # Column index from your result
    #     if v == -1:
    #         continue
    #     sum1 += BIGM[i][v] # i is now guaranteed to be < 100

    # Calculate sum2 (for the 'linear_sum_assignment' result)
    # sum2 = 0
    # for i in range(original_rows): # <-- Only iterate up to original_rows
    #     v = test[i] # Column index from scipy's result
    #     if v == -1: # The scipy result should not have -1, but keep the check for safety
    #         continue
    #     sum2 += BIGM[i][v] # i is now guaranteed to be < 100
    # print(ma)
    # #print(test)
    # print(sum1)
    # print(sum2)
    # print(f"Time taken = {round(end-start, 3)}s")
