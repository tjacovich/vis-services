import sys, os
import unittest
import json
from collections import defaultdict
PROJECT_HOME = os.path.abspath(os.path.join(os.path.dirname(__file__),'../../'))
sys.path.append(PROJECT_HOME)
from lib import author_network, word_cloud, paper_network, tf_idf


#input data

# has fewer than 50 nodes
input_js_author_network_small = json.load(open(PROJECT_HOME + "/tests/test_input/author_network_before_groups_func_small.json"))
input_js_data_parameter = json.load(open(PROJECT_HOME + "/tests/test_input/author_network_second_parameter.json"))
input_js_paper_network = json.load(open(PROJECT_HOME + "/tests/test_input/paper_network_before_groups_func_large.json"))


#result data

test_js_author_network = json.load(open(PROJECT_HOME + "/tests/test_output/author_network_accomazzi,a.json"))
test_js_author_network_max_groups = json.load(open(PROJECT_HOME + "/tests/test_output/author_network_accomazzi,a_max_groups_3.json"))
test_js_author_network_alberto = json.load(open(PROJECT_HOME + "/tests/test_input/kurtz_query.json"))

class TestEndpointLogic(unittest.TestCase):

    def test_word_cloud_resource(self):
        text1 = u"This is a sentence. And this is another sentence (although less important). I bought a car at http://www.car.com."
        text2 = u"Testing is good! href='#three' 2.3e2 + 4 = $\\alpha$"
        records = [text1, text2]
        word_cloud_json = word_cloud.generate_wordcloud(records, n_most_common = 100, n_threads = 2, accepted_pos = (u'NN', u'NNP', u'NNS', u'NNPS',))
        expected_word_cloud_json = {u'car': {'idf': 0.3010299956639812,
                                      'record_count': 1,
                                      'total_occurrences': 1},
                                     u'sentence': {'idf': 0.22184874961635634,
                                      'record_count': 2,
                                      'total_occurrences': 1},
                                     u'testing': {'idf': 0.3010299956639812,
                                      'record_count': 1,
                                      'total_occurrences': 1}}
        self.assertEqual(word_cloud_json, expected_word_cloud_json)


    def test_author_network_resource(self):

        #current default
        max_groups = 8
        self.maxDiff = None


        #testing group aggregation function
        #if it receives fewer than 50 nodes, it should just return the graph in the form {fullgraph : graph}

        processed_data_small = author_network.augment_graph_data(input_js_author_network_small, input_js_data_parameter)

        self.assertNotIn("summaryGraph", processed_data_small)

        # otherwise, it should return json containing three items :
        # bibcode_dict, root (d3 structured data), and link_data

        input_js_author_network = json.load(open(PROJECT_HOME + "/tests/test_input/author_network_before_groups_func_large.json"))

        processed_data = author_network.augment_graph_data(input_js_author_network, input_js_data_parameter)

        self.assertTrue("bibcode_dict" in processed_data)
        self.assertTrue("root" in processed_data)
        self.assertTrue("link_data" in processed_data)

        # testing entire function

        input_js_author_network = json.load(open(PROJECT_HOME + "/tests/test_input/author_network_before_groups_func_large.json"))

        processed_data = json.loads(json.dumps(author_network.augment_graph_data(input_js_author_network, input_js_data_parameter), sort_keys=True))
        self.assertEqual(processed_data, test_js_author_network)



    def test_paper_network_resource(self):

        #first, test the tf-idf library

        self.maxDiff = None

        input_js_tf_idf = json.load(open(PROJECT_HOME + "/tests/test_input/tf_idf_input.json"))

        test_js_tf_idf = json.load(open(PROJECT_HOME + "/tests/test_output/tf_idf_output.json"))

        processed_data = json.loads(json.dumps(tf_idf.get_tf_idf_vals(input_js_tf_idf), sort_keys=True))

        self.assertEqual(processed_data, test_js_tf_idf)

        #now test reference counting function

        processed_data = json.loads(json.dumps(paper_network.get_papernetwork(input_js_paper_network["response"]["docs"], 10), sort_keys=True))

        topCommonReferences = processed_data["summaryGraph"]["nodes"][0]["top_common_references"].items().sort()

        def get_group_references(group):
            indexes =[i for i,n in enumerate(processed_data["fullGraph"]["nodes"]) if n["group"] == group]
            links =[l for l in processed_data["fullGraph"]["links"] if l["source"] in indexes and l["target"] in indexes]
            freq_dict = defaultdict(list)
            for l in links:
                for o in l["overlap"]:
                    freq_dict[o].extend([l["source"], l["target"]])

            for f in freq_dict:
                freq_dict[f] = len(list(set(freq_dict[f])))

            final = sorted(freq_dict.items(), key=lambda x:x[1], reverse=True)[:5]

            num_papers = processed_data["summaryGraph"]["nodes"][0]["paper_count"]

            final = [(f[0], f[1]/float(num_papers)) for f in final].sort()
            return final

        self.assertEqual(topCommonReferences, get_group_references(0))

        # now just test input/output

        test_js_paper_network =  json.load(open(PROJECT_HOME + "/tests/test_output/paper_network_star.json"))

        processed_data = json.loads(json.dumps(paper_network.get_papernetwork(input_js_paper_network["response"]["docs"], 10), sort_keys=True))
        self.assertEqual(processed_data, test_js_paper_network)
