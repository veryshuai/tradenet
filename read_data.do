* This script loads raw stata data from Jim and writes it into my csv format

*pwd
cd /home/veryshuai/Documents/research/tradenet/manipulation/aea2015/

*load data
use /home/veryshuai/Documents/research/tradenet/data/colombia_imports/DIAN_M/output_old/dian_M_manu

*introduce concordance with country names
destring code_origin, g(PAIS3)
sort PAIS3
merge m:1 PAIS3 using crude_concordance_12
drop code_origin
rename dest_alf code_origin 

*keep the variables I use
keep name_imp id name_exp code_origin hs10 x_fob yr_month 

*format id's correctly
format %12.0f id

* OPTIONAL DROP OBSERVATIONS
drop if hs10 >= 8529000000 | hs10 < 8516000000
drop if code_origin != "CHN"

*write to csv
outsheet using network_data.csv, delim("|") noq replace
