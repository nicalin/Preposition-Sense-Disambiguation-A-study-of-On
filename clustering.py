# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 19:15:46 2020

@author: User
"""

from nltk.corpus import wordnet
from nltk.corpus import wordnet as wn
from collections import defaultdict
from pprint import pprint
import json
import copy

#read jason file
with open('ON_WN_sense_dict.json' , 'r') as reader:
    ON_WN_sense_dict = json.loads(reader.read())
    
print(ON_WN_sense_dict['在…上面；到…上面']['VonN_wn'])    
print(ON_WN_sense_dict['在…上面；到…上面']['VonN_wn'][0][2])


#hierarchy clustering tree
#Meaning: 1st: cluster: [synsets][LCS][avg similarity]
on_hierarchy_cluster_tree = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: dict())))

#similarity matrix
#Meaning: syn1: syn2: wup
similarity_matrix = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0)))


"""Construct Similarity Matrix"""
for sense in ON_WN_sense_dict:
    
    
    wn_len = len(ON_WN_sense_dict[sense]['VonN_wn'])
    for i in range(wn_len-1):
        for j in range(i+1 ,wn_len):
            syn1 = ON_WN_sense_dict[sense]['VonN_wn'][i][2]
            syn2 = ON_WN_sense_dict[sense]['VonN_wn'][j][2]
            
            if syn1 != 'None' and syn2 != 'None':
                synset1 = wn.synset(syn1)
                synset2 = wn.synset(syn2)
                sim = wn.wup_similarity(synset1,synset2)
                
                if syn1 == syn2:
                    if similarity_matrix[sense][syn1][syn2] == 0:
                        similarity_matrix[sense][syn1][syn2] = 2
                    else:
                        similarity_matrix[sense][syn1][syn2] += 1 
                else:
                    if sim != None:
                        similarity_matrix[sense][syn1][syn2] = sim
                    else:
                        similarity_matrix[sense][syn1][syn2] = 0
                
def calculate_max_sim(c_sense, c_sim_tree, p_len, c_len):

    max_sim = 0
    comb=[]
    
    sim_tree = c_sim_tree
    
    for k in sim_tree:
        for l in sim_tree:
            if l > k:
                avg_tmp = 0
                avg_count = 0
                for syn1 in sim_tree[k]['synsets']:
                    for syn2 in sim_tree[l]['synsets']:
                        if syn1 in similarity_matrix[c_sense] and syn2 in similarity_matrix[c_sense][syn1]:
                            avg_tmp += similarity_matrix[c_sense][syn1][syn2]
                        else:    
                            avg_tmp += similarity_matrix[c_sense][syn2][syn1]
                        avg_count += 1   
                avg_tmp = avg_tmp/avg_count
                if avg_tmp > max_sim:
                    max_sim = avg_tmp
                    comb=[k,l] 
                 
    if comb == []:
        return sim_tree
    
    else:
        sim_tree[comb[0]]['synsets'].extend(sim_tree[comb[1]]['synsets'])
        sim_tree[comb[0]]['avg sim'] = max_sim
        if max_sim > 0.5:
            cut[c_sense] += 1
        if sim_tree[comb[0]]['LCS'] != 'None' and sim_tree[comb[1]]['LCS'] != 'None':     
            syns = wn.synset(sim_tree[comb[0]]['LCS']).lowest_common_hypernyms(wn.synset(sim_tree[comb[1]]['LCS']))
            names = [ s.name() for s in syns ] 
            
            if names != []:
                sim_tree[comb[0]]['LCS'] = names[0]
            else:
                sim_tree[comb[0]]['LCS'] = 'None'
        else:
            sim_tree[comb[0]]['LCS'] = 'None'
        del sim_tree[comb[1]]
        return sim_tree
 

"""Construct Similarity tree"""

cut_dict = defaultdict(lambda: defaultdict(lambda: dict()))    


for sense in ON_WN_sense_dict:
    cut = {}
    wn_len = len(ON_WN_sense_dict[sense]['VonN_wn'])
    
    
    for i in range(wn_len):
        if ON_WN_sense_dict[sense]['VonN_wn'][wn_len-1-i][2] == 'None':
            del ON_WN_sense_dict[sense]['VonN_wn'][wn_len-1-i]
    
    wn_len = len(ON_WN_sense_dict[sense]['VonN_wn'])
    
    for i in range(wn_len):
        if i==0:
            for j in range(wn_len):
                syn = []
                syn.append(ON_WN_sense_dict[sense]['VonN_wn'][j][2])
                on_hierarchy_cluster_tree[sense][0][j]['synsets'] = syn
                
                on_hierarchy_cluster_tree[sense][0][j]['LCS'] = ON_WN_sense_dict[sense]['VonN_wn'][j][2]
                on_hierarchy_cluster_tree[sense][0][j]['avg sim'] = 1 
                cut[sense] = 0
        else:
            sim_tree = copy.deepcopy(on_hierarchy_cluster_tree[sense][i-1])
            on_hierarchy_cluster_tree[sense][i]=calculate_max_sim(sense, sim_tree, wn_len, wn_len-i)
        
    
    if wn_len != 0:
        cut_dict[sense]=on_hierarchy_cluster_tree[sense][cut[sense]]


"""Convert all_scores to dict"""

with open('on_wn_n_cluster.json', 'w') as outfile:
    json.dump(on_hierarchy_cluster_tree, outfile, ensure_ascii=False)


with open('on_wn_n_cluster_cut.json', 'w') as outfile1:
    json.dump(cut_dict, outfile1, ensure_ascii=False)

#Verb
#hierarchy clustering tree
#Meaning: 1st: cluster: [synsets][LCS][avg similarity]
on_v_hierarchy_cluster_tree = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: dict())))

#similarity matrix
#Meaning: syn1: syn2: wup
v_similarity_matrix = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0)))


"""Construct Similarity Matrix"""
for sense in ON_WN_sense_dict:
    
    print(sense)
    wn_len = len(ON_WN_sense_dict[sense]['VonN_wn'])
    for i in range(wn_len-1):
        for j in range(i+1 ,wn_len):
            syn1 = ON_WN_sense_dict[sense]['VonN_wn'][i][0]
            syn2 = ON_WN_sense_dict[sense]['VonN_wn'][j][0]
            if syn1 != 'NO_V' and syn1 != 'None' and syn2 != 'NO_V' and syn2 != 'None':
                synset1 = wn.synset(syn1)
                synset2 = wn.synset(syn2)
                sim = wn.wup_similarity(synset1,synset2)
                
                if syn1 == syn2:
                    if v_similarity_matrix[sense][syn1][syn2] == 0:
                        v_similarity_matrix[sense][syn1][syn2] = 2
                    else:
                        v_similarity_matrix[sense][syn1][syn2] += 1 
                else:
                    if sim != None:
                        v_similarity_matrix[sense][syn1][syn2] = sim
                    else:
                        v_similarity_matrix[sense][syn1][syn2] = 0


def calculate_v_max_sim(c_sense, c_sim_tree, p_len, c_len):

    max_sim = 0
    comb=[]
    
    sim_tree = c_sim_tree
    
    for k in sim_tree:
        for l in sim_tree:
            if l > k:
                avg_tmp = 0
                avg_count = 0
                for syn1 in sim_tree[k]['synsets']:
                    for syn2 in sim_tree[l]['synsets']:
                        if syn1 in v_similarity_matrix[c_sense] and syn2 in v_similarity_matrix[c_sense][syn1]:
                            avg_tmp += v_similarity_matrix[c_sense][syn1][syn2]
                        else:    
                            avg_tmp += v_similarity_matrix[c_sense][syn2][syn1]
                        avg_count += 1   
                avg_tmp = avg_tmp/avg_count
                if avg_tmp > max_sim:
                    max_sim = avg_tmp
                    comb=[k,l] 
                
                    
    if comb == []:
        return sim_tree
    
    else:
    
        sim_tree[comb[0]]['synsets'].extend(sim_tree[comb[1]]['synsets'])
        sim_tree[comb[0]]['avg sim'] = max_sim
        if max_sim > 0.3:
            v_cut[c_sense] += 1  
        if sim_tree[comb[0]]['LCS'] != 'None' and sim_tree[comb[1]]['LCS'] != 'None':     
            syns = wn.synset(sim_tree[comb[0]]['LCS']).lowest_common_hypernyms(wn.synset(sim_tree[comb[1]]['LCS']))
            names = [ s.name() for s in syns ] 
            
            if names != []:
                sim_tree[comb[0]]['LCS'] = names[0]
            else:
                sim_tree[comb[0]]['LCS'] = 'None'
        else:
            sim_tree[comb[0]]['LCS'] = 'None'
        del sim_tree[comb[1]]
        return sim_tree


"""Construct Similarity tree"""

v_cut_dict = defaultdict(lambda: defaultdict(lambda: dict()))    


for sense in ON_WN_sense_dict:
    v_cut = {}
    wn_len = len(ON_WN_sense_dict[sense]['VonN_wn'])
    
    
    for i in range(wn_len):
        if ON_WN_sense_dict[sense]['VonN_wn'][wn_len-1-i][0] == 'None' or ON_WN_sense_dict[sense]['VonN_wn'][wn_len-1-i][0] == 'NO_V':
            del ON_WN_sense_dict[sense]['VonN_wn'][wn_len-1-i]
    
    wn_len = len(ON_WN_sense_dict[sense]['VonN_wn'])
    
    for i in range(wn_len):
        if i==0:
            for j in range(wn_len):
                syn = []
                syn.append(ON_WN_sense_dict[sense]['VonN_wn'][j][0])
                on_v_hierarchy_cluster_tree[sense][0][j]['synsets'] = syn
                
                on_v_hierarchy_cluster_tree[sense][0][j]['LCS'] = ON_WN_sense_dict[sense]['VonN_wn'][j][0]
                on_v_hierarchy_cluster_tree[sense][0][j]['avg sim'] = 1 
                v_cut[sense] = 0
        else:
            sim_tree = copy.deepcopy(on_v_hierarchy_cluster_tree[sense][i-1])
            on_v_hierarchy_cluster_tree[sense][i]=calculate_v_max_sim(sense, sim_tree, wn_len, wn_len-i)
        
    
    if wn_len != 0:
        v_cut_dict[sense]=on_v_hierarchy_cluster_tree[sense][v_cut[sense]]
    

with open('on_wn_v_cluster.json', 'w') as outfile:
    json.dump(on_v_hierarchy_cluster_tree, outfile, ensure_ascii=False)
       

with open('on_wn_v_cluster_cut.json', 'w') as outfile1:
    json.dump(v_cut_dict, outfile1, ensure_ascii=False)                                 
    



              