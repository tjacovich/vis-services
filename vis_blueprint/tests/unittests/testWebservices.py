import sys, os
PROJECT_HOME = os.path.abspath(os.path.join(os.path.dirname(__file__),'../../'))
sys.path.append(PROJECT_HOME)
from flask.ext.testing import TestCase
import unittest
import requests
import json


class TestWebservices(TestCase):
  '''Tests that each route as an http response'''
  
  def create_app(self):
    '''Start the wsgi application'''
    from app import create_app
    return create_app()

  def test_word_cloud_resource(self):
    r = self.client.get('/word-cloud/?q=author:accomazzi,a')
    self.assertEqual(r.status_code,500)


  def test_author_network_resource(self):
    r = self.client.get('/author-network/?q=author:accomazzi,a')
    self.assertEqual(r.status_code, 500)


  def test_nonSpecificUrlRoutes(self):
    '''Iterates over each non specific (ie, one that doesn't require an argument) route 
    in app, testing for http response code < 500'''
    for rule in self.app.url_map.iter_rules():
      if not rule.arguments: #only test routes that do not require arguments.
        url = url_for(rule.endpoint)
        r = self.client.get(url)
        self.assertTrue(r.status_code < 500)

  def test_ResourcesRoute(self):
    '''Tests for the existence of a /resources route, and that it returns properly formatted JSON data'''
    r = self.client.get('/resources')
    self.assertEqual(r.status_code,200)
    [self.assertIsInstance(k, basestring) for k in r.json] #Assert each key is a string-type

    for expected_field, _type in {'scopes':list,'methods':list,'description':basestring}.iteritems():
      [self.assertIn(expected_field,v) for v in r.json.values()] #Assert each resource is described has the expected_field
      [self.assertIsInstance(v[expected_field],_type) for v in r.json.values()] #Assert every expected_field has the proper type




if __name__ == '__main__':
  unittest.main()