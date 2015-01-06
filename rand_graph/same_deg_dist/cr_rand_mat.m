%cr_rand_mat.m
%This script generates and saves as "graph.csv" a uniform randomly generated graph

%random seed
rng(80085);

%generate node numbs
sell = randi(10000,250000,1);
buy = randi(10000,250000,1);
year = randi(19,250000,1) + 1991;
product = randi(1000000000,250000,1);
value = randi(10000,250000,1);

%generate matrix
A = [sell,buy,year,product,value];

%export
csvwrite('graph_rand.csv',A);
