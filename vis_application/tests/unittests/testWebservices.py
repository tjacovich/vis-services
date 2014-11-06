import sys, os
PROJECT_HOME = os.path.abspath(os.path.join(os.path.dirname(__file__),'../../'))
sys.path.append(PROJECT_HOME)
from flask.ext.testing import TestCase
import unittest
import requests
import json


test_js_word_cloud = json.load(open("test_data/word_cloud_accomazzi,a.json"))
test_json_word_cloud_min_occurences = json.load(open("test_data/word_cloud_accomazzi,a_min_occurrence_word_5.json"))

test_js_author_network = json.load(open("test_data/author_network_accomazzi,a.json"))
test_js_author_network_max_groups = json.load(open("test_data/author_network_accomazzi,a_max_groups_3.json"))

class TestWebservices(TestCase):
  '''Tests that each route as an http response'''
  
  def create_app(self):
    '''Start the wsgi application'''
    from app import create_app
    return create_app()

  def test_word_cloud(self):
    r = self.client.get('/word-cloud/?q=author:accomazzi,a')
    self.assertEqual(r.status_code,200)
    self.assertEqual(r.json, test_js_word_cloud)

    r = self.client.get('/word-cloud/?q=author:accomazzi,a&min_occurrences_word=5')
    self.assertEqual(r.status_code,200)
    self.assertEqual(r.json, test_json_word_cloud_min_occurences)



  def test_author_network(self):
    r = self.client.get('/author-network/?q=author:accomazzi,a')
    self.assertEqual(r.status_code,200)
    self.assertEqual(r.json, test_js_author_network)

    r = self.client.get('/author-network/?q=author:accomazzi,a&max_groups=3')
    self.assertEqual(r.status_code,200)
    self.assertEqual(r.json, test_js_author_network_max_groups)



if __name__ == '__main__':
  unittest.main()