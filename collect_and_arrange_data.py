# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 15:53:20 2019

@author: User
"""
import json
from collections import defaultdict
import re
from pywsd import disambiguate
from nltk.corpus import wordnet as wn


def writeJSON(dictionary, file_name): 
    outf = open(file_name,'w',encoding = 'UTF-8')
    json.dump(dictionary, outf, ensure_ascii = False)
    outf.close()
    
    return


def UnifyLen(on_dict):
    """Purpose: to unify the lengths of element under each key (examples, POS, split_ex..) of the same sentence"""
    
    temp_dict = defaultdict(lambda: defaultdict(list))
    
    for ch_sense, details in on_dict['preposition'].items():
        for info_type, sent_or_pos in details.items():
            if info_type == 'examples':
                index = 0
                split_lst = []
                for sent in sent_or_pos:
                    
                    #add space before abbreviations
                    abv = re.compile('\'')
                    
                    if re.search(abv, sent):
                        sent = re.sub(abv, " '", sent)                   
                        on_dict['preposition'][ch_sense][info_type][index] = sent
                                        
                    #process special symbols-1
                    price_punct = re.compile("([.\,:;\-?!€$£\s\)\/])")
                    
                    split_sent = re.split(price_punct, sent)
                    for element in split_sent:
                        if element == ' ':
                            split_sent.remove(element)
                        elif element == '':
                            split_sent.remove(element)
                        
                    #process special symbols-2
                    for element in split_sent: 
                        if element == ' ':
                            split_sent.remove(element)
                        elif element == '':
                            split_sent.remove(element)
                   
                    sent = ' '.join(split_sent)
                    on_dict['preposition'][ch_sense][info_type][index] = sent
                    
                    #Add splitted sentence
                    split_lst.append(split_sent)                        
                    index += 1
                      
            temp_dict[ch_sense]['split_ex'] = split_lst
            
        
    #Add splitted sentences to [on_dict]   
    for ch_sense, details in on_dict['preposition'].items():
        for ch, split_sent in temp_dict.items():
            if ch_sense == ch:
                on_dict['preposition'][ch_sense]['split_ex'] = temp_dict[ch_sense]['split_ex']
                break
        
    #Check whether the lengths of [POS] and [split] are same
    to_be_del = []
    for ch_sense, details in on_dict['preposition'].items():
        for info_type, info in details.items():
            if info_type == 'pos_of_examples':
                index = 0
                for sent_pos in info:
                    
                    sent_pos_len = len(sent_pos.split())
                    split_ex_len = len(on_dict['preposition'][ch_sense]['split_ex'][index])
                    
                    if sent_pos_len != split_ex_len:
                        to_be_del.append([ch_sense, on_dict['preposition'][ch_sense]['examples'][index], on_dict['preposition'][ch_sense]['pos_of_examples'][index], on_dict['preposition'][ch_sense]['split_ex'][index]])
                        
                    index += 1
    
    #Delete sentences whose amount of elements under [POS] key are inconsistent to that of the amount of words in the same sentences
    for del_index in to_be_del:
        ch_sense = del_index[0]
        examples = del_index[1]
        pos = del_index[2]
        split_ex = del_index[3]

        on_dict['preposition'][ch_sense]['examples'].remove(examples)
        on_dict['preposition'][ch_sense]['pos_of_examples'].remove(pos)
        on_dict['preposition'][ch_sense]['split_ex'].remove(split_ex)   
        
    #Add split POS
    for ch_sense, details in on_dict['preposition'].items():
        all_split_pos = [] #All split pos (all sentences) of a particular sense
        for each_sent_pos in details['pos_of_examples']:
            each_sent_pos = [split_pos for split_pos in each_sent_pos.split(' ')]
            all_split_pos.append(each_sent_pos)
        
        on_dict['preposition'][ch_sense]['split_pos'] = all_split_pos
    
    
    
    return 


def AddSynset(on_dict):
    
    """Purpose: To disambiguate the target sentences and add the result to [on_dict]"""
    
    all_wsd = defaultdict(list)
    for ch_sense, details in on_dict['preposition'].items():
        sent_wsd = []#disambiguate sentence
        for info_type, info in details.items():
            if info_type == 'examples':
                for sent in info:
                    get_sense = []
                    temp = disambiguate(sent)
                    for wd, sense in temp:
                        if type(sense) != type(None):#if the word can be disambiguated
                            sense = str(sense)
                            pattern = re.compile("(Synset\(\'|\'\))")
                            sense = re.sub(pattern, "", sense)                            
                            get_sense.append([wd, sense])
                        
                    sent_wsd.append(get_sense)                   
        all_wsd[ch_sense] = sent_wsd

   
    #Add disambiguated sentences to [on_dict]
    sense_dict = defaultdict(lambda: defaultdict(list))#recoed the WordNet senses of all words in the sentences
    for ch_sense, details in on_dict['preposition'].items():
        for info_type, info in details.items():
            if info_type == 'split_ex':
                sent_index = 0 
                for split_sent in info:
                    sense_lst = []
                    for i in range(len(split_sent)):
                        sense_lst.append('None')
                    
                    wd_index = 0
                    for wd in split_sent:
                        for wsd_wd in all_wsd[ch_sense][sent_index]:
                            if wd == wsd_wd[0]:
                                sense_lst[wd_index] = wsd_wd[1]
                                break
                        
                        wd_index += 1
                    
                    sense_dict[ch_sense]['wn_sense'].append(sense_lst)
                    sent_index += 1
    
    #Add the content of [sense_dict] to [on_dict]
    for ch_sense, details in on_dict['preposition'].items():
        on_dict['preposition'][ch_sense]['wn_sense'] = sense_dict[ch_sense]['wn_sense']
                 
    return 


def ChkSentPOS(on_dict):
    """
    Purpose: To check whether (1.) the sentence contains multiple ons (2.) the sentence contains a noun (object);
    If the setnence contatins multiple ons or does not contain an object, delete this sentence from data
    """
    
    to_be_del = []      
    for ch_sense, details in on_dict['preposition'].items():      
              
        #Check if there is more than one [on]
        sent_index = 0 
        for sent in details['split_ex']:
            on_num = 0
            for wd in sent:
                if wd == 'on':
                    on_num += 1
            if on_num > 1:
                all_info = [ch_sense, details['examples'][sent_index], details['pos_of_examples'][sent_index], details['split_ex'][sent_index], details['split_pos'][sent_index], details['wn_sense'][sent_index]]
                to_be_del.append(all_info)
                
            sent_index += 1
               
        #Check if the is any [noun] in the sentence
        sent_index = 0
        for sent in on_dict['preposition'][ch_sense]['split_pos']:
            if 'NOUN' not in sent:
                if 'PRON' not in sent and 'PROPN' not in sent:
                    all_info = [ch_sense, details['examples'][sent_index], details['pos_of_examples'][sent_index], details['split_ex'][sent_index], details['split_pos'][sent_index], details['wn_sense'][sent_index]]    
                    to_be_del.append(all_info)            
            sent_index += 1
    
    #Delete items
    for del_items in to_be_del:
        ch_sense = del_items[0]
        examples = del_items[1]
        pos_of_examples = del_items[2]
        split_ex = del_items[3]
        split_pos = del_items[4]
        wn_sense = del_items[5]

        on_dict['preposition'][ch_sense]['examples'].remove(examples)
        on_dict['preposition'][ch_sense]['pos_of_examples'].remove(pos_of_examples) 
        on_dict['preposition'][ch_sense]['split_ex'].remove(split_ex)
        on_dict['preposition'][ch_sense]['split_pos'].remove(split_pos)
        on_dict['preposition'][ch_sense]['wn_sense'].remove(wn_sense)
    
    return 
            

def GetTgIndex(split_ex, split_pos):
    
    """
    Purpose: Get indices of [V] [on] and [N] in a sentence
    Input: split_ex (list), split_pos (list)
    Output: the indices of [V], [on], and [N] (list; in the order of V on N)
    #Note: some ons are contained in phrases and therefore cannot get the [V]. In such case, 'NO_V' is returned to indicate the absence of V
    """
    
    #Get the position of "on" (anchor point)
    index = 0
    for wd in split_ex:
        if wd == 'on' or wd == 'On':
            ON_index = index
            break       
        index += 1
    
    #Get index of the target N (noun)
    for i in range(ON_index, len(split_pos), 1):
        if i == (len(split_pos)-1):#if not found after the anchor point, start finding from the beginning
            for j in range(0, ON_index, 1):
                if split_pos[j] == 'NOUN' or split_pos[j] == 'PRON' or split_pos[j] == 'PROPN':
                    N_index = j
                    break
        
        else:
            if split_pos[i] == 'NOUN' or split_pos[i] == 'PRON' or split_pos[i] == 'PROPN':
                N_index = i
                break

    #Get index of the target V (verb)
    V_index = 'NO_V'  
    for i in range(ON_index, -1, -1):
        if ON_index == 0:
            for j in range(ON_index, len(split_pos), 1):
                if split_pos[j] == 'VERB':
                    V_index = j
                    break
        else:
            if split_pos[i] == 'VERB':
                V_index = i
                break       
    
    return [V_index, ON_index, N_index]


def GetV_ON_N(on_dict):
    """
    Purpose: Extract the [V], [on], and [N] from every sentence
    """
    
    WN_sense_dict = defaultdict(lambda: defaultdict(list))
    for ch_sense, details in camb_ON_entry['preposition'].items():
        for i in range(0, len(details['examples']), 1):#i --> index of the current sentence
            indexes = GetTgIndex(details['split_ex'][i], details['split_pos'][i])
            
            if indexes[0] == 'NO_V':
                WN_sense_dict[ch_sense]['VonN_word'].append([indexes[0], details['split_ex'][i][indexes[1]], details['split_ex'][i][indexes[2]]])
                WN_sense_dict[ch_sense]['VonN_pos'].append([indexes[0], details['split_pos'][i][indexes[1]], details['split_pos'][i][indexes[2]]])
                WN_sense_dict[ch_sense]['VonN_wn'].append([indexes[0], details['wn_sense'][i][indexes[1]], details['wn_sense'][i][indexes[2]]])
                               
            else:
                WN_sense_dict[ch_sense]['VonN_word'].append([details['split_ex'][i][indexes[0]], details['split_ex'][i][indexes[1]], details['split_ex'][i][indexes[2]]])
                WN_sense_dict[ch_sense]['VonN_pos'].append([details['split_pos'][i][indexes[0]], details['split_pos'][i][indexes[1]], details['split_pos'][i][indexes[2]]])
                WN_sense_dict[ch_sense]['VonN_wn'].append([details['wn_sense'][i][indexes[0]], details['wn_sense'][i][indexes[1]], details['wn_sense'][i][indexes[2]]])
    
    return WN_sense_dict

                
##################
#      MAIN      #
##################
 
camb_ON_entry = json.load(open('Cambridge_All_On_sent_with_result.json', encoding = 'UTF-8'))


#Add spaces around quotations (so that the length under each key could be consistent)
for ch_sense, details in camb_ON_entry['preposition'].items():
    for info_type, sentences in details.items():
        
        if info_type == 'examples':
            index = 0
            for sent in sentences:
    
                #Process quotations
                if '\"' in sent:
                    if sent == '\"Where had we got up to?\" \"We were on page 42.\"':
                        sent = '\" Where had we got up to? \" \" We were on page 42. \"'
                    elif sent == '\"Is the shower fixed yet?\" \"I\'m working on it\".':
                        sent = '\" Is the shower fixed yet? \" \" I\'m working on it \".'
    
                    camb_ON_entry['preposition'][ch_sense][info_type][index] = sent
            
                #numbers
                if re.search(r"\d[\,\.]\d", sent):
                    
                    if sent == 'She\'s coming in on the 5.30 bus.':
                        sent = 'She\'s coming in on the 530 bus.'
                    elif sent == 'She\'s on (= earning) £25,000 a year.':
                        sent = 'She\'s on (= earning) £25000 a year.'
                    elif sent == 'New employees start on a basic salary of £25,000.':
                        sent = 'New employees start on a basic salary of £25000.'
                
                    camb_ON_entry['preposition'][ch_sense][info_type][index] = sent
        
                index += 1

#remove "(that)" individually
index = 0
for sent in camb_ON_entry['preposition']['處於…狀況（或過程）中']['examples']:
    if "(that)" in sent:
        sent = 'There are few indications the economy is on an upswing.'
        camb_ON_entry['preposition']['處於…狀況（或過程）中']['examples'][index] = sent
        break
    index += 1

camb_ON_entry['preposition']['處於…狀況（或過程）中']['pos_of_examples'][index] = 'ADV VERB ADJ NOUN DET NOUN VERB ADP DET NOUN PUNCT'


UnifyLen(camb_ON_entry)
AddSynset(camb_ON_entry)
ChkSentPOS(camb_ON_entry)
#WN_sense_dict = GetV_ON_N(camb_ON_entry)
#writeJSON(WN_sense_dict, 'ON_WN_sense_dict.json')


                    
                    
                    
                    
                    
                    