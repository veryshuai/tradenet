# This script creates bipartite plots and stats (mostly with Colombian sellers as nodes)

import igraph as ig
import numpy as np
import scipy
import pandas as pd
import matplotlib.pyplot as plt
import math
import random
import pickle
from collections import defaultdict

def load_dat():
    graph = ig.read('igraph_small.csv',format='edge')
    vals = pd.read_csv('vals_small.csv')['val']
    hs = pd.read_csv('vals_small.csv')['hs10']
    hss = pd.read_csv('vals_small.csv')['hs_source']
    exp_alf = pd.read_csv('vals_small.csv')['exp_alf']
    source = pd.read_csv('vals_small.csv')['source']
    imp_name = pd.read_csv('vals_small.csv')['imp_name']
    exp_name = pd.read_csv('vals_small.csv')['exp_name']
    atts = {'vals': vals,'hs': hs,'exp_alf': exp_alf,
            'hss': hss,'source': source,
            'imp_name': imp_name, 'exp_name': exp_name}
    return graph, atts

def what_buyers(es, coun):
    '''takes an igraph edgesequence, and returns list
    of sellers who source ANY shipment from coun'''

    #find sellers
    sell_to_us = []
    for obj in graph.es:
        if obj['source'] == coun:
            sell_to_us.append(obj.target)

    #unique list
    uniq = set(sell_to_us)
    res = list(uniq)

    return res

def most_frequent(dat_vec):
    '''returns the most frequent value from a data
    vector'''

    vcounts = dat_vec['val'].value_counts()

    if pd.notnull(dat_vec.val.iat[0]): #avoids an error
        most_frequent_val = vcounts.index.values[0]
    else:
        print 'WARNING: Encountered null in most frequent val calc'
        most_frequent_val = 'NULL'

    return most_frequent_val

def source_hs(es,lab):
    '''takes an igraph edgesequence, and returns tuple 
    of lists of vertices and hs codes to the US'''

    #find sellers
    raw_tups = []
    for obj in graph.es:
        i = obj.target
        h = obj[lab]
        raw_tups.append((i, h))

    #get most frequent
    tup_dat = pd.DataFrame(raw_tups, columns=['firm_id','val'])
    uniq_dat = tup_dat.groupby('firm_id').apply(most_frequent)

    #get lists rather than a list of tuples
    ids = uniq_dat.index.values
    hss = uniq_dat.values

    return (ids, hss)

def make_projection(graph, atts):
    """ makes bipartite projections, returns seller projection"""

    # PREPARE EDGE ATTRIBUTES
    graph.es['val'] = list(atts['vals'])
    graph.es['hs'] = list(atts['hs'])
    graph.es['exp_alf'] = list(atts['exp_alf'])
    graph.es['hss'] = list(atts['hss'])
    graph.es['source'] = list(atts['source'])
    graph.es['imp_name'] = list(atts['imp_name'])
    graph.es['exp_name'] = list(atts['exp_name'])

    # PREPARE VERTEX ATTRIBUTES
    # The strength member function sums all of the edge values
    graph.vs['val'] = graph.strength(graph.vs, weights='val')
    # Get list of importers who source from the US
    us_list = what_buyers(graph.es, 'USA')
    graph.vs['US'] = 0
    graph.vs[us_list]['US'] = 1
    # Get list of exporters who sell to a seleted foreign coutnry
    us_list = what_buyers(graph.es, 'CHN')
    graph.vs['CHN'] = 0
    graph.vs[us_list]['CHN'] = 1
    # Get most frequent hs by exporter
    hs_tup = source_hs(graph.es,'hss')
    graph.vs['hs_source'] = 0
    graph.vs[hs_tup[0]]['hs_source'] = hs_tup[1]
    # Get most frequent source
    source_tup = source_hs(graph.es,'source')
    graph.vs['source'] = 0
    graph.vs[source_tup[0]]['source'] = source_tup[1]
    # # Get most frequent source name
    # source_tup = source_hs(graph.es,'exp_name')
    # graph.vs['exp_name'] = 0
    # graph.vs[source_tup[0]]['exp_name'] = source_tup[1]
    # Get most valuable source 
    max_exp = pd.read_pickle('max_exp.pickle')
    graph.vs['exp_name'] = max_exp
    # Get most frequent dest name
    source_tup = source_hs(graph.es,'imp_name')
    graph.vs['imp_name'] = 0
    graph.vs[source_tup[0]]['imp_name'] = source_tup[1]
    
    # SIZES FROM graph.csv
    size = 244 
    edge_size = 334 
    big_size = 451 

    sub = big_size - size

    # MAKE THE TWO TYPES (SELLER AND BUYER)
    graph.vs['type'] = [1] * big_size
    graph.vs[size:]['type'] = [0] * sub 

    # PROEJECT AND ADD ATTRIBUTES
    proj1, proj2 = graph.bipartite_projection()
    proj1.vs['val'] = graph.vs[size+1:big_size]['val']
    proj1.vs['val'] = graph.vs[size+1:big_size]['val']


    # WRITE AND READ
    proj1.write_pickle('proj1.pickle')
    proj1 = ig.read('proj1.pickle')
    print(ig.summary(proj1))

    return proj1, proj2

