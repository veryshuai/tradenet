# This script generates a random graph which does not respect the datas degree distribution.  All it is going to do in practice is shuffle the list.

import pandas as pd
import numpy as np
import random as rand

def load_dat(years):
    dat                                  = pd.read_csv('graph.csv')
    dat_by_yr                            = []
    for yr in years:
        dat_by_yr.append(dat[dat['YEAR'] == yr])
    return dat_by_yr

def count_vals(dat_by_yr):
    buyers  = [] 
    sellers = []
    for k in range(len(dat_by_yr)):
        temp_df = dat_by_yr[k]
        buyers.append(len(set(list(temp_df['IMP_ID']))))
        sellers.append(len(set(list(temp_df['EXP_ID']))))
    return buyers, sellers

def main(years):
    dat_by_yr                            = load_dat(years)
    buyers, sellers                      = count_vals(dat_by_yr)
    inc                                  = 0
    for k in range(len(dat_by_yr)):
        dat_temp                         = dat_by_yr[k]
        dat_by_yr[k]['RAND_IMP_ID']      = dat_by_yr[k]['IMP_ID'].apply(lambda x: rand.randrange(buyers[k]))
        dat_by_yr[k]['RAND_EXP_ID']      = dat_by_yr[k]['EXP_ID'].apply(lambda x: rand.randrange(sellers[k]))
    new_dat                              = pd.concat(dat_by_yr)
    new_dat                              = new_dat[['RAND_EXP_ID','RAND_IMP_ID','YEAR','POS_ARA3','FOB_DOL3']].set_index('RAND_EXP_ID')
    new_dat.to_csv('graph_tot_rand.csv')

years = range(2007,2010)
main(years)


