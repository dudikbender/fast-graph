# Import required base modules
#from neo4j import GraphDatabase
from datetime import datetime
import os
from dotenv import load_dotenv
from typing import Optional

# Import modules from FastAPI
from fastapi import APIRouter, Depends, HTTPException, status

# Import internal utilities for database access, authorisation, and schemas
from utils.db import neo4j_driver
from authorisation.auth import get_current_active_user
from utils.schema import User, Node, Relationship

# Load environment variables
load_dotenv('.env')

# Set the API Router
router = APIRouter()

# List of acceptable node labels and relationship types
# Modify these to add constraints
node_labels = ['Address','Geography','Person','Company']
relationship_types = ['LIVES_IN','USED_TO_LIVE_IN','WORKS_FOR','LOCATED_IN','KNOWS']
base_properties = ['created_by','created_time','permission']

### CREATE NODES AND RELATIONSHIPS
# Create new node
@router.post('/create_node', response_model=Node)
async def create_node(label:str, node_attributes: dict, permission: Optional[str] = None, 
                      current_user: User = Depends(get_current_active_user)):
    
    # Check that node has an acceptable label
    if label not in node_labels:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Operation not permitted, node label is not accepted.",
            headers={"WWW-Authenticate": "Bearer"})

    # Check that attributes dictionary does not modify base fields
    for key in node_attributes:
        if key in base_properties:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail=f"Operation not permitted, you cannot modify those fields with this method.",
                                headers={"WWW-Authenticate": "Bearer"})
    
    cypher = (f'CREATE (new_node:{label})\n'
               'SET new_node.created_by = $created_by\n'
               'SET new_node.created_time = $created_time\n'
               'SET new_node.permission = $permission\n'
               'SET new_node += {attributes}\n'
               'RETURN new_node, LABELS(new_node) as labels')

    with neo4j_driver.session() as session:
        result = session.run(query=cypher, 
                             parameters={'created_by':current_user.username,
                             'created_time':str(datetime.utcnow()),
                             'permission':permission,
                             'attributes':node_attributes})

        node_data = result.data()[0]

    properties = node_data['new_node']
    labels = node_data['labels']
    
    node = Node(labels=labels,
                properties=properties)
    return node

# Create new relationship between two nodes
@router.post('/create_relationship', response_model=Relationship)
async def create_relationship(source_node_label: str, source_node_property: str, source_node_property_value: str,
                              target_node_label: str, target_node_property: str, target_node_property_value: str,
                              relationship_type: str, relationship_attributes: dict,
                              permission: Optional[str] = None,
                              current_user: User = Depends(get_current_active_user)):
    # Check that relationship has an acceptable type
    if relationship_type not in relationship_types:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Operation not permitted, relationship type is not accepted.",
            headers={"WWW-Authenticate": "Bearer"})

    # Check that attributes dictionary does not modify base fields
    for key in relationship_attributes:
        if key in base_properties:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail=f"Operation not permitted, you cannot modify those fields with this method.",
                                headers={"WWW-Authenticate": "Bearer"})
    
    cypher = (f'MATCH (nodeA:{source_node_label}) WHERE nodeA.{source_node_property} = $nodeA_property\n'
            f'MATCH (nodeB:{target_node_label}) WHERE nodeB.{target_node_property} = $nodeB_property\n'
            f'CREATE (nodeA)-[relationship:{relationship_type}]->(nodeB)\n'
            'SET relationship.created_by = $created_by\n'
            'SET relationship.created_time = $created_time\n'
            'SET relationship.permission = $permission\n'
            'SET relationship += {relationship_attributes}\n'
            'RETURN nodeA, nodeB, LABELS(nodeA) as nodeA_labels, LABELS(nodeB) as nodeB_labels, TYPE(relationship), PROPERTIES(relationship)')

    with neo4j_driver.session() as session:
        result = session.run(query=cypher, 
                             parameters={'created_by':current_user.username,
                                         'created_time':str(datetime.utcnow()),
                                         'permission':permission,
                                         'nodeA_property':source_node_property_value,
                                         'nodeB_property':target_node_property_value,
                                         'relationship_attributes':relationship_attributes})

        relationship_data = result.data()[0]

    # Organize the response data
    relationship_type = relationship_data['TYPE(relationship)']
    properties = relationship_data['PROPERTIES(relationship)']
    source_node_labels = relationship_data['nodeA_labels']
    target_node_labels = relationship_data['nodeB_labels']
    source_node = Node(labels=source_node_labels,
                       properties=relationship_data['nodeA'])
    target_node = Node(labels=target_node_labels,
                       properties=relationship_data['nodeB'])
    
    relationship = Relationship(relationship_type=relationship_type,
                                properties=properties,
                                source_node=source_node,
                                target_node=target_node)
    return relationship