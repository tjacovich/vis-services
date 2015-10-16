from flask import current_app, request
from flask.ext.restful import Resource, reqparse
from flask.ext.discoverer import advertise
from lib import word_cloud
from lib import author_network
from lib import paper_network
from client import client


class WordCloud(Resource):
  '''Returns collated tf/idf data for a solr query'''
  decorators = [advertise('scopes', 'rate_limit')]
  scopes = []
  rate_limit = [500,60*60*24]

  def post(self):

    solr_args = request.json
    if 'max_groups' in solr_args:
        del solr_args['min_percent_word']
    if 'min_occurrences_word' in solr_args:
        del solr_args['min_occurrences_word']

    solr_args["rows"] = min(int(solr_args.get("rows", [current_app.config.get("VIS_SERVICE_WC_MAX_RECORDS")])[0]), current_app.config.get("VIS_SERVICE_WC_MAX_RECORDS"))
    solr_args['fields'] = ['id']
    solr_args['defType'] = 'aqp'
    solr_args['tv'] = 'true'
    solr_args['tv.tf_idf'] = 'true'
    solr_args['tv.tf'] = 'true'
    solr_args['tv.positions'] ='false'
    solr_args['tf.offsets'] = 'false'
    solr_args['tv.fl'] ='abstract,title'
    solr_args['fl'] ='id,abstract,title'
    solr_args['wt'] = 'json'

    headers = {'X-Forwarded-Authorization' : request.headers.get('Authorization')}

    response = client().get(current_app.config.get("VIS_SERVICE_TVRH_PATH") , params = solr_args, headers=headers)

    if response.status_code == 200:
        data = response.json()
    else:
        return {"Error": "There was a connection error. Please try again later", "Error Info": response.text}, response.status_code

    if data:
        min_percent_word = request.args.get("min_percent_word", current_app.config.get("VIS_SERVICE_WC_MIN_PERCENT_WORD"))
        min_occurrences_word = request.args.get("min_occurrences_word", current_app.config.get("VIS_SERVICE_WC_MIN_OCCURRENCES_WORD"))

        word_cloud_json = word_cloud.generate_wordcloud(data, min_percent_word = min_percent_word, min_occurrences_word = min_occurrences_word)
    if word_cloud_json:
        return word_cloud_json, 200
    else:
        return {"Error": "Empty word cloud. Try changing your minimum word parameters or expanding your query."}, 200

class AuthorNetwork(Resource):
  '''Returns author network data for a solr query'''
  decorators = [advertise('scopes', 'rate_limit')]
  scopes = []
  rate_limit = [500,60*60*24]

  def post(self):

    solr_args = request.json

    solr_args["rows"] = min(int(solr_args.get("rows", [current_app.config.get("VIS_SERVICE_AN_MAX_RECORDS")])[0]), current_app.config.get("VIS_SERVICE_AN_MAX_RECORDS"))
    solr_args['fl'] = ['author_norm', 'title', 'citation_count', 'read_count','bibcode', 'pubdate']
    solr_args['wt'] ='json'

    headers = {'X-Forwarded-Authorization' : request.headers.get('Authorization')}

    response = client().get(current_app.config.get("VIS_SERVICE_SOLR_PATH") , params = solr_args, headers=headers)

    if response.status_code == 200:
      full_response = response.json()
    else:
      return {"Error": "There was a connection error. Please try again later", "Error Info": response.text}, response.status_code

    #get_network_with_groups expects a list of normalized authors
    author_norm = [d.get("author_norm", []) for d in full_response["response"]["docs"]]
    author_network_json = author_network.get_network_with_groups(author_norm, full_response["response"]["docs"])

    if author_network_json:
      return {"msg" : {"numFound" : full_response["response"]["numFound"],
       "start": full_response["response"].get("start", 0),
        "rows": int(full_response["responseHeader"]["params"]["rows"])
       }, "data" : author_network_json}, 200
    else:
      return {"Error": "Empty network."}, 200


class PaperNetwork(Resource):
  '''Returns paper network data for a solr query'''
  decorators = [advertise('scopes', 'rate_limit')]
  scopes = []
  rate_limit = [500,60*60*24]

  def post(self):

    solr_args = dict(request.json)
    if 'max_groups' in solr_args:
        del solr_args['max_groups']

    solr_args["rows"] = min(int(solr_args.get("rows", [current_app.config.get("VIS_SERVICE_PN_MAX_RECORDS")])[0]), current_app.config.get("VIS_SERVICE_PN_MAX_RECORDS"))

    solr_args['fl'] = ['bibcode,title,first_author,year,citation_count,read_count,reference']
    solr_args['wt'] ='json'

    headers = {'X-Forwarded-Authorization' : request.headers.get('Authorization')}

    response = client().get(current_app.config.get("VIS_SERVICE_SOLR_PATH") , params = solr_args, headers=headers)

    if response.status_code == 200:
      full_response = response.json()

    else:
      return {"Error": "There was a connection error. Please try again later", "Error Info": response.text}, response.status_code

    #get_network_with_groups expects a list of normalized authors
    data = full_response["response"]["docs"]
    paper_network_json = paper_network.get_papernetwork(data, request.args.get("max_groups", current_app.config.get("VIS_SERVICE_PN_MAX_GROUPS")))
    if paper_network_json:
      return {"msg" : {"numFound" : full_response["response"]["numFound"],
       "start": full_response["response"].get("start", 0),
        "rows": int(full_response["responseHeader"]["params"]["rows"])
       }, "data" : paper_network_json}, 200
    else:
      return {"Error": "Empty network."}, 200
