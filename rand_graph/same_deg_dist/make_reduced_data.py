#This script creates a reduced version of the data used in the python graph analysis, in order to fit with our previous matlab format

import pandas as pd

if __name__=='__main__':
    
    # load
    dat = pd.read_csv('graph_full_cons_elec.csv')
   
    # optional country filter -- don't forget to set country tag in ga_bip.m
    dat = dat[dat['code_origin'] == 'CHN']

    # seller, buyer, year, hs, val
    dat_red = dat[['EXP_ID','IMP_ID','YEAR','hs10','x_fob']]

    # make unique seller buyer pairs
    # (of course, this makes hs and value meaningless!)
    # (they remain due to imput expectations of matlab script)
    dat_red = dat_red.drop_duplicates(['EXP_ID','IMP_ID'])

    # save
    dat_red.to_csv('graph_matlab.csv', index=False, index_label=False)

