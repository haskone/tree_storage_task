import unittest
from sqlalchemy.ext.declarative import declarative_base
from tree_storage.storage import Storage
from tree_storage.model import Node

Base = declarative_base()


class TestStorage(unittest.TestCase):

    def setUp(self):
        self.storage = Storage(db_url='sqlite:///:memory:')

    def tearDown(self):
        Base.metadata.drop_all(self.storage.engine)

    def add_nodes(self, nodes):
        # some kind of wrapper over add_nodes for the sake
        # of simplify test_add_nodes*
        result = []
        for node_id, parent_id in nodes:
            self.storage.add_nodes(node_id=node_id, parent_id=parent_id)
        for node_id in sorted(set([node_id for node_id, _ in nodes])):
            result_node = self.storage.session.query(Node).filter(Node.node_id == node_id).one()
            result.append((result_node.node_id, result_node.parent_id))
        return result

    def test_add_nodes_simple(self):
        # id, parent
        nodes = [('0', '1'),
                 ('1', '2'),
                 ('3', '4'),
                 ('4', '5')]
        self.assertEqual(nodes, self.add_nodes(nodes))

    def test_add_nodes_update(self):
        # id, parent
        nodes = [('1', '2'),
                 ('1', '3'),
                 ('2', '4'),
                 ('2', '5'),
                 ('1', '6')]
        expected = [('1', '6'),
                    ('2', '5')]
        self.assertEqual(expected, self.add_nodes(nodes))

    def test_get_trees_id_based(self):
        nodes = [('10', '0'),
                 ('20', '10')]
        expected = [['0', '10', '20']]
        # TODO: yeah, need to rewrite with native methods, not with *storage
        # here and below
        self.add_nodes(nodes)

        result = self.storage.get_trees(node_id='20')
        self.assertEqual(expected, result)

    def test_get_trees_parent_based(self):
        nodes = [('10', '0'),
                 ('20', '10')]
        expected = [['0', '10', '20']]
        self.add_nodes(nodes)

        result = self.storage.get_trees(node_id='0')
        self.assertEqual(expected, result)

    def test_is_loop_false(self):
        nodes = [('10', '0')]
        self.add_nodes(nodes)

        input_node = [{'id': '20', 'parent': '10'}]
        self.assertFalse(self.storage.is_loop(input_node))

    def test_is_loop_true(self):
        nodes = [('10', '0')]
        self.add_nodes(nodes)

        input_node = [{'id': '0', 'parent': '10'}]
        self.assertTrue(self.storage.is_loop(input_node))

if __name__ == '__main__':
    unittest.main()
