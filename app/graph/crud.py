from datetime import datetime, timezone
from typing import Optional

# Import modules from FastAPI
from fastapi import APIRouter, Depends, HTTPException, status

# Import internal utilities for database access, authorisation, and schemas
from app.utils.db import neo4j_driver
from app.authorisation.auth import get_current_active_user
from app.utils.schema import User, Node, Nodes, Relationship

# Set the API Router
router = APIRouter()

# List of acceptable node labels and relationship types
# Modify these to add constraints
node_labels = ['Address', 'Geography', 'Person', 'Company', 'Event']
relationship_types = ['LIVES_IN', 'USED_TO_LIVE_IN', 'WORKS_FOR', 'LOCATED_IN', 'KNOWS', 'ATTENDED', 'FRIEND']

# Used for validation to ensure they are not overwritten
base_properties = ['created_by', 'created_time']


# CREATE new node
@router.post('/create_node', response_model=Node)
async def create_node(label: str, node_attributes: dict,
                      current_user: User = Depends(get_current_active_user)):
    # Check that node is not User
    if label == 'User':
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Operation not permitted, cannot create a User with this method.",
            headers={"WWW-Authenticate": "Bearer"})

    # Check that node has an acceptable label
    if label not in node_labels:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Operation not permitted, node label is not accepted.",
            headers={"WWW-Authenticate": "Bearer"})

    # Check that attributes dictionary does not modify base fields
    for key in node_attributes:
        if key in base_properties:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Operation not permitted, you cannot modify those fields with this method.",
                                headers={"WWW-Authenticate": "Bearer"})

    unpacked_attributes = 'SET ' + ', '.join(f'new_node.{key}=\'{value}\'' for (key, value) in node_attributes.items())

    cypher = f"""
            CREATE (new_node:{label})\n'
            SET new_node.created_by = $created_by\n'
            SET new_node.created_time = $created_time\n'
            {unpacked_attributes}\n
            RETURN new_node, LABELS(new_node) as labels, ID(new_node) as id')
            """

    with neo4j_driver.session() as session:
        result = session.run(
            query=cypher,
            parameters={
                'created_by': current_user.username,
                'created_time': str(datetime.now(timezone.utc)),
                'attributes': node_attributes,
            },
        )

        node_data = result.data()[0]

    return Node(node_id=node_data['id'],
                labels=node_data['labels'],
                properties=node_data['new_node'])


# READ data about a node in the graph by ID
@router.get('/read/{node_id}', response_model=Node)
async def read_node_id(node_id: int, current_user: User = Depends(get_current_active_user)):
    """
    **Retrieves data about a node in the graph, based on node ID.**

    :param **node_id** (str) - node id, used for indexed search

    :returns: Node response, with node id, labels, and properties.
    """

    cypher = """
    MATCH (node)
    WHERE ID(node) = $node_id
    RETURN ID(node) as id, LABELS(node) as labels, node
    """

    with neo4j_driver.session() as session:
        result = session.run(query=cypher,
                             parameters={'node_id': node_id})

        node_data = result.data()[0]

    # Check node for type User, and send error message if needed
    if 'User' in node_data['labels']:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Operation not permitted, please use User endpoints to retrieve user information.",
            headers={"WWW-Authenticate": "Bearer"})

    # Return Node response
    return Node(node_id=node_data['id'],
                labels=node_data['labels'],
                properties=node_data['node'])


# READ data about a collection of nodes in the graph
@router.get('/read_node_collection', response_model=Nodes)
async def read_nodes(search_node_property: str, node_property_value: str,
                     current_user: User = Depends(get_current_active_user)):
    """
    Retrieves data about a collection of nodes in the graph, based on node property.

    :param **node_property** (str) - property to search in nodes

    :param **node_property_value** (str) - value of property, to select the correct node

    :returns: Node response, with node id, labels, and properties. Returns only first response.
    """

    cypher = f"""
        MATCH (node)
        WHERE node.{search_node_property} = '{node_property_value}'
        RETURN ID(node) as id, LABELS(node) as labels, node')
        """

    with neo4j_driver.session() as session:
        result = session.run(query=cypher)

        collection_data = result.data()

    node_list = []
    for node in collection_data:
        # Create node for each result in query
        node = Node(node_id=node['id'],
                    labels=node['labels'],
                    properties=node['node'])

        # Append each node result into Nodes list
        node_list.append(node)

    # Return Nodes response with collection as list
    return Nodes(nodes=node_list)


