'''
File that takes care of the authors network
Version 2
mostly by Giovanni with some additions by Alex
'''


from __future__ import division
import histeq
from itertools import combinations
import networkx as nx
import community
import math
from networkx.readwrite import json_graph
from collections import defaultdict 
import requests

import config


__all__ = ['generate_network']


#Giovanni's config variables that don't change

#total number of links I can select
max_num_links = 12000
#total number of links with the same weight I can select
max_num_links_same_weight = 2000
#max number of authors per paper... if there are more authors I cut the paper for the links but not for the nodes
max_num_auth_paper = 15

#Giovanni's helper functions

def _remap_dict_in_range(mydict, newrange=[1, 100]):
    """function that transform a dictionary 
    in another with the values mapped in a defined range"""
    
    def translate(value, leftMin, leftMax, rightMin, rightMax):
        """local function that maps a single value"""
        # Figure out how 'wide' each range is
        leftSpan = leftMax - leftMin
        if leftSpan == 0:
            leftSpan = 1
        rightSpan = rightMax - rightMin
        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value - leftMin) / float(leftSpan)
        # Convert the 0-1 range into a value in the right range.
        return rightMin + (valueScaled * rightSpan)
    #I extract the values from the dictionary
    dict_values = mydict.values()
    #and the max and min
    minvalue = min(dict_values)
    maxvalue = max(dict_values)
    #I define a new dictionary where to put the results
    ret_dic = {}
    #then I remap all the values
    for elem in mydict:
        mapped_val = translate(mydict[elem], minvalue, maxvalue, newrange[0], newrange[1])
        ret_dic[elem] = mapped_val
    return ret_dic


#Alex's function that takes a generated graph and gives you back a graph with groups

def augment_graph_data(data, max_groups):
    
    if len(data["nodes"]) < 50:
        
        return {"fullGraph" :data}
    
    total_nodes = len(data['nodes'])   
    connector_nodes = []

    # checking to see if one node connects to all other nodes, and removing it from consideration
    # will be used as a special "connector node" below
    for i, n in enumerate(data['nodes']):
        links =  [l for l in data['links'] if l['source'] == i or l['target'] == i]
        if len(links) == total_nodes -1:
            connector_nodes.append(n)
            data['nodes'][i]["delete"] = True
            for i2, n2 in enumerate(data['links']):
                if n2["source"] == i or n2["source"] == i:
                    data['links'][i2]["delete"] = True

    data['nodes'] = [n for n in data['nodes'] if not n.get("delete", False)]
    data['links'] = [l for l in data['links'] if not l.get("delete", False)]
    
    #create the networkx graph
    G = nx.Graph()
    for i,x in enumerate(data['nodes']):
        G.add_node(i, nodeName= x["nodeName"], nodeWeight = x["nodeWeight"])

    for i,x in enumerate(data['links']):
        G.add_edge(x["source"], x["target"], weight = x["value"])
   
    all_nodes = G.nodes()
    
    #attach group names to all nodes
    partition = community.best_partition(G)

    for g in G.nodes():
        G.node[g]["group"] = partition[g]

    #with new group info, create the summary group graph
    summary_graph = community.induced_graph(partition, G)

    #enhance the information that will be in the json handed off to d3
    for x in summary_graph.nodes():
        summary_graph.node[x]["size"] = sum([G.node[auth].get("nodeWeight", 0) for auth in G.nodes() if G.node[auth]["group"] == x])
        authors = sorted([G.node[auth] for auth in G.nodes() if G.node[auth]["group"] == x], key = lambda x: x.get("nodeWeight", 0), reverse = True)
        num_names = int(math.ceil(len(authors) /10))
        summary_graph.node[x]["nodeName"] =  [d.get("nodeName", "") for d in authors[:num_names]]
        summary_graph.node[x]["authorCount"] = len(authors)

 #remove all but top n groups from summary graph
    top_nodes = sorted([n for n in summary_graph.nodes(data = True)], key= lambda x : x[1]["size"], reverse = True )[:max_groups]
    top_node_ids = [n[0] for n in top_nodes]
    for group_id in summary_graph.nodes():
        if group_id not in top_node_ids:
            summary_graph.remove_node(group_id);
            
