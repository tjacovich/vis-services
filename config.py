SECRET_KEY = 'this should be changed'

SOLR_PATH = 'http://localhost:9000/solr/collection1/select'

TVRH_SOLR_PATH = 'http://localhost:9000/solr/tvrh/'

#This section configures this application to act as a client, for example to query solr via adsws
CLIENT = {
  'TOKEN': 'we will provide an api key token for this application'
}



#word cloud config

WC_MAX_RECORDS = 100
WC_START = 0

#threshold that a word stem has to pass before being included
WC_MIN_PERCENT_WORD = 3

WC_MIN_OCCURRENCES_WORD = 2




#author network config

AN_MAX_RECORDS = 1000
AN_START = 0

#configuration for augmented graph data
AN_MAX_GROUPS = 8


#paper network config

#paper network calculation is kind of slow, so limiting the number of records for now.
PN_MAX_RECORDS = 150
PN_START = 0

#configuration for augmented graph data
PN_MAX_GROUPS = 10


