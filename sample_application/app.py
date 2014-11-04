import os
from flask import Blueprint, Flask
from flask import Flask, g
from views import Resources, UnixTime
from flask.ext.restful import Api

def create_app():
  blueprint = Blueprint(
      'sample_application',
      __name__,
      static_folder=None,
  )
  api = Api(blueprint)
  api.add_resource(Resources, '/resources')
  api.add_resource(UnixTime, '/time')

  app = Flask(__name__, static_folder=None) 
  app.url_map.strict_slashes = False
  app.config.from_object('sample_application.config')
  try:
    app.config.from_object('sample_application.local_config')
  except ImportError:
    pass
  app.register_blueprint(blueprint)
  return app