* This do file uses colombia network data to run some regressions related to Gibrat's law

log using results/gibrat_regs.log, replace

*********************EXPORTERS*****************************

clear 
set more off

* GET WORKING DIRECTORY
*cd /gpfs/home/dcj138/work/networks/gibrat_regs/

* IMPORT DATA
insheet using "results/export_trans_stata_data.csv"

* CREATE LOGS
g ln_first = ln(first)
g ln_last = ln(v2)
g ln_first2 = ln_first^2

* NAIVE OLS
reg ln_last ln_first ln_first2

* HECKMAN SELECTION
* Note, I double checked (wikipedia) that the model is formally identified from 
* normality assumption when 1st and 2nd stage contain same explanatory variables
heckman ln_last ln_first, sel(ln_first) twostep

* * SCATTER
* graph twoway (scatter ln_last ln_first) (lfit ln_first ln_first) (lfit ln_last ln_first), legend(off) xtitle("ln(t)") ytitle("ln(t+1)")
* graph export "results/exporter_scatter.png", replace
* 
* * LARGE FIRMS ONLY
* reg ln_last ln_first if first > 10
* graph twoway (scatter ln_last ln_first) (lfit ln_first ln_first) (lfit ln_last ln_first) if first > 10, legend(off) xtitle("ln(t)") ytitle("ln(t+1)")
* graph export "results/exporter_scatter_large_firms.png", replace


***************************IMPORTERS*****************************

clear 
set more off

* GET WORKING DIRECTORY
*cd /gpfs/home/dcj138/work/networks/gibrat_regs/

* IMPORT DATA
insheet using "results/import_trans_stata_data.csv"

* CREATE LOGS
g ln_first = ln(first)
g ln_last = ln(v2)
g ln_first2 = ln_first^2

* NAIVE OLS
reg ln_last ln_first ln_first2

* HECKMAN SELECTION
* Note, I double checked (wikipedia) that the model is formally identified from 
* normality assumption when 1st and 2nd stage contain same explanatory variables
heckman ln_last ln_first, sel(ln_first) twostep

* * SCATTER
* graph twoway (scatter ln_last ln_first) (lfit ln_first ln_first) (lfit ln_last ln_first), legend(off) xtitle("ln(t)") ytitle("ln(t+1)")
* graph export "results/importer_scatter.png", replace
* 
* * LARGE FIRMS ONLY
* reg ln_last ln_first if first > 10
* graph twoway (scatter ln_last ln_first) (lfit ln_first ln_first) (lfit ln_last ln_first) if first > 10, legend(off) xtitle("ln(t)") ytitle("ln(t+1)")
* graph export "results/importer_scatter_large_firms.png", replace

log close
