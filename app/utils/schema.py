from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


# Authorisation response models
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Node response models
class NodeBase(BaseModel):
    node_id: int
    labels: list


class Node(NodeBase):
    properties: Optional[dict] = None


class Nodes(BaseModel):
    nodes: List[Node]


# User response models
class User(BaseModel):
    username: str
    full_name: Optional[str] = None
    joined: Optional[datetime] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str


# Relationship response models
class Relationship(BaseModel):
    relationship_id: int
    relationship_type: str
    source_node: Node
    target_node: Node
    properties: Optional[dict] = None


# Query response model
class Query(BaseModel):
    response: list
