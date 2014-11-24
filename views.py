from flask import current_app, Blueprint, jsonify, request
from flask.ext.restful import Resource, reqparse
from lib import word_cloud
from lib import author_network
from lib import paper_network



blueprint = Blueprint(
    'visualization',
    __name__,
    static_folder=None,
)

#This resource must be available for every adsabs webservice.
class Resources(Resource):
  '''Overview of available resources'''
  scopes = [] 
  def get(self):
    func_list = {}
    for rule in current_app.url_map.iter_rules():
      methods = current_app.view_functions[rule.endpoint].methods
      scopes = current_app.view_functions[rule.endpoint].view_class.scopes
      description = current_app.view_functions[rule.endpoint].view_class.__doc__
      func_list[rule.rule] = {'methods':methods,'scopes': scopes,'description': description}
    return func_list, 200



class WordCloud(Resource):
  '''Returns collated tf/idf data for a solr query'''
  scopes = [] 

  def get(self):

    parser = reqparse.RequestParser()
    parser.add_argument('q', type=str, required=True)
    parser.add_argument('fq', type=str)
    parser.add_argument('start', type=int, default = current_app.config.get("WC_START"))
    parser.add_argument('rows', type=int, default = current_app.config.get("WC_MAX_RECORDS"))
    parser.add_argument('min_percent_word', type=int, default = current_app.config.get("WC_MIN_PERCENT_WORD"))
    parser.add_argument('min_occurrences_word', type=int, default = current_app.config.get("WC_MIN_OCCURRENCES_WORD"))
    args = parser.parse_args()


    d = {
        'q' : args.get("q"),
        'fq' : args.get("fq"),
        'rows':  min(args.get("rows"), current_app.config.get("WC_MAX_RECORDS")),
        'start': args.get("start"),
        'facets': [], 
        'highlights': [],
        #fields parameter is necessary for tvrh query
        'fields': ['id'],
        'defType':'aqp', 
        'tv.tf_idf': 'true', 
        'tv.tf': 'true', 
        'tv.positions':'false',
        'tf.offsets':'false',
        'tv.fl':'abstract,title',
        'fl':'id,abstract,title',
        'wt': 'json',   
         }

    response = current_app.client.session.get(current_app.config.get("TVRH_SOLR_PATH") , params = d)
    
    if response.status_code == 200:
        data = response.json()
    else:
        return {"Error": "There was a connection error. Please try again later"}, response.status_code

    if data:
        word_cloud_json = word_cloud.generate_wordcloud(data, min_percent_word=args.get("min_percent_word"), min_occurrences_word=args.get("min_occurrences_word"))
    if word_cloud_json:
        return word_cloud_json, 200
    else:
        return {"Error": "Empty word cloud. Try changing your minimum word parameters or expanding your query."}

class AuthorNetwork(Resource):
  '''Returns author network data for a solr query'''
  scopes = [] 

  def get(self):

    parser = reqparse.RequestParser()
    parser.add_argument('q', type=str, required=True)
    parser.add_argument('fq', type=str)
    parser.add_argument('start', type=int, default = current_app.config.get("AN_START"))
    parser.add_argument('rows', type=int, default = current_app.config.get("AN_MAX_RECORDS"))
    parser.add_argument('max_groups', type=int, default = current_app.config.get("AN_MAX_GROUPS"))
    args = parser.parse_args()


    #request data from solr
    d = {
        'q' : args.get("q"),
        'fq' : args.get("fq"),
        'rows': min(args.get("rows"), current_app.config.get("AN_MAX_RECORDS")),
        'start': args.get("start"),
        'facets': [], 
        'fl': 'author_norm', 
        'highlights': [], 
        'wt' : 'json'
        }


    response = current_app.client.session.get(current_app.config.get("SOLR_PATH") , params = d)

    if response.status_code == 200:
      data = response.json()
    else:
      return {"Error": "There was a connection error. Please try again later"}, response.status_code

    #get_network_with_groups expects a list of normalized authors
    data = [d.get("author_norm", []) for d in data["response"]["docs"]]
    author_network_json = author_network.get_network_with_groups(data, args.get("max_groups"))

    if author_network_json:
      return author_network_json, 200
    else:
      return {"Error": "Empty network."}


class PaperNetwork(Resource):
  '''Returns paper network data for a solr query'''
  scopes = [] 

  def get(self):

    parser = reqparse.RequestParser()
    parser.add_argument('q', type=str, required=True)
    parser.add_argument('fq', type=str)
    parser.add_argument('start', type=int, default = current_app.config.get("PN_START"))
    parser.add_argument('rows', type=int, default = current_app.config.get("PN_MAX_RECORDS"))
    parser.add_argument('max_groups', type=int, default = current_app.config.get("PN_MAX_GROUPS"))
    args = parser.parse_args()


    #request data from solr
    d = {
        'q' : args.get("q"),
        'fq' : args.get("fq"),
        'rows': min(args.get("rows"), current_app.config.get("PN_MAX_RECORDS")),
        'start': args.get("start"),
        'facets': [], 
        'fl': ['bibcode,title,first_author,year,citation_count,read_count,reference'], 
        'highlights': [], 
        'wt' : 'json'
        }

    response = current_app.client.session.get(current_app.config.get("SOLR_PATH") , params = d)

    print response.url

    if response.status_code == 200:
      data = response.json()
    else:
      return {"Error": "There was a connection error. Please try again later"}, response.status_code

    #get_network_with_groups expects a list of normalized authors
    data = data["response"]["docs"]
    author_network_json = paper_network.get_papernetwork(data, args.get("max_groups"))

    if author_network_json:
      return author_network_json, 200
    else:
      return {"Error": "Empty network."}





