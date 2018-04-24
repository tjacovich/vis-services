[![Waffle.io - Columns and their card count](https://badge.waffle.io/adsabs/vis-services.svg?columns=all)](https://waffle.io/adsabs/vis-services)
[![Build Status](https://travis-ci.org/adsabs/vis-services.svg?branch=master)](https://travis-ci.org/adsabs/vis-services)
[![Coverage Status](https://coveralls.io/repos/adsabs/vis-services/badge.svg)](https://coveralls.io/r/adsabs/vis-services)
[![Code Climate](https://codeclimate.com/github/adsabs/vis-services/badges/gpa.svg)](https://codeclimate.com/github/adsabs/vis-services)
[![Issue Count](https://codeclimate.com/github/adsabs/vis-services/badges/issue_count.svg)](https://codeclimate.com/github/adsabs/vis-services)

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

This endpoint takes a solr query (q parameter and optionally fq, start, rows) and returns json.
* The json contains term frequency, term inverse document frequency, and total number of documents in which the term occurred.
* The words shown represent the most frequent occurrence of all words with the given lemma.

# Reminder for absentminded people on how to develop locally:
  1. activate virtualenv (assumming it's already there): source env/bin/activate
  2. pip install -r requirements.txt
  3. pip install -r dev-requirements.txt
  4. python -m spacy download en # Downloads en_core_web_sm by default
  5. add your api token to the config.py
  6. Set config variables DEBUG = True and TESTING = True to get informative error messages
  7. python wsgi.py to run the local server
