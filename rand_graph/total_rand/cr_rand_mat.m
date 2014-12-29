%cr_rand_mat.m
%This script generates and saves as "graph.csv" a uniform randomly generated graph

%random seed
rng(80085);

%sizes
imp_number = 89973;
exp_number = 175724;
edge_number = 1016144;
year_number = 17;
year_start = 1995;

%generate node numbs
sell = randi(exp_number,edge_number,1);
buy = randi(imp_number,edge_number,1);
year = randi(year_number,edge_number,1) + year_start;
product = randi(1000000000,edge_number,1);
value = randi(10000,edge_number,1);

%generate matrix
A = [sell,buy,year,product,value];

%export
csvwrite('graph_rand.csv',A);
