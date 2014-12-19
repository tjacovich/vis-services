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

    solr_args = {k : v for k, v in request.args.items() if k not in ["min_percent_word", "min_occurrences_word"]}
    solr_args["rows"] = min(solr_args.get("rows", current_app.config.get("WC_MAX_RECORDS")), current_app.config.get("WC_MAX_RECORDS"))

    solr_args['fields'] = ['id']
    solr_args['defType'] = 'aqp'
    solr_args['tv.tf_idf'] = 'true'
    solr_args['tv.tf'] = 'true'
    solr_args['tv.positions'] ='false'
    solr_args['tf.offsets'] = 'false'
    solr_args['tv.fl'] ='abstract,title'
    solr_args['fl'] ='id,abstract,title'
    solr_args['wt'] = 'json' 

    response = current_app.client.session.get(current_app.config.get("TVRH_SOLR_PATH") , params = solr_args)
    
    if response.status_code == 200:
        data = response.json()
    else:
        return {"Error": "There was a connection error. Please try again later", "Error Info": response.text}, response.status_code

    if data:

        min_percent_word = request.args.get("min_percent_word", current_app.config.get("WC_MIN_PERCENT_WORD"))
        min_occurrences_word = request.args.get("min_occurrences_word", current_app.config.get("WC_MIN_OCCURRENCES_WORD"))

        word_cloud_json = word_cloud.generate_wordcloud(data, min_percent_word = min_percent_word, min_occurrences_word = min_occurrences_word)
    if word_cloud_json:
        return word_cloud_json, 200
    else:
        return {"Error": "Empty word cloud. Try changing your minimum word parameters or expanding your query."}

class AuthorNetwork(Resource):
  '''Returns author network data for a solr query'''
  scopes = [] 

  def get(self):

    solr_args = {k : v for k,v in request.args.items() if k != "max_groups"}

    solr_args["rows"] = min(solr_args.get("rows", current_app.config.get("AN_MAX_RECORDS")), current_app.config.get("AN_MAX_RECORDS"))

    solr_args['fl'] = ['author_norm']
    solr_args['wt'] ='json'

    response = current_app.client.session.get(current_app.config.get("SOLR_PATH") , params = solr_args)

    if response.status_code == 200:
      data = response.json()
    else:
      return {"Error": "There was a connection error. Please try again later", "Error Info": response.text}, response.status_code

    #get_network_with_groups expects a list of normalized authors
    data = [d.get("author_norm", []) for d in data["response"]["docs"]]
    author_network_json = author_network.get_network_with_groups(data, request.args.get("max_groups", current_app.config.get("AN_MAX_GROUPS")))

    if author_network_json:
      return author_network_json, 200
    else:
      return {"Error": "Empty network."}


class PaperNetwork(Resource):
  '''Returns paper network data for a solr query'''
  scopes = [] 

  def get(self):

    solr_args = {k : v for k,v in request.args.items() if k != "max_groups"}
    solr_args["rows"] = min(solr_args.get("rows", current_app.config.get("PN_MAX_RECORDS")), current_app.config.get("PN_MAX_RECORDS"))

    solr_args['fl'] = ['bibcode,title,first_author,year,citation_count,read_count,reference']
    solr_args['wt'] ='json'

    response = current_app.client.session.get(current_app.config.get("SOLR_PATH") , params = solr_args)

    if response.status_code == 200:
      data = response.json()
    else:
      return {"Error": "There was a connection error. Please try again later", "Error Info": response.text}, response.status_code

    #get_network_with_groups expects a list of normalized authors
    data = data["response"]["docs"]
    author_network_json = paper_network.get_papernetwork(data, request.args.get("max_groups", current_app.config.get("AN_MAX_GROUPS")))

    if author_network_json:
      return author_network_json, 200
    else:
      return {"Error": "Empty network."}





