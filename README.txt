####################################################################
# COLOMBIA TRADE NETWORK PLOTS AND STATS                           #
####################################################################


######### MANIFEST ########
README.txt
network_data_sample.csv
make_census_ids.py
rem_dups.py
graph_manip.py
igraph_small.csv
vals_small.csv
bipartite_projection_plot.py

######## REQUIRED NON STANDARD PYTHON LIBRARIES ##############
pandas
igraph

######## HOW TO RUN #######
These instructions are for how to run the program from raw data.  If you would like to use the attached data, skip to step 6.

1. First, data needs to be put into the format of the file network_data_sample.csv.  I did this using the stata files prepared by Jim.

2. Use python to run make_census_ids.py.  This creates census style ids for importers using country names, firm names, and addresses.  The output of this file is called graph_trans.csv.

3. Use python to run rem_dups.py.  This removes duplicate entries of exporters and importers, and sums up the value of transactions between them.

4. Use python to run graph_manip.py.  This creates the edge list and attribute files igraph_small.csv and vals_small.csv used in the bipartite projection program.

5. A row must be added to the top of vals_small.csv as follows:
ids,val,dest_alf,hs10,hs_source,hs_dest,dest,imp_name

6. Use python to run bipartite_projection_plots.py, which will use igraph_small.csv and vals_small.csv.  You should be able to use the attached files if you wish.  This file generates the plot files, and generates some statistics which are printed into standard output.

######## NOTES ############
Tested using python 3.x in Ubuntu Linux 13.10.

