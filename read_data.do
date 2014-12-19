* This script loads raw stata data from Jim and writes it into my csv format

*pwd
cd /home/veryshuai/Documents/research/tradenet/manipulation/aea2015/

*load data
use /home/veryshuai/Documents/research/tradenet/data/colombia_imports/DIAN_M/output_old/dian_M_manu

*keep the variables I use
keep name_imp id name_exp code_origin hs10 x_fob yr_month

*format id's correctly
format %12.0f id

*write to csv
outsheet using network_data.csv, delim("|") noq replace