def get_comps(proj1):
    """ finds components and component statistics"""

    totval = sum(proj1.vs['val'])
    clust = proj1.clusters()
    lcc = clust.giant()
    giantval = sum(lcc.vs['val'])

    print("".join(['Diameter: ', str(proj1.diameter())]))
    print("".join(['Average path length: ', str(proj1.average_path_length())]))
    print("".join(['Seller count: ', str(proj1.vcount())]))
    print("".join(['Percent sellers in giant component: ', str(lcc.vcount()/float(proj1.vcount()))]))
    print("".join(['Total value, FOB dollars: ', str(totval)]))
    print("".join(['Percent value in giant component: ',
                    str(giantval / float(totval))]))
    return clust, lcc, totval, giantval


def csize(clust):
    """ calculate component sizes and print counts"""

    # GET COMPONENT SIZES
    cv_size = []
    for k in range(len(clust)):
        verts = clust.subgraph(k).vcount()
        cv_size.append(verts)
    
    # PRINT HISTOGRAM
    print("COMPONENT SIZE HISTOGRAM")
    print('')
    for k in range(27):
        print("".join([str(k), ',', str(cv_size.count(k))]))
    print('')
    
    # Confirm 2nd largest component size
    print("".join(['Largest component size: ',
        str(sorted(cv_size)[-1])]))
    print("".join(['2nd largest component size: ',
        str(sorted(cv_size)[-2])]))

    return 0

