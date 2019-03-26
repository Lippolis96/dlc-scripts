'''
  The purpose of this code is to adjust all paths in the training dataset
'''

import numpy as np
import os, sys
import yaml
import pathlib
import h5py
import pandas as pd
import copy

pwd_project = sys.argv[1]

pwd_config_file = os.path.join(pwd_project, 'config.yaml')

if not os.path.isfile(pwd_config_file):
  raise ValueError('Config file not found at:', pwd_config_file)

pwd_project     = os.path.abspath(pwd_project)
pwd_config_file = os.path.abspath(pwd_config_file)

#print("Absolute path to project is: ", pwd_project)
print("Absolute path to project file is: ", pwd_config_file)

##################################
#  Editing config.yaml file
##################################
print('Editing config.yaml file')
with open(pwd_config_file, "r") as fconf:
  data_conf = yaml.load(fconf)

# Fix project path
project_path_old = data_conf['project_path']
data_conf['project_path'] = pwd_project
#print('Old path:', project_path_old)

# Fix all paths to videos
video_sets_old = data_conf.pop('video_sets')
data_conf['video_sets'] = {}
for k,v in video_sets_old.items():
  k_new = k.replace(project_path_old, data_conf['project_path']).replace('\\','/')
  data_conf['video_sets'][k_new] = v

# Save changes
with open(pwd_config_file, 'w') as fconf_new:
  yaml.dump(data_conf, fconf_new, default_flow_style=False)

##################################
#  Editing csv paths
##################################
print('Editing paths in .csv marking files')
pwd_labeled = os.path.join(pwd_project, 'labeled-data')
for dirpath, dirnames, filenames in os.walk(pwd_labeled):
    for filename in [f for f in filenames if f.endswith(".csv")]:
        csv_fname = os.path.join(dirpath, filename)
        print("Fixing file", csv_fname)

        with open(csv_fname, 'r') as csvfile:
            data_csv = csvfile.readlines()
            
        data_csv = [line.strip().split(',') for line in data_csv]
        data_csv = [[line[0].replace('\\', '/')] + line[1:] for line in data_csv]
            
        with open(csv_fname, 'w') as csvfile:
            for line in data_csv:
                csvfile.write(",".join(line) + '\n')

##################################
#  Marking h5 paths
##################################
print('Editing paths in .h5 marking files')
pwd_labeled = os.path.join(pwd_project, 'labeled-data')
for dirpath, dirnames, filenames in os.walk(pwd_labeled):
    for filename in [f for f in filenames if f.endswith(".h5")]:
        h5_fname = os.path.join(dirpath, filename)
        print("Fixing file", h5_fname)
        
        h5_df = pd.read_hdf(h5_fname, 'df_with_missing')

        # Rename all indices
        h5_df.index = pd.Index([idx.replace('\\', '/') for idx in h5_df.index])
        
        print(h5_df.index)
        
        
        #print(h5_df.keys())
        #for key in h5_df.keys():
            #for keyname in list(h5_df[key].keys()):
                #newkeyname = keyname.replace('\\', '/')
                
                ## Add transformed keys
                #h5_df[key][newkeyname] = h5_df[key][keyname]
                
                ## Delete old keys
                #del h5_df[key][keyname]
            
        #for key in h5_df.keys():
            #print(h5_df[key])
        
        # Save edited dataframe back
        h5_df.to_hdf(h5_fname, 'df_with_missing', format='table', mode='w')
            

            
            #print(h5_df[key].keys())
            #for key2 in h5_df[key].keys():
                #print(key2)
        #print(h5_df.values())
        
        #h5_df.to_hdf(h5_fname, 'df_with_missing', format='table', mode='w')
        
        #h5f = h5py.File(h5_fname, 'r+')
        #sub = h5f['df_with_missing']
        #table = sub['table'][...]
        ##del h5f['df_with_missing/table']
        
        #for i in range(len(table)):
            #table[i][0] = table[i][0].decode('UTF-8').replace('\\', '/').encode()
            #print(table[i][0])
        
        #sub['table'][...] = table
        #h5f.close()

        
