import numpy as np
import h5py

data = ("Many cats".encode(), np.linspace(0, 1, 20))
data_type = [('index', 'S' + str(len(data[0]))), ('values', '<f8', (20,))]

arr = np.array(data, dtype=data_type)
print(arr)

h5f = h5py.File("lol.h5", 'w')
dset = h5f.create_dataset("data", arr, dtype=data_type)
h5f.close()