def plot_comp(comp, fname, layout_name):
    """ plot component """

    size = len(comp.vs)
    edge_size = len(comp.es)
    comp.vs['label'] = [''] * size
    comp.vs['size']  = [math.log(x) for x in comp.vs.degree()]
    #comp.vs['label_size']  = [0] * size
    comp.es['arrow_size']  = [0] * edge_size
    comp.es['width']  = [0.01] * edge_size
    comp.es['transparency']  = [0.5] * edge_size
    comp.es['color']  = 'gray'

    # try a plot
    likey_layout = 'n'
    while likey_layout == 'n':

        myseed = input('Enter random seed: ')
        # reduce size
        biggest = []
        for x in comp.vs:
            #if x['val'] > 8e4:
            if x['val'] > 0:
                biggest.append(x.index)
        print(len(biggest))

        #comp_new = comp.induced_subgraph(random.sample(range(len(comp.vs)),5000))
        comp_new = comp.induced_subgraph(comp.vs[biggest])
        clust = comp_new.clusters()
        lcc = clust.giant()
        random.seed(myseed)
        layout = lcc.layout(layout_name) #root=0

        for coloring in ['USA', 'CHN', 'hs', 'hs_val', 'sect', 'sect_val', 'source', 'exp_name', 'imp_name', 'community']:

            print(coloring)

            if coloring == 'USA':
                lcc.vs['label'] = '*' 
                color = []
                for x in lcc.vs['US']:
                    if x == 1:
                        color.append('red')
                    else:
                        color.append('grey')
                lcc.vs['label'] = '*' # shape of label
                lcc.vs['color'] = 'white' # remove vertices
                lcc.vs['size'] = [0] * size # make vertices tiny
                lcc.es['color']  = 'white' # remove edges
                lcc.vs['label_color'] = color
                lcc.vs['label_size']  = 15

            if coloring == 'CHN':
                color = []
                for x in lcc.vs['CHN']:
                    if x == 1:
                        color.append('red')
                    else:
                        color.append('grey')
                lcc.vs['label'] = '*' # shape of label
                lcc.vs['color'] = 'white' # remove vertices
                lcc.vs['size'] = [0] * size # make vertices tiny
                lcc.es['color']  = 'white' # remove edges
                lcc.vs['label_color'] = color
                lcc.vs['label_size']  = 15 

            if coloring == 'hs_val':
                trunk  = [int(x / 100000000) for x in lcc.vs['hs_source']]
                lcc.vs['label'] = trunk
                color = []
                for x in trunk:
                    if x % 7 == 0:
                        color.append('yellow')
                    if x % 7 == 1:
                        color.append('red')
                    if x % 7 == 2:
                        color.append('green')
                    if x % 7 == 3:
                        color.append('blue')
                    if x % 7 == 4:
                        color.append('orange')
                    if x % 7 == 5:
                        color.append('black')
                    if x % 7 == 6:
                        color.append('purple')
                lcc.vs['color'] = 'white'
                lcc.vs['size'] = [0] * size
                lcc.vs['label_color'] = color
                lcc.vs['label_size']  = [math.log(x / 1e5) for x in lcc.vs['val']]
                lcc.es['width']  = [0] * edge_size

            if coloring == 'hs':
                #trunk  = [int(x / 100000000) for x in lcc.vs['hs_source']]
                trunk  = [int(x / 1000000) - 8500 for x in lcc.vs['hs_source']]
                lcc.vs['label'] = trunk
                color = []
                for x in trunk:
                    if x % 7 == 0:
                        color.append('yellow')
                    if x % 7 == 1:
                        color.append('red')
                    if x % 7 == 2:
                        color.append('green')
                    if x % 7 == 3:
                        color.append('blue')
                    if x % 7 == 4:
                        color.append('orange')
                    if x % 7 == 5:
                        color.append('black')
                    if x % 7 == 6:
                        color.append('purple')
                lcc.vs['color'] = 'white'
                lcc.vs['size'] = [0] * size
                lcc.vs['label_color'] = color
                lcc.vs['label_size']  = [math.log(x) for x in lcc.vs.degree()]
                lcc.es['width']  = [0] * edge_size

            if coloring == 'sect':
                trunk  = [int(x / 100000000) for x in lcc.vs['hs_source']]
                color = []
                lab = [] 
                for x in trunk:
                    if x <= 24:
                        color.append('green')
                        lab.append('food')
                    if (x > 24 and x < 28) or (x > 70 and x < 84):
                        color.append('black')
                        lab.append('primary')
                    if (x >=28 and x <=70) or (x >= 84):
                        color.append('gray')
                        lab.append('manufactures')
                lcc.vs['label'] = lcc.vs['source']
                lcc.vs['color'] = 'white'
                lcc.vs['size'] = [0] * size
                lcc.vs['label_color'] = color
                lcc.vs['label_size']  = [math.log(x) for x in lcc.vs.degree()]
                lcc.es['width']  = [0] * edge_size

            if coloring == 'sect_val':
                trunk  = [int(x / 100000000) for x in lcc.vs['hs_source']]
                color = []
                lab = []
                for x in trunk:
                    if x <= 24:
                        color.append('green')
                    if (x > 24 and x < 28) or (x > 70 and x < 84):
                        color.append('black')
                    if (x >=28 and x <=70) or (x >= 84):
                        color.append('gray')
                lcc.vs['label'] = lcc.vs['source']
                lcc.vs['color'] = 'white'
                lcc.vs['size'] = [0] * size
                lcc.vs['label_color'] = color
                lcc.vs['label_size']  = [math.log(x / 1e5) for x in lcc.vs['val']]
                lcc.es['width']  = [0] * edge_size

            if coloring == 'source':
                trunk  = lcc.vs['source']
                lcc.vs['label'] = trunk
                color = []
                for x in trunk:
                    if x == 'USA':
                        color.append('red')
                    elif x == 'CHN':
                        color.append('green')
                    elif x == 'BRA':
                        color.append('blue')
                    elif hash(x) % 5 == 0:
                        color.append('yellow')
                    elif hash(x) % 5 == 1:
                        color.append('grey')
                    elif hash(x) % 5 == 2:
                        color.append('purple')
                    elif hash(x) % 5 == 3:
                        color.append('orange')
                    elif hash(x) % 5 == 4:
                        color.append('pink')
                lcc.vs['color'] = 'white'
                lcc.vs['size'] = [0] * size
                lcc.vs['label_color'] = color
                lcc.vs['label_size']  = [math.log(x) for x in lcc.vs.degree()]
                lcc.es['width']  = [0] * edge_size

            if coloring == 'exp_name':
                for x in lcc.vs['source']:
                    if hash(x) % 8 == 0:
                        color.append('yellow')
                    if hash(x) % 8 == 1:
                        color.append('red')
                    if hash(x) % 8 == 2:
                        color.append('green')
                    if hash(x) % 8 == 3:
                        color.append('blue')
                    if hash(x) % 8 == 4:
                        color.append('orange')
                    if hash(x) % 8 == 5:
                        color.append('black')
                    if hash(x) % 8 == 6:
                        color.append('purple')
                    if hash(x) % 8 == 7:
                        color.append('pink')
                trunk  = [x[:12] for x in lcc.vs['exp_name']]
                lcc.vs['label'] = trunk
                lcc.vs['label_size']  = [max(math.log(x / 5e3),0) for x in lcc.vs['val']]

            #if coloring == 'imp_name':
            #     for x in lcc.vs['source']:
            #         if hash(x) % 8 == 0:
            #             color.append('yellow')
            #         if hash(x) % 8 == 1:
            #             color.append('red')
            #         if hash(x) % 8 == 2:
            #             color.append('green')
            #         if hash(x) % 8 == 3:
            #             color.append('blue')
            #         if hash(x) % 8 == 4:
            #             color.append('orange')
            #         if hash(x) % 8 == 5:
            #             color.append('black')
            #         if hash(x) % 8 == 6:
            #             color.append('purple')
            #         if hash(x) % 8 == 7:
            #             color.append('pink')
            #     trunk  = [x[:12] for x in lcc.vs['imp_name']]
            #     lcc.vs['label'] = trunk
            #     lcc.vs['label_size']  = [max(math.log(x / 5e3),0) for x in lcc.vs['val']]

            if coloring == 'community':
                lcc.vs['size']  = [math.log(x) for x in lcc.vs.degree()]
                lcc.vs['label'] = [''] * size
                lcc = lcc.community_walktrap().as_clustering()

            
            ig.plot(lcc, 'results/' + fname + coloring + '.pdf',
                    layout = layout)

        likey_layout = input('What do you think?  Keep it? (y/n): ')

    return 0