# UPDATE properties of node in the graph
@router.put('/update/{node_id}')
async def update_node(node_id: int, attributes: dict):
    # Check that property to update is not part of base list
    for key in attributes:
        if key in base_properties:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Operation not permitted, that property field cannot be updated.",
                headers={"WWW-Authenticate": "Bearer"})

    cypher = '''MATCH (node) WHERE ID(node) = $id
                SET node += $attributes
                RETURN node, ID(node) as id, LABELS(node) as labels'''

    with neo4j_driver.session() as session:
        result = session.run(query=cypher,
                             parameters={'id': node_id, 'attributes': attributes})

        node_data = result.data()[0]

    # Return Node response
    return Node(node_id=node_data['id'],
                labels=node_data['labels'],
                properties=node_data['node'])


# DELETE node in the graph
@router.post('/delete/{node_id}')
async def delete_node(node_id: int):

    cypher = """
    MATCH (node)
    WHERE ID(node) = $node_id
    DETACH DELETE node
    """

    with neo4j_driver.session() as session:
        result = session.run(query=cypher,
                             parameters={'node_id': node_id})

        node_data = result.data()

    # Confirm deletion was completed by empty response
    return node_data or {
        'response': f'Node with ID: {node_id} was successfully deleted from the graph.'
    }


# RELATIONSHIPS
# Create new relationship between two nodes
@router.post('/create_relationship', response_model=Relationship)
async def create_relationship(source_node_label: str, source_node_property: str, source_node_property_value: str,
                              target_node_label: str, target_node_property: str, target_node_property_value: str,
                              relationship_type: str, relationship_attributes: Optional[dict] = None,
                              current_user: User = Depends(get_current_active_user)):
    # Check that relationship has an acceptable type
    if relationship_type not in relationship_types:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Operation not permitted, relationship type is not accepted.",
            headers={"WWW-Authenticate": "Bearer"})

    # Check that attributes dictionary does not modify base fields
    for key in relationship_attributes:
        if key in base_properties:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Operation not permitted, you cannot modify those fields with this method.",
                                headers={"WWW-Authenticate": "Bearer"})

    if relationship_attributes:
        unpacked_attributes = 'SET ' + ', '.join(f'relationship.{key}=\'{value}\'' for (key, value) in relationship_attributes.items())
    else:
        unpacked_attributes = ''

    cypher = f"""
        MATCH (nodeA:{source_node_label}) WHERE nodeA.{source_node_property} = $nodeA_property
        MATCH (nodeB:{target_node_label}) WHERE nodeB.{target_node_property} = $nodeB_property
        CREATE (nodeA)-[relationship:{relationship_type}]->(nodeB)
        SET relationship.created_by = $created_by
        SET relationship.created_time = $created_time
        {unpacked_attributes}
        RETURN nodeA, nodeB, LABELS(nodeA), LABELS(nodeB), ID(nodeA), ID(nodeB), ID(relationship), TYPE(relationship), PROPERTIES(relationship)
        """

    with neo4j_driver.session() as session:
        result = session.run(
            query=cypher,
            parameters={
                'created_by': current_user.username,
                'created_time': str(datetime.now(timezone.utc)),
                'nodeA_property': source_node_property_value,
                'nodeB_property': target_node_property_value,
            },
        )

        relationship_data = result.data()[0]

    # Organise the data about the nodes in the relationship
    source_node = Node(node_id=relationship_data['ID(nodeA)'],
                       labels=relationship_data['LABELS(nodeA)'],
                       properties=relationship_data['nodeA'])

    target_node = Node(node_id=relationship_data['ID(nodeB)'],
                       labels=relationship_data['LABELS(nodeB)'],
                       properties=relationship_data['nodeB'])

    # Return Relationship response
    return Relationship(relationship_id=relationship_data['ID(relationship)'],
                        relationship_type=relationship_data['TYPE(relationship)'],
                        properties=relationship_data['PROPERTIES(relationship)'],
                        source_node=source_node,
                        target_node=target_node)


