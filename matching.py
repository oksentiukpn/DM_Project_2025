'''
Matching module
'''
from copy import deepcopy
import collections
MIN_ACCEPT = 0.6
INF = float('inf')

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
    [[inf, inf, 0.3], [inf, 0.4, 0.0], [inf, inf, 0.1]]
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
    [2, 0, 1]
    >>> matrix_30 = [
    ... [ 50, 40, 30, 20, 10,  0,  8,  9, 11, 12, 60, 55, 52, 49, 47, 150,140,130,120,110, 5, 4, 3, 2, 1, 200,199,198,197,196 ],
    ... [  0, 45, 44, 43, 42, 41, 40,  1,  2,  3, 70, 65, 63, 61, 60, 145,135,125,115,105, 9, 8, 7, 6, 5, 210,205,203,202,201 ],
    ... [ 55,  0, 48, 47, 46, 45, 44, 40,  3,  4, 75, 72, 70, 68, 65, 155,150,145,140,135, 7, 6, 5, 4, 3, 215,213,211,209,207 ],
    ... [ 52, 51,  0, 49, 48, 47, 46, 45, 40,  5, 77, 76, 75, 73, 70, 160,155,150,145,140, 4, 3, 2, 1, 0, 220,218,217,216,210 ],
    ... [ 60, 59, 58,  0, 49, 48, 47, 46, 45, 40, 80, 79, 78, 76, 75, 165,160,155,150,145, 3, 2, 1, 0, 9, 225,224,223,222,221 ],
    ... [ 70, 69, 68, 67,  0, 49, 48, 47, 46, 45, 85, 84, 83, 81, 80, 170,165,160,155,150, 2, 1, 0, 9, 8, 230,229,228,227,226 ],
    ... [ 80, 70, 60, 55, 50,  0, 49, 48, 47, 46, 90, 89, 88, 87, 86, 175,170,165,160,155, 1, 0, 9, 8, 7, 235,234,233,232,231 ],
    ... [ 90, 85, 78, 71, 63, 55,  0, 48, 47, 46, 95, 93, 91, 88, 87, 180,175,170,165,160, 0, 9, 8, 7, 6, 240,239,238,237,236 ],
    ... [ 95, 90, 85, 80, 70, 60, 50,  0, 47, 46,100, 97, 95, 92, 89, 185,180,175,170,165, 9, 8, 7, 6, 5, 245,244,243,242,241 ],
    ... [100, 95, 90, 85, 80, 70, 60, 50,  0, 46,105,102,100, 97, 94, 190,185,180,175,170, 8, 7, 6, 5, 4, 250,249,248,247,246 ],
    ... [ 60, 58, 56, 54, 53, 52, 51, 50, 49, 48,  0, 40, 35, 32, 30, 95, 90, 85, 80, 75, 7, 6, 5, 4, 3, 120,119,118,117,116 ],
    ... [ 62, 60, 58, 56, 55, 54, 53, 52, 51, 50, 40,  0, 33, 31, 30, 98, 95, 90, 85, 80, 6, 5, 4, 3, 2, 121,120,119,118,117 ],
    ... [ 64, 62, 60, 58, 57, 56, 55, 54, 53, 52, 35, 33,  0, 31, 30,100, 97, 95, 90, 85, 5, 4, 3, 2, 1, 122,121,120,119,118 ],
    ... [ 66, 64, 62, 60, 59, 58, 57, 56, 55, 54, 32, 31, 31,  0, 30,102,100, 97, 95, 90, 4, 3, 2, 1, 0, 123,122,121,120,119 ],
    ... [ 68, 66, 64, 62, 61, 60, 59, 58, 56, 55, 30, 30, 30, 30,  0,105,102,100, 97, 95, 3, 2, 1, 0, 9, 124,123,122,121,120 ],
    ... [150,140,130,120,110,100, 95, 90, 85, 80, 75, 70, 65, 60, 55,  0, 40, 30, 20, 10, 9, 8, 7, 6, 5, 60, 59, 58, 57, 56 ],
    ... [145,135,125,115,105, 95, 92, 88, 83, 78, 72, 68, 63, 58, 53, 40,  0, 35, 25, 15, 8, 7, 6, 5, 4, 55, 54, 53, 52, 51 ],
    ... [140,130,120,110,100, 90, 87, 84, 79, 74, 68, 63, 60, 55, 50, 30, 35,  0, 27, 18, 7, 6, 5, 4, 3, 50, 49, 48, 47, 46 ],
    ... [135,125,115,105, 95, 85, 82, 79, 75, 71, 63, 60, 57, 53, 49, 20, 25, 27,  0, 22, 6, 5, 4, 3, 2, 45, 44, 43, 42, 41 ],
    ... [130,120,110,100, 90, 80, 78, 75, 72, 70, 60, 57, 55, 52, 48, 10, 15, 18, 22,  0, 5, 4, 3, 2, 1, 40, 39, 38, 37, 36 ],
    ... [  9,  8,  7,  6,  5,  4,  3,  2,  1,  0, 8, 7, 6, 5, 4, 9, 8, 7, 6, 5,  0, 40, 35, 30, 25, 100, 99, 98, 97, 96 ],
    ... [  8,  7,  6,  5,  4,  3,  2,  1,  0,  9, 7, 6, 5, 4, 3, 8, 7, 6, 5, 4, 40,  0, 34, 29, 24, 99, 98, 97, 96, 95 ],
    ... [  7,  6,  5,  4,  3,  2,  1,  0,  9,  8, 6, 5, 4, 3, 2, 7, 6, 5, 4, 3, 35, 34,  0, 28, 23, 98, 97, 96, 95, 94 ],
    ... [  6,  5,  4,  3,  2,  1,  0,  9,  8,  7, 5, 4, 3, 2, 1, 6, 5, 4, 3, 2, 30, 29, 28,  0, 22, 97, 96, 95, 94, 93 ],
    ... [  5,  4,  3,  2,  1,  0,  9,  8,  7,  6, 4, 3, 2, 1, 0, 5, 4, 3, 2, 1, 25, 24, 23, 22,  0, 96, 95, 94, 93, 92 ],
    ... [200,190,180,170,160,150,140,130,120,110,100, 95, 90, 85, 80, 75, 55, 45, 35, 25,100, 99, 98, 97, 96,  0,  1,  2,  3,  4 ],
    ... [195,185,175,165,155,145,135,125,115,105, 95, 92, 88, 83, 78, 72, 50, 44, 36, 27, 99, 98, 97, 96, 95,  1,  0,  3,  4,  5 ],
    ... [190,180,170,160,150,140,130,120,110,100, 90, 85, 81, 78, 75, 70, 48, 40, 33, 23, 98, 97, 96, 95, 94,  2,  3,  0,  5,  6 ],
    ... [185,175,165,155,145,135,125,115,105, 95, 85, 80, 75, 70, 65, 60, 45, 38, 30, 20, 97, 96, 95, 94, 93,  3,  4,  5,  0,  7 ],
    ... [180,170,160,150,140,130,120,110,100, 90, 80, 75, 70, 65, 60, 55, 40, 35, 28, 18, 96, 95, 94, 93, 92,  4,  5,  6,  7,  0 ]]

    >>> match(matrix_30)
    [5, 0, 1, 2, 3, 4, 20, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 9, 21, 22, 23, 24, 25, 26, 27, 28, 29]
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
    def find_lines(matrix: list[list]):
        '''
        Func
        '''
        # Building graph
        adj = [[] for _ in range(n)]
        for i in range(n):
            for k in range(n):
                if not matrix[i][k]:
                    adj[i].append(k)

        # Hopcroft algorithm

        pair_u = [-1] * n
        pair_v = [-1] * n
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

        # Kening theorem

        free_rows = [i for i in range(n) if pair_u[i] == -1]
        visited_rows = set()
        visited_cols = set()
        queue = collections.deque(free_rows)
        for row in free_rows:
            visited_rows.add(row)

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
        count = len(selected_rows) + len(selected_cols)
        return {'rows': selected_rows, 'cols': selected_cols, 'count': count}
    arr2 = reduction(arr_copy)
    lines = find_lines(deepcopy(arr2))

    # Step 4
    def shift(matrix: list[list], dels: dict):
        '''
        Docstring for shift

        :param matrix: Description
        :type matrix: list[list]
        :param dels: Description
        :type dels: dict
        '''
        # finding min for all matrix
        min_v = min(v for i, row in enumerate(matrix) for j, v in enumerate(row) if i not in dels['rows'] and j not in dels['cols'])
        for index, row in enumerate(matrix):
            if index in dels['rows']: # adding to crossed number
                matrix[index] = [round(n + min_v, 3) if i in dels['cols'] else n for i, n in enumerate(row)]
                continue
            matrix[index] = [n if i in dels['cols'] else round(n - min_v, 3) for i, n in enumerate(row)] # removing for all another
        return matrix
    k = 0
    while lines['count'] != n:
        k += 1
        if k == 1000:
            print(lines)
            return -1
        arr2 = shift(arr2, lines)
        lines = find_lines(deepcopy(arr2))

    # Step 5!
    def choose_zeros(matrix: list[list]):
        '''
        Docstring for choose_zeros

        :param matrix: Description
        '''
        used_cols = [False for _ in range(n)]
        result = [-1] * n

        def recurse(row):
            # if all rows proccesed => we found
            if row == n:
                return True
            for col in range(n):
                if matrix[row][col] == 0 and not used_cols[col]:
                    # choosing zeros
                    used_cols[col] = True
                    result[row] = col

                    if recurse(row + 1): # look in next row
                        return True
                    # if we can't asign we roll back
                    used_cols[col] = False
                    result[row] = -1
            return False
        # 0 because we start from first row
        if recurse(0):
            return result
        # if we did not find, it must not happen, for bug finding
        return 'NOT FOUND'

    return choose_zeros(arr2)



if __name__ == "__main__":
    import doctest
    print(doctest.testmod())
