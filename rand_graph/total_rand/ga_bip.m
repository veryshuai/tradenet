%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% ga_bip.m
% "graph analysis bipartite"
% 
% This is a data mining program for analyzing  the buyer seller network of Colombia-US trade data
% This script calculates a few moments of the transactions graph located in file 'graph.csv'  
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% USER OPTIONS
cens_lev = 0; %if a histogram bin has smaller than cens_lev firms, it is deleted

%OPTIONAL COUNTRY TAG ON SAVE FILES
country = '';

% READ IN DATA
DAT = csvread('graph_rand.csv');

% CREATE ALL_YEAR VARIABLES
BUY_deg_all = int16.empty(0,0);
SELL_deg_all = int16.empty(0,0);
BUY_deg2_all = int16.empty(0,0);
SELL_deg2_all = int16.empty(0,0);

% LOOP THROUGH YEARS
for yr = 1996:2012
	display(['WORKING ON YEAR ', num2str(yr),'.']);
	
	% CREATE MATRIX FROM DATA
	RAW_A = DAT(DAT(:,3)==yr,1:2);

	% change the arbitrary firm ids to unique counting numbers [KEY_SELL,~,COUNT_A_SELL] = unique(RAW_A(:,1));
	[KEY_SELL,~,COUNT_A_SELL] = unique(RAW_A(:,1));
	[KEY_BUY,~,COUNT_A_BUY] = unique(RAW_A(:,2));

	% change type to a sparse matrix, with non-zero values set equal to one
	[~,l]=unique([COUNT_A_SELL,COUNT_A_BUY],'rows');
	A = sparse(COUNT_A_SELL(l,1),COUNT_A_BUY(l,1),1,size(KEY_SELL,1),size(KEY_BUY,1));
	 
	%DEGREE DISTRIBUTIONS
	display('Calculating Degree Distributions');
	BUY_deg = full(sum(A,1)');
	SELL_deg = full(sum(A,2));

	%APPEND TO ALL YEARS
	BUY_deg_all = [BUY_deg_all; BUY_deg];
	SELL_deg_all = [SELL_deg_all; SELL_deg];
	
	%DISTANCE 2 DEGREE 
	display('Calculating 2nd Degree Distributions');
	BUY_proj = A' * A;
	BUY_proj(1:size(BUY_proj,1)+1:end) = 0; %kill diagonals
	BUY_deg2 = full(sum(BUY_proj,2)); 
	SELL_proj = A * A';
	SELL_proj(1:size(SELL_proj,1)+1:end) = 0; %kill diagonals
	SELL_deg2 = full(sum(SELL_proj,2)); 
		
	%APPEND TO ALL YEARS
	BUY_deg2_all = [BUY_deg2_all; BUY_deg2];
	SELL_deg2_all = [SELL_deg2_all; SELL_deg2];

	% % LOCAL CLUSTERING COEFFICIENT
	% % see Latapy et. al (2008)
	% display('Calculating Clustering Coefficients');
	% % sellers
	% 	% pairwise
	% 	LOC_CLUST_PAIR = zeros(size(A,1));
	% 	FULL_A = full(A);
	% 	for k = 1:size(FULL_A,1)
	% 		ROW_BASE = FULL_A(k,:);
	% 		ind = find(ROW_BASE);
	% 		for m = ind
	% 			inind = find(FULL_A(:,m));
	% 			for n = inind'
	% 				if LOC_CLUST_PAIR(k,n) == 0 %avoid redoing what is already written
	% 					ROW_IN = FULL_A(n,:);
	% 					LOC_CLUST_PAIR(k,n) = (sum(sum([ROW_BASE;ROW_IN])==2)-1)/(sum(sum([ROW_BASE;ROW_IN])>=1)+1); %technical footnote: LOC_CLUST_PAIR is size of the intersection of neighborhoods/size of the union of neighborhoods. Since k and n are in each others neiborhoods, we actually have to add 1 to the denominator to get the correct number.
	% 				end	
	% 			end	
	% 		end	
	% 	end
	% 	% nodewise
	% 	LOC_CLUST_NODE_SELL = sum(LOC_CLUST_PAIR,2)./max(SELL_deg2,1); %the max is to avoid infs. 
	% 	% mean
	% 	LOC_CLUST_SELL = sum(LOC_CLUST_NODE_SELL)/(sum(LOC_CLUST_NODE_SELL>0));
	% % buyers 
	% 	% pairwise
	% 	LOC_CLUST_PAIR = zeros(size(A,2));
	% 	FULL_A = FULL_A';
	% 	for k = 1:size(FULL_A,1)
	% 		ROW_BASE = FULL_A(k,:);
	% 		ind = find(ROW_BASE);
	% 		for m = ind
	% 			inind = find(FULL_A(:,m));
	% 			for n = inind'
	% 				if LOC_CLUST_PAIR(k,n) == 0 %avoid redoing what is already written
	% 					ROW_IN = FULL_A(n,:);
	% 					LOC_CLUST_PAIR(k,n) = (sum(sum([ROW_BASE;ROW_IN])==2)-1)/(sum(sum([ROW_BASE;ROW_IN])>=1)+1); 
	% 				end	
	% 			end	
	% 		end	
	% 	end
	% 	% nodewise
	% 	LOC_CLUST_NODE_BUY = sum(LOC_CLUST_PAIR,2)./max(BUY_deg2,1); %the max is to avoid infs. 
	% 	% mean
	% 	LOC_CLUST_BUY = sum(LOC_CLUST_NODE_BUY)/(sum(LOC_CLUST_NODE_BUY>0));
	% 
	% % NOT PRIVACY PROTECTED, included so I don't forget to check it out later
	% % BUY_degdeg2scat = figure;
	% % scatter(BUY_deg,BUY_deg2);
	% % fname = sprintf('results/%d/BUY_degdeg2scat_%d.pdf',yr,yr);
	% % print(BUY_degdeg2scat,'-dpdf',fname);
	% % SELL_degdeg2scat = figure;
	% % scatter(SELL_deg,SELL_deg2);
	% % fname = sprintf('results/%d/SELL_degdeg2scat_%d.pdf',yr,yr);
	% % print(SELL_degdeg2scat,'-dpdf',fname);
	
	% WRITE RESULTS, for the most part histograms to protect privacy
	[BUY_deg_count,BUY_deg_edge] = hist(BUY_deg,1:300);
	BUY_deg_count = BUY_deg_count(BUY_deg_count>cens_lev);
	BUY_deg_edge = BUY_deg_edge(BUY_deg_count>cens_lev);
	fname = sprintf('results/%d/BUY_deg_count_%d%s',yr,yr,country);
	csvwrite(fname,BUY_deg_count);
	fname = sprintf('results/%d/BUY_deg_edge_%d%s',yr,yr,country);
	csvwrite(fname,BUY_deg_edge);
	
	[SELL_deg_count,SELL_deg_edge] = hist(SELL_deg,1:300);
	SELL_deg_count = SELL_deg_count(SELL_deg_count>cens_lev);
	SELL_deg_edge = SELL_deg_edge(SELL_deg_count>cens_lev);
	fname = sprintf('results/%d/SELL_deg_count_%d%s',yr,yr,country);
	csvwrite(fname,SELL_deg_count);
	fname = sprintf('results/%d/SELL_deg_edge_%d%s',yr,yr,country);
	csvwrite(fname,SELL_deg_edge);
	
	[BUY_deg2_count,BUY_deg2_edge] = hist(BUY_deg2,1:300);
	BUY_deg2_count = BUY_deg2_count(BUY_deg2_count>cens_lev);
	BUY_deg2_edge = BUY_deg2_edge(BUY_deg2_count>cens_lev);
	fname = sprintf('results/%d/BUY_deg2_count_%d%s',yr,yr,country);
	csvwrite(fname,BUY_deg2_count);
	fname = sprintf('results/%d/BUY_deg2_edge_%d%s',yr,yr,country);
	csvwrite(fname,BUY_deg2_edge);
	
	[SELL_deg2_count,SELL_deg2_edge] = hist(SELL_deg2,1:300);
	SELL_deg2_count = SELL_deg2_count(SELL_deg2_count>cens_lev);
	SELL_deg2_edge = SELL_deg2_edge(SELL_deg2_count>cens_lev);
	fname = sprintf('results/%d/SELL_deg2_count_%d%s',yr,yr,country);
	csvwrite(fname,SELL_deg2_count);
	fname = sprintf('results/%d/SELL_deg2_edge_%d%s',yr,yr,country);
	csvwrite(fname,SELL_deg2_edge);
	
	% [LOC_CLUST_NODE_BUY_count,LOC_CLUST_NODE_BUY_edge] = hist(LOC_CLUST_NODE_BUY,0:.0005:.5);
	% LOC_CLUST_NODE_BUY_count = LOC_CLUST_NODE_BUY_count(LOC_CLUST_NODE_BUY_count>cens_lev);
	% LOC_CLUST_NODE_BUY_edge = LOC_CLUST_NODE_BUY_edge(LOC_CLUST_NODE_BUY_count>cens_lev);
	% fname = sprintf('results/%d/LOC_CLUST_NODE_BUY_count_%d',yr,yr);
	% csvwrite(fname,LOC_CLUST_NODE_BUY_count);
	% fname = sprintf('results/%d/LOC_CLUST_NODE_BUY_edge_%d',yr,yr);
	% csvwrite(fname,LOC_CLUST_NODE_BUY_edge);
	% 
	% [LOC_CLUST_NODE_SELL_count,LOC_CLUST_NODE_SELL_edge] = hist(LOC_CLUST_NODE_SELL,0:.0005:.2);
	% LOC_CLUST_NODE_SELL_count = LOC_CLUST_NODE_SELL_count(LOC_CLUST_NODE_SELL_count>cens_lev);
	% LOC_CLUST_NODE_SELL_edge = LOC_CLUST_NODE_SELL_edge(LOC_CLUST_NODE_SELL_count>cens_lev);
	% fname = sprintf('results/%d/LOC_CLUST_NODE_SELL_count_%d',yr,yr);
	% csvwrite(fname,LOC_CLUST_NODE_SELL_count);
	% fname = sprintf('results/%d/LOC_CLUST_NODE_SELL_edge_%d',yr,yr);
	% csvwrite(fname,LOC_CLUST_NODE_SELL_edge);

	% BUY_corr = corr(BUY_deg,BUY_deg2);
	% SELL_corr =corr(SELL_deg,SELL_deg2);
	% fname = sprintf('results/%d/degdeg2corr_BUY_%d',yr,yr);
	% csvwrite(fname,BUY_corr);
	% fname = sprintf('results/%d/degdeg2corr_SELL_%d',yr,yr);
	% csvwrite(fname,SELL_corr);

end

    
    yr = 'all';
	% WRITE RESULTS FOR ALL YEARS, for the most part histograms to protect privacy
	[BUY_deg_count,BUY_deg_edge] = hist(BUY_deg_all,1:300);
	BUY_deg_count = BUY_deg_count(BUY_deg_count>cens_lev);
	BUY_deg_edge = BUY_deg_edge(BUY_deg_count>cens_lev);
	fname = sprintf('results/%s/BUY_deg_count_%s%s',yr,yr,country);
	csvwrite(fname,BUY_deg_count);
	fname = sprintf('results/%s/BUY_deg_edge_%s%s',yr,yr,country);
	csvwrite(fname,BUY_deg_edge);

	[SELL_deg_count,SELL_deg_edge] = hist(SELL_deg_all,1:300);
	SELL_deg_count = SELL_deg_count(SELL_deg_count>cens_lev);
	SELL_deg_edge = SELL_deg_edge(SELL_deg_count>cens_lev);
	fname = sprintf('results/%s/SELL_deg_count_%s%s',yr,yr,country);
	csvwrite(fname,SELL_deg_count);
	fname = sprintf('results/%s/SELL_deg_edge_%s%s',yr,yr,country);
	csvwrite(fname,SELL_deg_edge);

	[BUY_deg2_count,BUY_deg2_edge] = hist(BUY_deg2_all,1:300);
	BUY_deg2_count = BUY_deg2_count(BUY_deg2_count>cens_lev);
	BUY_deg2_edge = BUY_deg2_edge(BUY_deg2_count>cens_lev);
	fname = sprintf('results/%s/BUY_deg2_count_%s%s',yr,yr,country);
	csvwrite(fname,BUY_deg2_count);
	fname = sprintf('results/%s/BUY_deg2_edge_%s%s',yr,yr,country);
	csvwrite(fname,BUY_deg2_edge);

	[SELL_deg2_count,SELL_deg2_edge] = hist(SELL_deg2_all,1:300);
	SELL_deg2_count = SELL_deg2_count(SELL_deg2_count>cens_lev);
	SELL_deg2_edge = SELL_deg2_edge(SELL_deg2_count>cens_lev);
	fname = sprintf('results/%s/SELL_deg2_count_%s%s',yr,yr,country);
	csvwrite(fname,SELL_deg2_count);
	fname = sprintf('results/%s/SELL_deg2_edge_%s%s',yr,yr,country);
	csvwrite(fname,SELL_deg2_edge);

display('ALL DONE!');
