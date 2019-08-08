import os, sys
import numpy as np

# Print progress bar with percentage
def progress_bar(i, imax):
    sys.stdout.write('\r')
    sys.stdout.write('[{:3d}%] '.format(i * 100 // imax))
    sys.stdout.flush()

# Get path relative to a higher level path
# NOTE: ONLY WORKS WITH FOLDER PATHS, NOT FILE PATHS
def get_relpath(path, root):
    relpath = os.path.relpath(path, root)
    return relpath if relpath != "." else ""

# Find all folders in this folder (excluding subdirectories)
def get_subfolders(folderpath):
    return [_dir for _dir in os.listdir(folderpath) if os.path.isdir(os.path.join(folderpath, _dir))]

# Find all files in a given directory including subdirectories
# All keys must appear in file name
def getfiles_walk(inputpath, keys):
    rez = []
    NKEYS = len(keys)
    for dirpath, dirnames, filenames in os.walk(inputpath):
        for filename in filenames:
            if np.sum(np.array([key in filename for key in keys], dtype=int)) == NKEYS:
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
def move_filepaths(fpaths_walk, src_path, trg_path, skip_exist=False):
    source_fpaths = []
    moved_fpaths = []
    for src_subpath, src_subname in fpaths_walk:
        src_relsubpath = get_relpath(src_subpath, src_path)
        trg_subpath = os.path.join(trg_path, src_relsubpath)
        trg_subfpath = os.path.join(trg_subpath, src_subname)
        if skip_exist and os.path.isfile(trg_subfpath):
            print("-- skipping existing file", trg_subfpath)
        else:
            source_fpaths += [os.path.join(src_subpath, src_subname)]
            moved_fpaths += [trg_subfpath]
    return source_fpaths, moved_fpaths
