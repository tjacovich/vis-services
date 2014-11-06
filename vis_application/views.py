from flask import current_app, Blueprint, jsonify, request
from flask.ext.restful import Resource
from lib import word_cloud
from lib import author_network
import config

blueprint = Blueprint(
	'visualization',
	__name__,
	static_folder=None,
)

#function to help passing flask parameters to solr query
def ensure_int_variable(val, default):
	if val:
		return int(val)
	else:
		return default


class WordCloud(Resource):
  '''Returns collated tf/idf data for a solr query'''
  scopes = [] 

  def get(self):

	try:
	  q = request.args["q"]
	except KeyError:
	  return {'Error' : 'No query parameter was provided'}, 400

	fq = request.args.get("fq", None)

	rows = request.args.get("rows", None)
	if rows:
	  rows = int(rows)
	if not rows or rows > config.MAX_RECORDS:
		rows = config.MAX_RECORDS

	start = request.args.get("start", None)
	start = ensure_int_variable(start, config.START)

	min_percent_word = request.args.get("min_percent_word", None)
	min_percent_word = ensure_int_variable(min_percent_word, config.MIN_PERCENT_WORD)

	min_occurences_word = request.args.get("min_occurrences_word", None)
	min_occurences_word = ensure_int_variable(min_occurences_word, config.MIN_OCCURENCES_WORD)

	d = {
		'q' : q,
		'fq' : fq,
		'rows': rows,
		'start': start,
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

	response = current_app.client.session.get(config.TVRH_SOLR_PATH , params = d)
	
	if response.status_code == 200:
		data = response.json()
	else:
		return {"Error": "There was a connection error. Please try again later"}, 400

	if data:
		word_cloud_json = word_cloud.generate_wordcloud(data, min_percent_word=min_percent_word, min_occurences_word=min_occurences_word)

	return word_cloud_json, 200

class AuthorNetwork(Resource):
  '''Returns author network data for a solr query'''
  scopes = [] 

  def get(self):

	try:
		q= request.args["q"]
	except KeyError:
		return {'Error' : 'No query parameter was provided'}, 400

	#assign all query parameters and config variabls

	fq = request.args.get("fq", None)

	rows = request.args.get("rows", None)
	if rows:
		rows = int(rows)
	if not rows or rows > config.MAX_RECORDS:
		rows = config.MAX_RECORDS

	start = request.args.get("start", None)
	start = ensure_int_variable(start, config.START)

	max_groups = request.args.get("max_groups", None)
	max_groups = ensure_int_variable(max_groups, config.MAX_GROUPS)


	#request data from solr

	d = {
		'q' : q,
		'fq' : fq,
		'rows': rows,
		'start': start,
		'facets': [], 
		'fl': 'author_norm', 
		'highlights': [], 
		'wt' : 'json'
		}

	response = current_app.client.session.get(config.SOLR_PATH , params = d)
	if response.status_code == 200:
		data = response.json()
	else:
		return {"Error": "There was a connection error. Please try again later"}, 400

	if data:
		#get_network_with_groups expects a list of normalized authors
		data = [d.get("author_norm", []) for d in data["response"]["docs"]]
		author_network_json = author_network.get_network_with_groups(data, max_groups)

		return author_network_json, 200





