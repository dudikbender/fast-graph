# Import Neo4j Python driver
from neo4j import GraphDatabase

# Packages and functions for loading environment variables
from app.utils.environment import Config

neo4j_driver = GraphDatabase.driver(Config.NEO4J_URI, auth=(Config.NEO4J_USERNAME, Config.NEO4J_PASSWORD))
