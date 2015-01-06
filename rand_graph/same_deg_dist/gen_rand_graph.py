# This script generates a random graph which respects the datas degree distribution.  All it is going to do in practice is shuffle the list.

import pandas as pd
import numpy as np

def load_dat(start,end):
    dat = pd.read_csv('graph_matlab.csv')
    dat_by_yr = []
    for yr in range(start,end+1):
        dat_by_yr.append(dat[dat['YEAR'] == yr])
    return dat_by_yr

def main(start,end):
    dat_by_yr   = load_dat(start,end)
    inc         = 0
    for k in range(len(dat_by_yr)):
        dat_temp                    = dat_by_yr[k]
        dat_by_yr[k]['SHUF_IMP_ID'] = np.random.permutation(dat_temp['IMP_ID'])
        print dat_by_yr[k]
    new_dat = pd.concat(dat_by_yr)
    new_dat = new_dat[['EXP_ID','SHUF_IMP_ID','YEAR','POS_ARA3','FOB_DOL3']].set_index('EXP_ID')
    new_dat.to_csv('graph_shuffled.csv')

start = 2009
end   = 2009
main(start,end)


