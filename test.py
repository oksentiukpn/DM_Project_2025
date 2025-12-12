'''
Testing the Hungarian Algorithm implementation
'''
import numpy as np
from scipy.optimize import linear_sum_assignment
INF = float('inf')
MIN_ACCEPT = 60
# 1. Define your cost matrix (e.g., workers x tasks)
cost_matrix = [[0.1, 0.2, 0.26, 0.91, 0.51, 0.85, 0.1, 0.84, 0.25, 0.55, 0.65, 0.75, 0.55, 0.34, 0.58], [0.52, 0.57, 0.4, 0.94, 0.77, 0.54, 0.14, 0.85, 0.28, 0.13, 0.22, 0.92, 0.62, 0.4, 0.53], [0.85, 0.21, 0.22, 0.46, 0.59, 0.9, 0.43, 0.1, 0.29, 0.59, 0.59, 0.44, 0.7, 0.57, 0.69], [0.19, 0.99, 0.55, 0.9, 0.48, 0.95, 0.44, 0.89, 0.2, 0.26, 0.77, 0.9, 0.83, 0.83, 0.33], [0.1, 0.89, 0.11, 0.15, 0.51, 0.57, 0.17, 0.62, 0.23, 0.18, 0.88, 0.3, 0.19, 0.18, 0.58], [0.86, 0.17, 0.36, 0.41, 0.17, 0.6, 0.14, 0.73, 0.95, 0.51, 0.63, 0.29, 0.89, 0.7, 0.42], [0.85, 0.88, 0.11, 0.63, 0.6, 0.19, 0.88, 0.16, 0.83, 0.75, 0.99, 0.16, 0.61, 0.2, 0.2], [0.54, 0.31, 0.74, 0.71, 0.27, 0.15, 0.5, 0.33, 0.78, 0.21, 0.29, 0.48, 0.22, 0.8, 0.8], [0.55, 0.25, 0.44, 0.11, 0.63, 0.57, 0.98, 0.86, 0.27, 0.3, 0.98, 0.26, 0.13, 0.76, 0.7], [0.15, 0.29, 0.2, 0.24, 0.8, 0.33, 0.7, 0.12, 0.7, 0.18, 0.94, 0.6, 0.64, 0.37, 0.47]]
def square(matrix: list[list]) -> list:
    '''
    Pads a rectangular matrix with 0.0 to make it square.

    If Donors (rows) > Recipients (cols):
        Adds dummy columns filled with 0.0.
        Donors assigned to these columns are effectively "unmatched".
    '''
    rows = len(matrix)
    cols = len(matrix[0])

    if rows == cols:
        return matrix
    if rows < cols:
        # Add dummy columns (Recipients)
        matrix.extend([[INF for _ in range(cols)] for _ in range((rows - cols))])
    else:
        print("\033[91mDonors must be >= recipients \033[0m")
        exit()
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

m = convert_similarity(cost_matrix)
m = remove_not_accepted(m)
cost_matrix = np.array(square(m))






row_ind, col_ind = linear_sum_assignment(cost_matrix)

# Calculate the total cost using the optimal indices
total_cost = cost_matrix[row_ind, col_ind].sum()

print("Optimal assignment:")
for r, c in zip(row_ind, col_ind):
    print(f"Worker {r} -> Task {c} (Cost: {cost_matrix[r, c]})")

print(f"\nTotal Minimum Cost: {total_cost}")
