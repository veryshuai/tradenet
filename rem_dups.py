# This script removes duplicate transactions from graph_trans.csv
# and sums fob values

import pandas as pd
from scipy import stats

def error_proof_convert(x):
    try:
        arg = sum([float(k) for k in list(x)])
        return arg
    except:
        print('WARNING: Unreadable line in graph_trans.csv')
        return 0

def error_proof_hs(x):
    try:
        arg = stats.mode(x)
        return arg[0][0]
    except Exception as e:
        print(e)
        print('WARNING: Problem in hs mode finding error_proof_hs')
        return 0

def epm(x):
    try:
        first = x['index'].iat[0]
        max_ind = x['x_fob'].idxmax()
        res = x['imp_name'].iat[max_ind - first]
        return res
    except Exception as e:
        print(e)
        print('WARNING: Problem in max finding epm')
        return 'ERROR'

def main():
    dat = pd.read_csv('graph_trans.csv')
    val = dat.reset_index()\
            .groupby(['EXP_ID','IMP_ID'])['x_fob'].apply(error_proof_convert)
    hs = dat.reset_index()\
            .groupby(['EXP_ID','IMP_ID'])['hs10'].apply(error_proof_hs)
    dat['hs_source'] = dat.reset_index()\
            .groupby(['EXP_ID'])['hs10'].transform(error_proof_hs)
    dat['hs_dest'] = dat.reset_index()\
            .groupby(['IMP_ID'])['hs10'].transform(error_proof_hs)
    dat['source'] = dat.reset_index()\
           .groupby(['IMP_ID'])['code_origin'].transform(error_proof_hs)
    #dat['imp_name'] = dat.reset_index().groupby(['EXP_ID'], axis=1).apply(epm)
    #max_imp = dat.reset_index().groupby(['EXP_ID']).apply(epm)
    dat = dat.drop_duplicates(['EXP_ID','IMP_ID'])
    dat = dat.reset_index().set_index(['EXP_ID','IMP_ID'])\
            .drop('index',1).drop('Unnamed: 0', 1)
    dat['fob_x'] = val
    dat['hs10'] = hs 
    dat.reset_index().set_index('EXP_ID')
    dat.to_csv('graph.csv')
    #max_imp.to_pickle('max_imp.pickle')

main()
