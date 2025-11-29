'''
Matching module
'''

MIN_ACCEPT = 0.6


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
    ... [0.4, 0.5, 0.3]]

    >>> convert_similarity(similarity)
    [[0.5, 0.8, 0.3], [0.9, 0.4, 0.0], [0.6, 0.5, 0.7]]
    '''

    return [[round(1-value, 1) for value in row] for row in arr]


if __name__ == "__main__":
    import doctest
    print(doctest.testmod())
