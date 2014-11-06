from __future__ import division
#using the snowball stemming algorithm, aka Porter2
from stemming.porter2 import stem
import json
import re
import requests


import config


all = ['generate_wordcloud_dict']


# sometimes you find words like "star - boundaries" in the text
# this removes those spaces so they can be recognized as a dashed word
collapse_regex = re.compile(r'\s*-\s*')
# these characters indicate word boundaries 
split_regex = re.compile(r'[\s.();~:]+')


def list_to_dict(l):
    """
    takes awkward list of list data structure returned in solr json and dictifies it
    """
    d={}
    for index, item in enumerate(l[::2]):
        key=item
        value=l[index*2+1]
        if isinstance(value, list) and value!=[]:
            d[key]=list_to_dict(value)
        else:
            d.setdefault(key, []).append(value)
    return d


def add_punc_and_remove_redundancies(info_dict, text_dict):
    
    '''
    takes care of the dashed word problem -- removes concatenated dashed words
    and reduces the count of tokens that were created from the dashed word
    '''
    
    punc_list = ["-", "/"]
    for p in punc_list:            
        word_collection = []
        for t in text_dict:
            if p in t and t[len(t)-1]!= p and t[0] != p:
                word_collection.append(t)

        for word in word_collection:
            tokens = word.split(p)
            full = ("").join(tokens)
            for w in info_dict:
                # replacing concatenated words in tfidf info with dashed word
                if w == full:
                    temp = info_dict[w]
                    info_dict[word] = temp
                    del info_dict[w]
                    continue
                # if word matches token instead, reduce its count
                for t in tokens:
                    if w == t:
                        info_dict[w]["tf"][0] -=1
    return info_dict


def cleanse_dict(token_freq_dict):  
    
    '''
    a final function to get rid of anything we know we don't want
    in the json we're returning to the user
    '''
    
    #   getting rid of super obvious url fragments in acronym and words
    for t in token_freq_dict.keys():
        lower_t = t.lower()
        if "www" in lower_t or "http" in lower_t:
            del token_freq_dict[t]
#     getting rid of anything that occurs only once
        elif token_freq_dict[t]["idf"] == 1.0:
            del token_freq_dict[t]
            
    return token_freq_dict


def build_dict(tf_idf_info, text_info):
    
    '''
    this function is responsible for taking the tfidf info, and the texts of the title
    and abstract that were returned by the solr query, and returning two dictionaries:
    a dictionary for all acronyms, and a dictionary for all other tokens
    '''
    
    token_freq_dict = {}
    acr_freq_dict= {}
        
    for i, _id in enumerate(tf_idf_info):
        all_data = tf_idf_info[_id]
        abstract_info = all_data.get("abstract", {})
        title_info = all_data.get("title", {})

        abstract_text = [t for t in text_info if t["id"] == _id][0].get("abstract", "").lower()
        abstract_text = collapse_regex.sub("-", abstract_text)
        abstract_text = split_regex.split(abstract_text)

        title_text = [t for t in text_info if t["id"] == _id][0].get("title", [])[0].lower()
        title_text = collapse_regex.sub("-", title_text)
        title_text = split_regex.split(title_text)

        abstract_info = add_punc_and_remove_redundancies(abstract_info, abstract_text)
        title_info = add_punc_and_remove_redundancies(title_info, title_text)

        abstract_info.update(title_info)
        d = abstract_info         

        # create the dictionaries
        for token in d:
        #ignore parts of dashed words which have already been cleaned up
        #by add_punc_and_remove_redundancies
            if d[token]["tf"][0] == 0:
                continue
            if "syn::" in token:
                continue
            if "acr::" in token:
                acr = token[5:].upper()
                # reducing count of non-acronym version of the token by 1
                try:
                    freq_dict = token_freq_dict[token[5:].lower()]["tokens"]
                    freq_dict[freq_dict.keys()[0]]-=1
                except KeyError:
                    pass
                if acr in acr_freq_dict:
                    acr_freq_dict[acr]['total_occurences']+=1
                else:
                    acr_freq_dict[acr]={'total_occurences':1}
                    acr_freq_dict[acr]['idf'] = d[token]['tf-idf'][0]/d[token]['tf'][0]