#adding connector nodes
    for c in connector_nodes:
       summary_graph.add_node(c["nodeName"], nodeName = [c["nodeName"]], connector = True, size = None)
       for x in summary_graph.nodes():
           summary_graph.add_edge(c["nodeName"], x)
           
 #remove nodes from full graph that aren't in top group
 #this automatically takes care of edges, too
    for node in G.nodes(data = True):
        if node[1]["group"] not in top_node_ids:
            G.remove_node(node[0])


    final_data = {"summaryGraph" : json_graph.node_link_data(summary_graph), "fullGraph" : json_graph.node_link_data(G) }
        
    
    return final_data


#Giovanni's original author network building function, with data processed by the group function 
#right before it is returned to the user

def get_network_with_groups(authors_lists, max_groups):
    """Function that builds the authors network"""
        
    weight_single_authors = {}
    weight_authors_couples = {}
    
    #for each set of authors of each paper
    for list_auth_in_paper in authors_lists:
        
        #I sort the author name in the list so that I'm sure to have always the same couple of authors
        list_auth_in_paper.sort()
        #I get the weight per author
        auths_paper_weight = _get_author_weight(list_auth_in_paper)
        #then I assign this weight to each author 
        for author in list_auth_in_paper:
            weight_single_authors.setdefault(author, 0)
            weight_single_authors[author] += auths_paper_weight
            
        #if the paper has more authors than allowed I consider it only for the node and not for the links
        if len(list_auth_in_paper) <= max_num_auth_paper:
            #then I assign this weight to each couple of authors
            #then for each couple I assign the value
            for couple in combinations(list_auth_in_paper, 2):
                weight_authors_couples.setdefault(couple, 0);
                weight_authors_couples[couple] += auths_paper_weight
        
    #then I extract all the couples with the total weight
    weight_authors_couples_list = weight_authors_couples.items()
    #and I sort by the member of the connection and then by the weight (the last sorting performed is the first in the result)
    weight_authors_couples_list = sorted(weight_authors_couples_list, key=(lambda coauth: coauth[0]), reverse=False)
    weight_authors_couples_list = sorted(weight_authors_couples_list, key=(lambda coauth: coauth[1]), reverse=True)
    
    #############
    #I cut the number of links to a max value
    chosen_links = weight_authors_couples_list[:max_num_links]
    
    #I extract the list of authors with their weight and I sort the list in desc mode for the weight and asc for the names
    weight_single_authors_list = weight_single_authors.items()
    weight_single_authors_list.sort(key=lambda coauth: coauth[0], reverse=False)
    weight_single_authors_list.sort(key=lambda coauth: coauth[1], reverse=True)
    
    #then I re-convert back the list in a dictionary          
    chosen_links = dict(chosen_links)
   
    #then for each link I calculate the value of the link in a way that can be normalized
    to_use_links = {}
    for couple in chosen_links:
        #I round the weight to the integer after multiplying it to 100
        value_link = int(round(chosen_links[couple] * 100))
        to_use_links[couple] = value_link
    
    #I group the links with the same weight
    num_link_per_weight = {}
    for link in to_use_links:
        num_link_per_weight.setdefault(to_use_links[link], []).append(link)
    
    #I check each group and if it's more than the maximum amount I decided at the beginning I start to select only the links
    #that have the most important nodes in it
    num_link_per_weight_selected = {}
    for weight in num_link_per_weight:
        #if the group is bigger than the maximum allowed I cut it
        if len(num_link_per_weight[weight]) > max_num_links_same_weight:
            max_link_allowed = max_num_links_same_weight
            #I get an author from the top to bottom of the weighted list
            for auth in weight_single_authors_list:
                #for each link of the selected weight
                for link in num_link_per_weight[weight]:
                    #if the author is in the link
                    if auth[0] in link:
                        #I check if the author I am considering has a weight higher than the other in the link
                        #if not it means that I have already selected the link 
                        #(it's not possible that I reach the current author without selecting the link if the other author has a higher weight
                        #simply because I have checked the other author first)
                        
                        #I select which author is the current one and which is the other in the link
                        if link[0] == auth[0]:
                            current_auth = link[0]
                            other_auth = link[1]
                        else:
                            current_auth = link[1]
                            other_auth = link[0]
                        #then I check the weight
                        if weight_single_authors[current_auth] > weight_single_authors[other_auth]:
                            #if the weight of the current is higher than the other I select the link
                            num_link_per_weight_selected.setdefault(weight, []).append(link)
                            max_link_allowed -= 1
                        #if the weight is the same I check the alphabetic order
                        elif weight_single_authors[current_auth] == weight_single_authors[other_auth]:
                            if current_auth < other_auth:
                                num_link_per_weight_selected.setdefault(weight, []).append(link)
                                max_link_allowed -= 1
                    #if I selected the max number of links I stop
                    if max_link_allowed == 0:
                        break
                #if I selected the max number of links I stop
                if max_link_allowed == 0:
                    break
 
        #otherwise I simply copy it
        else:
            num_link_per_weight_selected[weight] = num_link_per_weight[weight]
     
    #then I reconstruct the "to_use_links" dictionary
    to_use_links = {}
    for weight in num_link_per_weight_selected:
        #print weight, len(num_link_per_weight_selected[weight])
        for link in num_link_per_weight_selected[weight]:
            to_use_links[link] = weight
    
    #Than I create a list of the chosen links (again)
    chosen_links = to_use_links.items()
    
    #then for each link I select the nodes to show
    to_use_nodes = {}
    for couple in to_use_links:
        to_use_nodes.setdefault(couple[0], weight_single_authors[couple[0]])
        to_use_nodes.setdefault(couple[1], weight_single_authors[couple[1]])
    
    #then I apply the Histogram equalization to the link weight
    hiseqobj = histeq.HistEq(to_use_links, [1, 40])
    to_use_links_normalized = hiseqobj.hist_eq()
    
    #and I re map the values of the authors in a new range
    to_use_nodes = _remap_dict_in_range(to_use_nodes, [5, 150])
    
    #I extract the list of names in a list, because I need the positions
    listnames = to_use_nodes.keys()
    #then I build the final variables
    nodes = []
    for name in listnames:
        nodes.append({'nodeName':name, 'nodeWeight':to_use_nodes[name]})
    
    #I construct the final links using the auth_links
    links = []
    
    for elems in to_use_links_normalized:
        #links.append({'source':listnames.index(elems[0]), 'target':listnames.index(elems[1]), 'value':fdict[link], 'source_name_ads': elems[0], 'target_name_ads': elems[1]})
        links.append({'source':listnames.index(elems[0]), 'target':listnames.index(elems[1]), 'value':to_use_links_normalized[elems]})
        
    authors = {'nodes': nodes, 'links': links}
        
    return augment_graph_data(authors, max_groups)



def get_data_for_network(q, fq=None, rows=None, start=None):

    d = {
        'q' : q,
        'fq' : fq,
        'rows': rows,
        'start': start,
        'facets': [], 
        'fields': ['author_norm'], 
        'highlights': [], 
        'wt' : 'json'
        
         }
    response = requests.get(config.SOLR_PATH , params = d)
    print response.url
    if response.status_code == 200:
        results = response
        print results
        return results
    else:
        return None


def generate_network(q,fq=None,rows=None,start=None, max_groups=None):

    if not rows or rows > config.MAX_RECORDS:
        rows = config.MAX_RECORDS
    if not start:
        start = config.START
    if not max_groups:
        max_groups = config.MAX_GROUPS

    data = get_data_for_network(q, fq, rows, start)

    if data:
        return get_network_with_groups(data, max_groups)
    else:
        return None
        



