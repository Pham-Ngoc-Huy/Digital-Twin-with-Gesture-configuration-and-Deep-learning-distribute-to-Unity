import numpy as np

x1 = np.array([1, 0, 0])
x2 = np.array([1, 1, 0])


if len(x1) != len(x2):
    raise ValueError("Vectors must have the same length.")

result = 0

for i in range(0, len(x1)):
    result +=  x1[i] * x2[i]
    print(f"i: {i}, x1[i]: {x1[i]}, x2[i]: {x2[i]}, result: {result}")
print(result)
if result != 0:
    print("Vectors are not orthogonal.")
    print("Vi: đây là 2 vector không phải tập trực giao, vì tích vô hướng của chúng khác 0.")

# projection x1 onto x2
projection = (np.dot(x2, x1) / np.dot(x1, x1)) * x1
print("Projection of x1 onto x2:", projection)         

# y_hat = x2 - projection_x2_x1

result_square = x2 - projection
print("Result of x1 - projection:", result_square)

y_hat = result_square / np.linalg.norm(result_square)

print("y_hat:", y_hat)
