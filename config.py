SECRET_KEY = 'this should be changed'

SOLR_PATH = 'http://api.adslabs.org/v1/'

TVRH_SOLR_PATH = 'http://localhost:9000/solr/tvrh/'

#This section configures this application to act as a client, for example to query solr via adsws
CLIENT = {
  'TOKEN': 'we will provide an api key token for this application'
}



#word cloud config

MAX_RECORDS = 500
START = 0

#threshold that a word stem has to pass before being included
MIN_PERCENT_WORD = 3

MIN_OCCURRENCES_WORD = 2




#author network config

MAX_RECORDS = 1000
START = 0

#configuration for augmented graph data
MAX_GROUPS = 8


