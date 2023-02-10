# Import Neo4j Python driver
from neo4j import GraphDatabase

# Packages and functions for loading environment variables
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv('.env'))

# Neo4j driver execution
uri = os.environ.get('NEO4J_URI')
username = os.environ.get('NEO4J_USERNAME', 'neo4j')
password = os.environ.get('NEO4J_PASSWORD')
neo4j_driver = GraphDatabase.driver(uri, auth=(username, password))
