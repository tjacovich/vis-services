# Visualization Endpoints for ADS

### Author Network

This endpoint takes a solr query (q parameter and optionally fq, start, and rows) and returns
a json structures.
* If there are fewer than 50 nodes, the json structure is simply a graph of author nodes
and their linkages. 
* Otherwise two graphs are returned : a "fullGraph" that has all node-link information for the nodes
that were successfully categorized into groups, and a "summaryGraph"
that summarizes the graph into groups.

You can add a max_groups parameter to limit the number of groups returned -- note this isn't taken into account
by the algorithm that generates the groups, it just limits the amount of information you will receive back.




### Word Cloud

This endpoint takes a solr query (q parameter and optionally fq, start, and rows) and returns
a json structures.
* If there are fewer than 50 nodes, the json structure is simply a graph of author nodes
and their linkages. 
* Otherwise two graphs are returned : a "fullGraph" that has all node-link information, and a "summaryGraph"
that summarizes the graph into groups
