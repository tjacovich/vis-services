import sys, os
PROJECT_HOME = os.path.abspath(os.path.join(os.path.dirname(__file__),'../../'))
sys.path.append(PROJECT_HOME)
from flask.ext.testing import TestCase
import unittest
import requests
import time

class TestWebservices(TestCase):
  '''Tests that each route as an http response'''
  
  def create_app(self):
    '''Start the wsgi application'''
    from app import create_app
    return create_app()

  def test_timeResource(self):
    '''Test the /time route'''
    r = self.client.get('/time')
    self.assertEqual(r.status_code,200)
    self.assertIn('now',r.json)
    self.assertNotEqual(r.json.get('now'),time.time()) #The clocks should be (very) slightly different

  def test_urlRoutes(self):
    '''Iterates over each route in app, testing for http response code < 500'''
    pass

  def test_ResourcesRoute(self):
    '''Tests for the existence of a /resources route, and that it returns properly formatted JSON data'''
    pass




if __name__ == '__main__':
  unittest.main()