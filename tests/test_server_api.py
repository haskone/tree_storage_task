import json
import unittest
import tree_storage.server_api as api_app
from unittest.mock import patch


class TestApi(unittest.TestCase):

    def setUp(self):
        api_app.app.config['TESTING'] = True
        self.app = api_app.app.test_client()

    @patch('tree_storage.storage.Storage.add_nodes')
    def test_add_nodes_ok(self, add_nodes_mock):
        response = self.app.post(
            '/nodes',
            data=json.dumps({"nodes": [{"id": "123", "parent": "321"}]}),
            content_type='application/json')

        add_nodes_mock.assert_called_with('123', '321')
        self.assertEqual(201, response.status_code)
        self.assertEqual('application/json', response.mimetype)

    @patch('tree_storage.storage.Storage.is_loop')
    def test_add_nodes_loop(self, is_loop_mock):
        is_loop_mock.return_value = True
        response = self.app.post(
            '/nodes',
            data=json.dumps({"nodes": [{"id": "123", "parent": "321"},
                                       {"id": "321", "parent": "123"}]}),
            content_type='application/json')

        is_loop_mock.assert_called_with([{'id': '123', 'parent': '321'},
                                         {'id': '321', 'parent': '123'}])
        self.assertEqual(400, response.status_code)
        self.assertEqual('application/json', response.mimetype)

    @patch('tree_storage.storage.Storage.get_trees')
    def test_get_trees(self, get_trees_mock):
        get_trees_mock.return_value = [['1', '2', '3']]
        response = self.app.get('/trees/2')

        get_trees_mock.assert_called_with(node_id='2')
        self.assertEqual(200, response.status_code)
        self.assertEqual('application/json', response.mimetype)
        self.assertEqual(json.dumps({"trees": [["1", "2", "3"]]}),
                         response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()
