# This program calculates statistics for NSF networks proposal

import pandas as pd
import numpy as np

def collapse(who, dat, val=False):
    """ collapses data by year, and adds zeros for 
    missing years"""

    collapse = dat.groupby([who, 'YEAR']).size().unstack()\
        .fillna(0).stack()

    if val == True:
        collapse = dat.groupby([who, 'YEAR']).size().unstack()\
            .fillna(0).stack()

    return collapse

def count_trans(clp, who):
    """takes collapsed data and calculates client transitions"""

    # FIRST SHIFT DATA
    shift = pd.DataFrame(clp).reset_index().groupby(who).shift(-1)

    # NEXT READ IN ORIGINAL DATA
    shift['first'] = pd.DataFrame(clp).reset_index()[0]

    # REMOVE NaNs   
    no_nons = shift[pd.notnull(shift['YEAR'])]

    # COUNT TRANS AND MAKE MATRIX
    tmat = no_nons.groupby(['first',0])['YEAR'].count().unstack().fillna(0)
    
    # REDUCED TRANS MATRIX
    tred = pd.DataFrame([tmat.iloc[1,:], tmat.iloc[2,:], tmat.iloc[3:4,:].sum(axis=0),
                         tmat.iloc[5:9,:].sum(axis=0), tmat.iloc[10:,:].sum(axis=0)],
                         index=['1','2','3-4','5-9','10+']).T
    tred = pd.DataFrame([tred.iloc[0,:], tred.iloc[1,:], tred.iloc[2,:], 
                         tred.iloc[3:4,:].sum(axis=0), tred.iloc[5:9,:].sum(axis=0), 
                         tred.iloc[10:,:].sum(axis=0)], 
                         index=['0','1','2','3-4','5-9','10+'],
                         columns=['1','2','3-4','5-9','10+']).T

    # DESTRUCTION AND FORMATION COUNTS BY TYPE 
    dest_counts = [tred.iloc[0,0], tred.iloc[1,0:1].sum(),
                   tred.iloc[2,0:2].sum(), tred.iloc[3,0:3].sum(),
                   tred.iloc[4,0:4].sum()]
    form_counts = [tred.iloc[0,2:5].sum(), tred.iloc[1,3:5].sum(),
                   tred.iloc[2,4:5].sum(), tred.iloc[3,5].sum(),
                   np.nan]
    stay_counts = [tred.iloc[0,1], tred.iloc[1,2], tred.iloc[2,3],
                   tred.iloc[3,4], tred.iloc[4,5]]

    # DESTRUCTION AND FORMATION RATES
    formrate = pd.DataFrame([dest_counts, stay_counts, form_counts],
                            index=['shrink','stay','grow'],
                            columns=['1','2','3-4','5-9','10+']).T
    formrate = formrate.div(formrate.sum(axis=1), axis=0)
    
    return tmat, no_nons, formrate

def gen_hist(clp, who):
    """generates client count histogram for the year 2007"""

    # CHANGE INTO DATAFRAME
    clp = pd.DataFrame(clp).reset_index()

    # ONLY 2007
    clp_2007 = clp[clp['YEAR'] == 2007]

    # COUNT CLIENT NUMBERS
    hist = clp_2007.groupby(0)[who].count()

    return hist

def mdp_calc(dat):
    """ calculates match death probaiblities"""

    # GET POSSIBLE YEARS TO SURVIVE 
    psy = dat.groupby(['EXP_ID', 'IMP_ID'])['YEAR']\
            .apply(lambda x: min(x.max() + 1, 2012) - x.min())

    # GET ACTUAL SURVIVE YEARS
    asy = dat.groupby(['EXP_ID', 'IMP_ID'])['YEAR']\
            .apply(lambda x: x.max() - x.min())

    return 1 - asy.sum() / float(psy.sum())

