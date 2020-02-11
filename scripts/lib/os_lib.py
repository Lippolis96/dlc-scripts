import os, sys
import numpy as np
import bisect

# Print progress bar with percentage
def progress_bar(i, imax, suffix=None):
    sys.stdout.write('\r')
    sys.stdout.write('[{:3d}%] '.format(i * 100 // imax))
    if suffix is not None:
        sys.stdout.write(suffix)
    if i == imax:
        sys.stdout.write("\n")
    sys.stdout.flush()

def sizeToString(sizeBytes):
    ranges = [1, 10**3, 10**6, 10**9, 10**12]
    suffix = ['B', 'Kb', 'Mb', 'Gb', 'Tb']
    idxThis = np.max([bisect.bisect_left(ranges, sizeBytes), 1])-1
    return str(np.round(sizeBytes / ranges[idxThis],3)) + " " + suffix[idxThis]


# Get path relative to a higher level path
# NOTE: ONLY WORKS WITH FOLDER PATHS, NOT FILE PATHS
def get_relpath(path, root):
    relpath = os.path.relpath(path, root)
    return relpath if relpath != "." else ""


# Find all folders in this folder (excluding subdirectories)
def get_subfolders(path):
    return [_dir for _dir in os.listdir(path) if os.path.isdir(os.path.join(path, _dir))]


# Get all files of a given extension in this folder (excluding subfolders)
def get_files(path, ext):
    return [fname for fname in os.listdir(path) if os.path.splitext(fname)[1] == ext]


# Find all files in a given directory including subdirectories
# All keys must appear in file name
def getfiles_walk(inputpath, keys=None, min_size=None, max_size=None):
    rez = []
    for dirpath, dirnames, filenames in os.walk(inputpath):
        for filename in filenames:
            filterTestsPass = [
                (keys is None) or np.all([key in filename for key in keys]),
                (min_size is None) or (os.path.getsize(os.path.join(dirpath, filename)) > min_size),
                (max_size is None) or (os.path.getsize(os.path.join(dirpath, filename)) < max_size)
            ]

            if np.all(filterTestsPass):
                rez += [(dirpath, filename)]
    return np.array(rez)


# Creates exact copy of source folder structure at target location (only folders, no files)
def copy_folder_structure(source_path, target_path):
    for dirpath, dirnames, filenames in os.walk(source_path):
        # Get current relative path
        source_dirpath_rel = get_relpath(dirpath, source_path)

        # Make a new folder
        target_dirpath = os.path.join(target_path, source_dirpath_rel)

        if not os.path.isdir(target_dirpath):
            print("Making directory:", target_dirpath)
            os.mkdir(target_dirpath)
        else:
            print("Skipping existing directory", target_dirpath)

            
# Converts file paths with respect to new root directory
def move_filepaths(fpaths_walk, src_path, trg_path):
    source_fpaths = []
    moved_fpaths = []
    for src_subpath, src_subname in fpaths_walk:
        src_relsubpath = get_relpath(src_subpath, src_path)
        trg_subpath = os.path.join(trg_path, src_relsubpath)
        trg_subfpath = os.path.join(trg_subpath, src_subname)
        source_fpaths += [os.path.join(src_subpath, src_subname)]
        moved_fpaths += [trg_subfpath]
    return source_fpaths, moved_fpaths