#              ADD WORDS longer than 2 letters
            elif len("".join([t for t in token if t.isalpha()])) > 2:
                key = stem("".join([t for t in token if t.isalpha()]))
                if key in token_freq_dict:
                    key_d =  token_freq_dict[key]["tokens"]
                    if token in key_d:
                        key_d[token] =key_d[token] + 1
                    else:
                        key_d[token] = 1
                        idf = d[token]['tf-idf'][0]/d[token]['tf'][0]
                        token_freq_dict[key]["idf"].append(idf)
                          
                else:
                    idf = d[token]['tf-idf'][0]/d[token]['tf'][0]
                    token_freq_dict[key] = {"tokens" : {token : 1}, "idf" : [idf] }
                    
    return token_freq_dict, acr_freq_dict


def wc_json(solr_json, min_percent_word, min_occurences_word):
    """
    This is the main word cloud creation function.
    It takes raw solr json with tf/idf info and returns a json object that has both term
    frequency and inverse term frequency for tokens in the tf/idf info. It stems these
    tokens in order to combine their counts, choosing the most common version of the word to 
    represent them.
    """
    text_info = solr_json["response"]["docs"]
    tf_idf_info = list_to_dict(solr_json['termVectors'][2:])
    num_records = len(solr_json["response"]["docs"])
        
    token_freq_dict, acr_freq_dict = build_dict(tf_idf_info, text_info)

#     keeping only stuff in token_freq_dict that appears > min_percent_word and > min_occurrences_word
#     creating a new dict with the most common incarnation of the token, and the total # of times
#     related stemmed words appeared
    temp_dict = {}
    for t in token_freq_dict:
        most_common_t_list = sorted(token_freq_dict[t]["tokens"].items(), key=lambda x:x[1], reverse=True)
        most_common_t_list = [x for x in most_common_t_list if x[1]==most_common_t_list[0][1]]
        for c in most_common_t_list:
            # if there's a hyphenated version, we choose that
            if '-' in c[0]:
                most_common_t = c[0]
                break
        # otherwise, whatever's shortest
        else:
            most_common_t = sorted(most_common_t_list, key=lambda x:len(x[0]))[0][0]
        num = sum(token_freq_dict[t]["tokens"].values())
        if num/num_records>= min_percent_word and num >= min_occurences_word:
            #find the average of all idf values
            idf = sum(token_freq_dict[t]["idf"])/len(token_freq_dict[t]["idf"])
            temp_dict[most_common_t] = {'total_occurences':num, "idf": idf}

    token_freq_dict = temp_dict

    #now also making sure acr_freq_dict only has words that appeared > min_percent_word times
    temp_dict = {}

    for a in acr_freq_dict:
#       adding lower case tokens (this might not always be strictly correct?)
        small_a = a.lower()
        if len(small_a) < 5 and small_a in token_freq_dict:
            acr_freq_dict[a]['total_occurences']+=token_freq_dict[small_a]['total_occurences']
            del token_freq_dict[small_a]
        
        total_occurences = acr_freq_dict[a]['total_occurences']
        if total_occurences/num_records>= min_percent_word and total_occurences >= min_occurences_word:
            temp_dict[a]=acr_freq_dict[a]
    acr_freq_dict = temp_dict
 
    token_freq_dict.update(acr_freq_dict)
    
    token_freq_dict = cleanse_dict(token_freq_dict)
         
    return token_freq_dict


def get_data_for_wordcloud(q, fq=None, rows=None, start=None):

    d = {
        'q' : q,
        'fq' : fq,
        'rows': rows,
        'start': start,
        'facets': [], 
        'highlights': [],
        'defType':'aqp', 
        'tv.tf_idf': 'true', 
        'tv.tf': 'true', 
        'tv.positions':'false',
        'tf.offsets':'false',
        'tv.fl':'abstract,title',
        'fl':'id,abstract,title',
        'wt': 'json'
        
         }
    response = requests.get(config.SOLR_PATH , params = d)
    
    if response.status_code == 200:
        results = response.json()
        return results
    else:
        return None


def generate_wordcloud(q,fq=None,rows=None,start=None, min_percent_word=None, min_occurences_word=None):

    if not rows or rows > config.MAX_RECORDS:
        rows = config.MAX_RECORDS
    if not start:
        start = config.START
    if not min_percent_word:
        min_percent_word = config.MIN_PERCENT_WORD
    if not min_occurences_word:
        min_occurences_word = config.MIN_OCCURENCES_WORD

    data = get_data_for_wordcloud(q, fq, rows, start)
    if data:
        return wc_json(data, min_percent_word=min_percent_word, min_occurences_word = min_percent_word)
    


