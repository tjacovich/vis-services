from flask import current_app, Blueprint, jsonify, request
from flask.ext.restful import Resource
import word_cloud
import author_network

blueprint = Blueprint(
    'visualization',
    __name__,
    static_folder=None,
)



class WordCloud(Resource):
  '''Returns collated tf/idf data for a solr query'''
  scopes = [] 
  def get(self):

    try:
      query = request.args["q"]
    except KeyError:
      return {'Error' : 'No query parameter was provided'}, 400

    fq = request.args.get("fq", None)
    rows = request.args.get("rows", None)
    start = request.args.get("start", None)
    min_percent_word = request.args.get("min_percent_word", None)
    min_occurences_word = request.args.get("min_occurences_word", None)

    word_cloud_json = word_cloud.generate_wordcloud(q = query, fq=fq, rows=rows,start=None, min_percent_word=min_percent_word, min_occurences_word=min_occurences_word)
    return word_cloud_json, 200


class AuthorNetwork(Resource):
  '''Returns author network data for a solr query'''
  scopes = [] 
  def get(self):

    try:
      query = request.args["q"]
    except KeyError:
      return {'Error' : 'No query parameter was provided'}, 400

    fq = request.args.get("fq", None)
    rows = request.args.get("rows", None)
    start = request.args.get("start", None)
    max_groups = request.args.get("max_groups", None)

    author_network_json = author_network.generate_network(q = query, fq=fq, rows=rows,start=None, max_groups = max_groups)
    return author_network_json, 200



