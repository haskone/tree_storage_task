from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String
from sqlalchemy.orm import relationship

Base = declarative_base()


class Node(Base):
    __tablename__ = 'node'
    node_id = Column(String(32), primary_key=True)
    parent_id = Column(String(32), ForeignKey('node.node_id'))
    children = relationship("Node")

    def __init__(self, node_id, parent_id):
        self.node_id = node_id
        self.parent_id = parent_id
