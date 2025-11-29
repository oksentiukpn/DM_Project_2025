'''
Matching module
'''

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


if __name__ == "__main__":
    import doctest
    print(doctest.testmod())
