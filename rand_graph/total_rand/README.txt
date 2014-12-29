INSTRUCTIONS FOR RUNNING GRAPH ANALYSIS SCRIPT 

Files and folders included with this package:
ga_bip.m
cr_rand_mat.m
empty results folders

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
ga_bip.m
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
This is the main MATLAB script.  There needs to 
be a file called graph.csv in the same
folder with the script for it to run correctly.
graph.csv is a comma separated array with five
columns:
(1) Seller ID
(2) Buyer ID
(3) Year
(4) HS Code
(5) Value
There is assumed to be a row for every 
transaction.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
cr_rand_mat.m
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
For testing, cr_rand_mat.m generates a random
graph.csv array, with 10,000 firms and 
250,000 transaction observations, across
the years 1992-2010.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
empty results folders
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
These also need to be unzipped into the same
directory as ga_bip.m, or else matlab will
get confused.
 
