from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from tree_storage.model import Node, Base


class Storage(object):

    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        session = sessionmaker()
        session.configure(bind=self.engine)
        Base.metadata.create_all(self.engine)
        self.session = session()

    def add_nodes(self, node_id, parent_id):
        """
        Add/Update one bind to the storage which
        represents two node.

        Add in case of node_id doesn't find in storage but
        update an existing bind without checking parent.

        :param node_id: string representation of node id
        :param parent_id: string representation of parent node id for node_id
        """
        if not self.session.query(Node).filter(Node.node_id == node_id).scalar():
            # create new
            node = Node(node_id=node_id, parent_id=parent_id)
            self.session.add(node)
            self.session.commit()
        else:
            # update existed
            self.session.query(Node).filter_by(node_id=node_id).update({"parent_id": parent_id})
            self.session.commit()

    def _get_child_lists(self, node_id):
        # Grab all children using recursion. Probably, should be rewritten with
        # ORM(SQL) interface but not such silly way
        nodes = self.session.query(Node).filter(Node.parent_id == node_id).all()
        children = []
        for node in nodes:
            children_below = self._get_child_lists(node.node_id)
            if children_below:
                for child in children_below:
                    children.append([node.node_id] + child)
            else:
                children.append([node.node_id])
        return children

    def _get_parents(self, node_id):
        # Simple recursion for getting all parents
        node = self.session.query(Node).filter(Node.node_id == node_id).scalar()
        if node is not None and node.parent_id is not None:
            return self._get_parents(node.parent_id) + [node.parent_id]
        else:
            return []

    def get_trees(self, node_id):
        """
        Get all chains for specified node.

        :param node_id: a node id for which need to return connected chains
        :return: data as [[<root node id>, ..., <leaf node id>], ..., [<another leaf>]]
        """
        data = []
        node = self.session.query(Node).filter(Node.node_id == node_id)
        if node is not None:
            parent_part = self._get_parents(node_id)
            for children_list in self._get_child_lists(node_id=node_id):
                data.append(parent_part + [node_id] + children_list)
            if not data:
                # no child - just put a one chain with a parent part
                data.append(parent_part + [node_id])
        return data

    def is_loop(self, nodes):
        """
        Check whether or not one of particular binds
        brings loop to the tree.

        Reject all nodes in case of one of them is broken

        :param nodes: new nodes
        :return: True/False - is it loop or not
        """
        for node in nodes:
            node_id = node['id']
            parent_id = node['parent']
            parents_of_parent = self._get_parents(node_id=parent_id)
            if node_id in parents_of_parent:
                return True
        return False
