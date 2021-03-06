# This python script makes ids just like those used at the census

import pandas as pd

if __name__ == "__main__":
    """loads network data, creates census ids,
        converts to numeric values, and saves"""

    # LOAD DATA
    dat = pd.read_csv('network_data.csv', delimiter='|', quotechar='"', error_bad_lines=False, encoding='iso-8859-1')
    dat.to_pickle('network_data.pickle')
    dat = pd.read_pickle('network_data.pickle')
    dat = dat.iloc[1:-2,:] # the very last observation is all nulls, no idea why

    #CREATE FIRM ID

    # First some data manipulation
    dat['code_origin'][pd.isnull(dat['code_origin']) == 1] = 'ERR' # replace NaNs with zero
    dat['name_exp'] = dat['name_exp'].str.replace('"','') # remove quotations
    dat['STR_ID'] = dat['name_exp'].str.strip().str[:7]\
            + dat['code_origin'].str.strip().str[:3]
            #+ dat['imp_city'].str.strip().str[:3]\
            #+ dat['imp_address'].str.strip().str[:2]
    dat['STR_ID'] = dat['STR_ID'].str.upper()

    #DROP NO NAMES, AND NON-INFORMATIVE NAMES
    dat = dat[dat['name_imp'] != '']
    dat = dat[dat['name_imp'] != 'TO ORDER']
    dat = dat[dat['name_imp'].str.strip() != 'TO THE ORDER OF']
    dat = dat[dat['name_imp'].str.strip() != 'TO THE ORDER']
    dat = dat[dat['name_imp'] != 'A LA ORDEN']

    #CREATE YEAR
    dat['YEAR'] = dat['yr_month'].apply(lambda x: int(x / 100))

    #YEAR FILTER
    dat = dat[dat['YEAR'] == 2003]
    
    #REPLACE STRINGS WITH NUMBERS - EXPORTER
    grouped = dat.groupby('STR_ID')['code_origin'].first() # unique row for each firm
    grouped = pd.DataFrame(grouped).reset_index().reset_index() # create unique numerical index for each firm
    dat     = pd.merge(dat, grouped, on='STR_ID') # merge into original data

    #REPLACE STRINGS WITH NUMBERS - IMPORTER
    #grouped = dat.groupby('exp_id')['dest_code'].first() # unique row for each firm
    grouped = dat.drop_duplicates(cols='id') # unique row for each firm
    grouped = grouped.reset_index().drop('level_0', 1).reset_index() # create unique numerical index for each firm
    grouped['index'] = grouped['level_0'] #kludge to make indexes match
    grouped = grouped[['index', 'id']]
    dat     = pd.merge(dat, grouped, on='id', suffixes=('_x','_y') )# merge into original data

    #CREATE NUM ID TRANSLATION LISTS
    dat[['STR_ID', 'index_x']].groupby('index_x').first().to_csv('importer_id.csv', encoding='utf-8')
    dat[['id', 'index_y']].groupby('index_y').first().to_csv('exporter_id.csv', encoding='utf-8')

    #CREATE REDUCED DATA
    red_dat         = dat[['index_y','index_x','YEAR','hs10','x_fob','code_origin_x','STR_ID', 'id', 'name_exp','name_imp']]
    red_dat.columns = ['IMP_ID','EXP_ID','YEAR','hs10','x_fob','code_origin','exp_alf','imp_id_orig', 'exp_name', 'imp_name']

    #OUTPUT TO CSV
    red_dat.to_csv('graph_trans.csv', encoding='utf-8')

