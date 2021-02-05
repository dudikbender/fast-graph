# Import Neo4j Python driver
from neo4j import GraphDatabase

# Packages and functions for loading environment variables
import os
from dotenv import load_dotenv, find_dotenv
env_loc = find_dotenv('.env')
load_dotenv(env_loc)

# Neo4j driver execution
uri = os.environ.get('NEO4J_URI')
username = os.environ.get('NEO4J_USERNAME')
password = os.environ.get('NEO4J_PASSWORD')
neo4j_driver = GraphDatabase.driver(uri, auth=(username, password))