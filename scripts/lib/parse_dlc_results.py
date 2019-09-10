import os
import numpy as np
# import pandas as pd
from collections import OrderedDict, defaultdict
import h5py
import cv2

from lib.os_lib import getfiles_walk, progress_bar
from lib.hdf5_wrapper import npStrArr2h5


def parse_dlc_csv(fname):
    # Read file
    with open(fname, 'r') as f:
        lines = f.readlines()

    # Parse CSV data
    nodeNames = list(OrderedDict.fromkeys(lines[1].strip().split(',')[1:]))
    data = np.array([line.strip().split(',') for line in lines[3:]]).astype(float)
    # df = pd.read_csv(dataFileName, sep=',', header=None, dtype=float, skiprows=3)
    # print("Data shape is", data.shape)
    nNodes = len(nodeNames)
    # nRows = data.shape[0]

    # Extract column positions from header
    bodyparts = np.array(lines[1].strip().split(','))
    properties = np.array(lines[2].strip().split(','))
    colX = np.zeros(nNodes, dtype=int)
    colY = np.zeros(nNodes, dtype=int)
    colP = np.zeros(nNodes, dtype=int)
    for i in range(nNodes):
        thiscols = bodyparts == nodeNames[i]
        colX[i] = np.where(np.logical_and(thiscols, properties == 'x'))[0]
        colY[i] = np.where(np.logical_and(thiscols, properties == 'y'))[0]
        colP[i] = np.where(np.logical_and(thiscols, properties == 'likelihood'))[0]
        
    return nodeNames, data[:, colX], data[:, colY], data[:, colP]


# Get fps of the video
def parse_avi_meta(vidname):
    capture = cv2.VideoCapture(vidname)
    fps = capture.get(cv2.CAP_PROP_FPS)
    capture.release()
    return fps


'''
1. Crawl from root, find all directories containing ['DeepCut_resnet50', '.csv']
2. For each directory, compress all files into one sub file with same name as directory
'''
def dlc_csv_composite_crawl(rootdir, outdir):
    
    # Construct dictionary of files indexed by the containing folder name
    # Files must appear in alphabetical order
    def paths2dict(walkpaths):            
        path_dict = defaultdict(list)
        for path, name in walkpaths:
            path_dict[os.path.basename(path)] += [os.path.join(path, name)]
        return {k : np.sort(v) for k,v in path_dict.items()}
    
    print("Finding paths to CSV and AVI files")
    walkpaths_csv = getfiles_walk(rootdir, ['DeepCut_resnet50', '.csv'])
    walkpaths_avi = getfiles_walk(rootdir, ['.avi'])
    
    path_dict_csv = paths2dict(walkpaths_csv)
    path_dict_avi = paths2dict(walkpaths_avi)
        
    # For each folder, create an output file that merges files inside
    N_FOLDERS = len(path_dict_csv)
    for i, (basename, csv_path_list) in enumerate(path_dict_csv.items()):
        print("Processing folder", i, "/", N_FOLDERS, "; Have", len(csv_path_list), "files")
        outpathname = os.path.join(outdir, basename+'.h5')
        assert basename in path_dict_avi.keys(), basename + " has .csv but no videos"        
        
        if os.path.isfile(outpathname):
            print("Skipping existing output file", outpathname)
        else:
            dlc_csv_merge_write(csv_path_list, path_dict_avi[basename], outpathname)

        
'''
1. Read all files
  1.1 Number of AVI and CSV files must match
  1.2 All nodeNames must match
  1.3 All framerates must match
2. Determine longest nTime, make outArray [nTimesMax, nNodes, nTrials] of np.nan
3. Fill array with data
4. Save to H5
'''
def dlc_csv_merge_write(csv_list, vid_list, outpathname):
    # Check if all elements of a list are the same
    def check_equal(lst, err=""):
        for el in lst[1:]:
            if el != lst[0]:
                raise ValueError(err, lst[0], "!=", el)
    
    # Check that the number of videos and CSV files is the same
    if len(csv_list) != len(vid_list):
        raise ValueError("There are", len(vid_list), "videos and", len(fpath), " csv files")
        
    # Check that the videos and CSV files correspond
    for csv_name, vid_name in zip(csv_list, vid_list):
        if os.path.basename(vid_name)[:-4] not in csv_name:
            raise ValueError("CSV and VIDEO files do not correspond", csv_name, vid_name)
    
    N_FILES = len(csv_list)
    csv_data_list = []
    progress_bar(0, N_FILES, "parsing CSV Files")
    for i, csv_name in enumerate(csv_list):
        csv_data_list += [parse_dlc_csv(csv_name)]
        progress_bar(i+1, N_FILES, "parsing CSV Files")
    
    avi_fps_list = []
    progress_bar(0, N_FILES, "getting FPS info")
    for i, vid_name in enumerate(vid_list):
        avi_fps_list += [parse_avi_meta(vid_name)]
        progress_bar(i+1, N_FILES, "getting FPS info")
        
    print("-- computing merged file")
    # Assert that all framerates are the same
    # Assert that all nodeNames match exactly
    check_equal(avi_fps_list, err="Found non-matching framerates")
    check_equal([data[0] for data in csv_data_list], err="Found non-matching keys")
    
    # Determine nNodes, nTrials, and longest nTime
    nNodes   = len(csv_data_list[0][0])
    nTrials  = len(csv_data_list)
    nTimesMax = np.max([data[1].shape[0] for data in csv_data_list])

    # Make output array
    outdata_X = np.full((nTimesMax, nNodes, nTrials), np.nan)
    outdata_Y = np.full((nTimesMax, nNodes, nTrials), np.nan)
    outdata_P = np.full((nTimesMax, nNodes, nTrials), np.nan)
    
    # Fill output array
    for i, (nodeNames, X, Y, P) in enumerate(csv_data_list):
        nTimesThis = X.shape[0]
        outdata_X[:nTimesThis, :, i] = X
        outdata_Y[:nTimesThis, :, i] = Y
        outdata_P[:nTimesThis, :, i] = P
    
    # Write result to file
    print("-- writing merged data of", nTrials, "videos to", outpathname)
    rezfile = h5py.File(outpathname, "w")
    
    vidNames = [os.path.basename(vidpathname) for vidpathname in vid_list]
    rezfile.attrs['VID_PATH'] = np.string_(os.path.dirname(vidNames[0]))
    npStrArr2h5(rezfile, csv_data_list[0][0], 'NODE_NAMES')
    npStrArr2h5(rezfile, vidNames, 'VID_NAMES')
    #npStrArr2h5(rezfile, csv_list, 'CSV_PATHS')
    rezfile['FPS'] = avi_fps_list[0]
    rezfile['X'] = outdata_X
    rezfile['Y'] = outdata_Y
    rezfile['P'] = outdata_P
    rezfile.close()
