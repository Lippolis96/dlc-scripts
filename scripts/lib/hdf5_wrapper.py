import h5py

# Write an array of strings to HDF5
def npStrArr2h5(h5file, arr, key):
    nElem = len(arr)
    keyGroup = h5file.create_dataset(key, (nElem,), dtype=h5py.special_dtype(vlen=str))
    for i in range(nElem):
        keyGroup[i] = arr[i] #keyGroup[i]