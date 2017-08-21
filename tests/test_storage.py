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
        pass

    def test_get_trees_parent_based(self):
        pass

    def test_is_loop(self):
        pass

if __name__ == '__main__':
    unittest.main()
