import h5py

# Write an array of strings to HDF5
def npStrArr2h5(h5file, arr, key):
    keyGroup = h5file.create_dataset(key, (len(arr),), dtype=h5py.special_dtype(vlen=str))
    for i in range(nNodes):
        keyGroup[i] = arr[i] #keyGroup[i]