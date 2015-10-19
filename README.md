[![Build Status](https://travis-ci.org/adsabs/vis-services.svg?branch=master)](https://travis-ci.org/adsabs/vis-services)

# Visualization Endpoints for ADS

### Author Network

This endpoint takes a solr query (q parameter and optionally fq, start, rows, and max_groups) and returns json.
* If there are fewer than 50 nodes, the json structure is simply a graph of author nodes
and their linkages.
* Otherwise two graphs are returned : a "fullGraph" that has all node-link information for the nodes
that were successfully categorized into groups, and a "summaryGraph"
that summarizes the graph into groups.

You can add a max_groups parameter to limit the number of groups returned -- note this isn't taken into account
by the algorithm that generates the groups, it just limits the amount of information you will receive back.



### Paper Network

This endpoint is very similar to the author network, with nodes representing individual papers and links representing references that these nodes have in common.

The implementation is different in that summary groups are titled with word clouds of the titles of the papers that are members of the group, while in the author network the title is just a list of the most common authors.


### Word Cloud

This endpoint takes a solr query (q parameter and optionally fq, start, rows, min_occurrences_word, and min_percent_word) and returns json.
* The json contains term frequency, term inverse document frequency, and total number of documents in which the term occured.
* The words shown represent the most frequent occurence of all words with the given stem.
* If you want to limit the words returned to the most frequent, you have two options:
     1. Set min_occurrences_word to mandate the number of times the word has to have appeared in the search results. (Default is 2)
     2. Set min_percent_word to mandate the minimum percentage of individual documents in which the word has to have appeared (Default is 3, so 3 out of 100 docs)

# Reminder for absentminded people on how to develop locally:
  1. activate virtualenv (assumming it's already there): source env/bin/activate
  2. pip install -r requirements.txt
  3. pip install -r dev-requirements.txt
  4. add your api token to the config.py
  5. Set config variables DEBUG = True and TESTING = True to get informative error messages
  6. python wsgi.py to run the local server