def pl_hist(g):
    """creaate and save path length histogram to disk""" 

    #OPEN FILE FOR WRITING
    f = open('pl_hist.txt','w')  

    #CREATE PATH LENGTH HISTOGRAM  
    h = g.path_length_hist() 

    f.write(h.to_string(show_bars=False))

    return 0

def bc_hist(g, name):
    """create and save betweenness centrality histogram to disk""" 

    #GET BETWEENNESS LIST 
    bl = g.betweenness() 

    #GET DEGREE LIST 
    dl = g.degree()
    
    #CREATE SERIES
    bs = pd.Series(bl)
    ds = pd.Series(dl)

    #PRINT BETWEENNESS AND DEGREE
    bs.to_csv('bs_' + name + '.csv')
    ds.to_csv('ds_' + name + '.csv')

    #SCATTER
    #plt.scatter(ds,bs)
    #plt.show()

    return 0

def spath(lcc):
    '''statistics related to the shortest path in largest component'''

    #sp = lcc.shortest_paths_dijkstra(source=range(1000))
    ecc = lcc.eccentricity()
    print('Max eccentricity')
    print(max(ecc))
    print('Min eccentricity')
    print(min(ecc))
    print('Mean eccentricity')
    print(sum(ecc) / float(len(ecc)))

    return 0

def eigcent(lcc):
    '''statistics related to the eigenvector centrality of largest component'''

    cent = lcc.eigenvector_centrality() 
    cent_sort = sorted(cent) # sort by centrality, small to high
    print 'Ten most important importers (eig cent.) in reverse order:'
    for k in range(-10,0):
        idxmax = cent.index(cent_sort[k]) # get 10 most central nodes
        print(lcc.vs[idxmax]['imp_name'])
    #appearances = defaultdict(int)
    #twodig = [int(x / 100000000) for x in lcc.vs[lcc.neighbors(2213)]['hs_source']]
    # for curr in twodig:
    #     appearances[curr] += 1

    return 0

if __name__ == "__main__":
    """ runs all the functions """

    repickle = input('Repickle data? (y/n): ')

    if repickle == 'y':
        # LOAD DATA
        graph, atts = load_dat()    

        # SET ATTRIBUTES
        proj1, proj2 = make_projection(graph, atts)
        
        # GET COMPONENTS AND VAL INFO
        clust, lcc, totval, giantval = get_comps(proj1)
        
        # PRINT COMPONENT SIZE COUNTS
        csize(clust)

        # SHORTEST PATH STUFF
        spath(lcc)

        # CENTRALITY STUFF
        eigcent(lcc)

        # GET PATH LENGTH HISTOGRAM
        pl_hist(proj1)

        # PRINT GLOBAL CLUSTERING COEFFICIENT OF GRAPH
        print 'Global clustering coefficient of largest component:' 
        print lcc.transitivity_undirected()

        # GET NODE BY NODE BETWEENNESS CENTRALITY HISTOGRAM
        bc_hist(proj1, 'expexp')
        bc_hist(proj2, 'impimp')

        # PLOT LARGEST COMPONENT
        # plot_comp(lcc, 'largest_component_drl.png', 'drl')
        pickle.dump(lcc, open('lcc.pickle','wb'))

    lcc = pickle.load(open('lcc.pickle','rb'))
    print('working on lgL')
    plot_comp(lcc, 'largest_component_lgl', 'lgl')
    # print('community')
    # plot_comp(lcc, 'largest_component_lgl_comm.png', 'lgl', 'community')