def sz(dat):
    """calculates size specific histograms for exporters"""

    # FOCUS ON 2007
    dat = dat[dat['YEAR'] == 2007]

    # GET IMPORTER SIZE AND EXPORTER SIZE
    dat['IMP_SZ'] = dat.groupby('IMP_ID')['EXP_ID']\
            .transform(lambda x: min(len(x),10))
    dat['EXP_SZ'] = dat.groupby('EXP_ID')['IMP_ID']\
            .transform(lambda x: min(len(x),10))

    # IMPORTER DIST BY EXPORTER SIZE
    hist = dat.groupby('EXP_SZ')['IMP_SZ'].value_counts(normalize=False).unstack()

    # make it nice to read by aggregating
    hred = pd.DataFrame([hist.iloc[0,:], hist.iloc[1,:], hist.iloc[2:3,:].sum(axis=0),
                         hist.iloc[4:8,:].sum(axis=0), hist.iloc[9:,:].sum(axis=0)],
                         index=['1','2','3-4','5-9','10+']).T
    hred = pd.DataFrame([hred.iloc[0,:], hred.iloc[1,:], hred.iloc[2:3,:].sum(axis=0), 
                         hred.iloc[4:8,:].sum(axis=0), hred.iloc[9:,:].sum(axis=0)], 
                         index=['1','2','3-4','5-9','10+'],
                         columns=['1','2','3-4','5-9','10+']).T

    # normalize
    hred_imp_dist_by_exp_sz = hred.div(hred.sum(axis=1).astype(float), axis=0)

    # EXPORTER DIST BY IMPORTER SIZE
    hist = dat.groupby('IMP_SZ')['EXP_SZ'].value_counts(normalize=False).unstack()

    # make it nice to read by aggregating
    hred = pd.DataFrame([hist.iloc[0,:], hist.iloc[1,:], hist.iloc[2:3,:].sum(axis=0),
                         hist.iloc[4:8,:].sum(axis=0), hist.iloc[9:,:].sum(axis=0)],
                         index=['1','2','3-4','5-9','10+']).T
    hred = pd.DataFrame([hred.iloc[0,:], hred.iloc[1,:], hred.iloc[2:3,:].sum(axis=0), 
                         hred.iloc[4:8,:].sum(axis=0), hred.iloc[9:,:].sum(axis=0)], 
                         index=['1','2','3-4','5-9','10+'],
                         columns=['1','2','3-4','5-9','10+']).T

    # normalize
    hred_exp_dist_by_imp_sz = hred.div(hred.sum(axis=1).astype(float), axis=0)

    return hred_imp_dist_by_exp_sz, hred_exp_dist_by_imp_sz

if __name__=='__main__':
    """ Let's get it started in here """

    # READ DATA
    dat = pd.read_csv('/home/veryshuai/Documents/research/tradenet/manipulation/aea2015/graph_full.csv')
    
    # ELIMINATE DUPLICATES BY YEAR
    dat = dat.groupby(['EXP_ID','IMP_ID','YEAR']).first().reset_index()

    # COLLAPSE
    impcol = collapse('IMP_ID', dat)
    expcol = collapse('EXP_ID', dat)

    # COLLAPSE FOR SIZE SPECIFIC HISTOGRAMS
    hred_imp_dist_by_exp_sz, hred_exp_dist_by_imp_sz = sz(dat)

    # # MATCH DEATH PROBABILITY
    # mdp = mdp_calc(dat)
    # print "".join(['Empirical match death probability is ',str(mdp)])

    # TRANSITIONS
    exp_tmat, exp_treg, exp_fr = count_trans(expcol, 'EXP_ID')
    imp_tmat, imp_treg, imp_fr = count_trans(impcol, 'IMP_ID')

    # 2007 CLIENT COUNT HISTOGRAMS
    exp_hist = gen_hist(expcol, 'EXP_ID')
    imp_hist = gen_hist(impcol, 'IMP_ID')

    # OUTPUT
    exp_tmat.to_csv('results\exporter_client_count_trans.csv')
    imp_tmat.to_csv('results\importer_client_count_trans.csv')
    exp_treg.to_csv('results\export_trans_stata_data.csv')
    imp_treg.to_csv('results\import_trans_stata_data.csv')
    exp_fr.to_csv('results\export_form_dest_rate.csv')
    imp_fr.to_csv('results\import_form_dest_rate.csv')
    exp_hist.to_csv('results\exporter_client_count_hist_2007.csv')
    imp_hist.to_csv('results\importer_client_count_hist_2007.csv')
    expcol.to_csv('results\export_val_stata_data.csv')
    impcol.to_csv('results\import_val_stata_data.csv')
    hred_imp_dist_by_exp_sz.to_csv('results\import_client_dist_by_exporter_size.csv')
    hred_exp_dist_by_imp_sz.to_csv('results\export_client_dist_by_importer_size.csv')
