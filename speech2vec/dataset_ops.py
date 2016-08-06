import argparse
from glob import glob
import os
import pdb

import h5py
import numpy as np
from tqdm import tqdm

DATA_ROOT = './data/'
DEV_CLEAN = 'dev-clean/'
TEST_CLEAN = 'test-clean/'
FBANK = 'fbank/'
FBANK_DELTA = 'fbank_delta/'
DATA_NAME = 'data.h5'

CSV_EXT = ".csv"

def load_digits(path='./data/dsp_hw2_one_digit/dsp_hw2_one_digit.h5'):
    f = h5py.File(path,'r')
    fbank = f['fbank'][:]
    fbank_delta = f['fbank_delta'][:]
    labels = f['labels'][:]
    return fbank, fbank_delta, labels

def load_dataset(path, num = None):
    # dataset: train | dev | test
    h5path = path + DATA_NAME
    f = h5py.File(h5path,'r')
    if not num:
        return f['fbank'][:]
    else:
        return f['fbank'][:num]

def create_dataset(path, ext = CSV_EXT):
    """
        Stores as array of objects( different size arrays )
    """
    print "Creating dataset at {0}...".format(path)
    print "Loading samples..."
    fbank = []
    num_of_samples = len(glob(path+"*.csv"))
    for i in tqdm(range(1,num_of_samples+1,1)):
        filename = path + str(i) + ext
        arr = np.loadtxt(filename,delimiter=',',dtype='float32')
        fbank.append(arr)

    # Get Maxmimum Timestep
    print "Getting maximum timestep..."
    max_timestep = 0
    for i in tqdm(range(len(fbank))):
        if fbank[i].shape[0] > max_timestep:
            max_timestep = fbank[i].shape[0]

    # Pad Zeros & Stack
    print "Padding zeros"
    for i in tqdm(range(len(fbank))):
        ts, _ = fbank[i].shape
        fbank[i] = np.pad(fbank[i],((0,max_timestep-ts),(0,0)),'constant',constant_values=0.)

    print "Stacking and rolling axis..."
    fbank = np.dstack(fbank)
    fbank = np.rollaxis(fbank,2,0)
    return fbank
    # Stack and save
    h5name = 'data.h5'
    print "Saving to {0}...".format(path+h5name)
    f = h5py.File(path+h5name,'w')
    f.create_dataset('fbank',data=fbank)
    f.close()
    print 'Done'
    print

# For matlab conversion
def save_to_csv(fbank,dir_name):
    assert dir_name.endswith("/")
    # Fbank is a numpy array
    try:
        os.makedirs(dir_name)
    except OSError:
        if not os.path.isdir(dir_name):
            raise

    for idx,arr in tqdm(enumerate(fbank)):
        fname = dir_name + str(idx+1) + ".csv"
        mask = np.all(np.isnan(arr) | np.equal(arr, 0), axis=1)
        arr = arr[~mask]
        np.savetxt(fname,arr,delimiter=",")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-a',dest='action',help='create')
    parser.add_argument('-p',dest='path',help='path to dataset(dev|test)')
    args =  parser.parse_args()
    action = args.action
    path = args.path
    if action and path:
        if action == "create":
            create_dataset(path)
        else:
            raise Exception("No such action {0}".format(action))
