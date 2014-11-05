from flask import current_app, Blueprint
from flask.ext.restful import Resource
import time

blueprint = Blueprint(
    'sample_application',
    __name__,
    static_folder=None,
)

#This resource must be available for every adsabs webservice.
class Resources(Resource):
  '''Overview of available resources'''
  scopes = ['oauth:sample_application:read','oauth:sample_application:logged_in'] 
  def get(self):
    func_list = {}
    for rule in current_app.url_map.iter_rules():
      methods = current_app.view_functions[rule.endpoint].methods
      scopes = current_app.view_functions[rule.endpoint].view_class.scopes
      description = current_app.view_functions[rule.endpoint].view_class.__doc__
      func_list[rule.rule] = {'methods':methods,'scopes': scopes,'description': description}
    return func_list, 200

class UnixTime(Resource):
  '''Returns the unix timestamp of the server'''
  scopes = ['oauth:sample_application:read','oauth:sample_application:logged_in'] 
  def get(self):
    return {'now': time.time()}, 200

class PrintArg(Resource):
  '''Returns the :arg in the route'''
  scopes = ['oauth:sample_application:read','oauth:sample_application:logged_in'] 
  def get(self,arg):
    return {'arg':arg}, 200

class ExampleApiUsage(Resource):
  '''This resource uses the app.client.session.get() method to access an api that requires an oauth2 token, such as our own adsws'''
  scopes = ['oauth:sample_application:read','oauth:sample_application:logged_in','oauth:api:search'] 
  def get(self):
    r = current_app.client.session.get('http://api.adslabs.org/v1/search')
    try:
      r = r.json()
      return {'response':r, 'api-token-which-should-be-kept-secret':current_app.client.token}, 200
    except: #For the moment, 401s are not JSON encoded; this will be changed in the future
      r = r.text
      return {'raw_response':r, 'api-token-which-should-be-kept-secret':current_app.client.token}, 501