# READ data about a relationship
@router.get('/read_relationship/{relationship_id}', response_model=Relationship)
async def read_relationship(relationship_id: int):

    cypher = """
        MATCH (nodeA)-[relationship]->(nodeB)
        WHERE ID(relationship) = $rel_id
        RETURN nodeA, ID(nodeA), LABELS(nodeA), relationship, ID(relationship), TYPE(relationship), nodeB, ID(nodeB), LABELS(nodeB), PROPERTIES(relationship)
        """

    with neo4j_driver.session() as session:
        result = session.run(query=cypher,
                             parameters={'rel_id': relationship_id})

        relationship_data = result.data()[0]

    # Organise the data about the nodes in the relationship
    source_node = Node(node_id=relationship_data["ID(nodeA)"],
                       labels=relationship_data["LABELS(nodeA)"],
                       properties=relationship_data["nodeA"])

    target_node = Node(node_id=relationship_data["ID(nodeB)"],
                       labels=relationship_data["LABELS(nodeB)"],
                       properties=relationship_data["nodeB"])

    # Return Relationship response
    return Relationship(relationship_id=relationship_data["ID(relationship)"],
                        relationship_type=relationship_data["TYPE(relationship)"],
                        properties=relationship_data["PROPERTIES(relationship)"],
                        source_node=source_node,
                        target_node=target_node)


# READ data about a relationship
@router.put('/update_relationship/{relationship_id}', response_model=Relationship)
async def update_relationship(relationship_id: int, attributes: dict):

    cypher = """
    MATCH (nodeA)-[relationship]->(nodeB)
    WHERE ID(relationship) = $rel_id
    SET relationship += $attributes
    RETURN nodeA, ID(nodeA), LABELS(nodeA), relationship, ID(relationship), TYPE(relationship), nodeB, ID(nodeB), LABELS(nodeB), PROPERTIES(relationship)
    """

    with neo4j_driver.session() as session:
        result = session.run(query=cypher,
                             parameters={'rel_id': relationship_id,
                                         'attributes': attributes})

        relationship_data = result.data()[0]

    # Organise the data about the nodes in the relationship
    source_node = Node(node_id=relationship_data['ID(nodeA)'],
                       labels=relationship_data['LABELS(nodeA)'],
                       properties=relationship_data['nodeA'])

    target_node = Node(node_id=relationship_data['ID(nodeB)'],
                       labels=relationship_data['LABELS(nodeB)'],
                       properties=relationship_data['nodeB'])

    # Return Relationship response
    return Relationship(relationship_id=relationship_data['ID(relationship)'],
                        relationship_type=relationship_data['TYPE(relationship)'],
                        properties=relationship_data['PROPERTIES(relationship)'],
                        source_node=source_node,
                        target_node=target_node)


# DELETE relationship in the graph
@router.post('/delete_relationship/{relationship_id}')
async def delete_relationship(relationship_id: int):

    cypher = """
        MATCH (a)-[relationship]->(b)
        WHERE ID(relationship) = $relationship_id
        DELETE relationship
        """

    with neo4j_driver.session() as session:
        result = session.run(query=cypher,
                             parameters={'relationship_id': relationship_id})

        relationship_data = result.data()

    # Confirm deletion was completed by empty response
    return relationship_data or {
        'response': f'Relationship with ID: {relationship_id} was successfully deleted from the graph.'
    }
