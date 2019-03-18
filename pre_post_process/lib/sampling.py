import numpy as np

# Select M of N possible objects with uniform probability
# Result is an array of indices of the selected objects
def selectUniform(N, M):
    p = np.random.uniform(0, 1, N)
    select = p <= np.quantile(p, M/N)
    return np.linspace(0, N-1, N).astype(int)[select]
