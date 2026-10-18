diag_matrix = [[0 for _ in range(3)] for _ in range(3)]
for r in range(0,3):
    for c in range(0,3):
        if r == c:
            diag_matrix[r][c] = 1
        else:
            diag_matrix[r][c] = 0
print(diag_matrix)