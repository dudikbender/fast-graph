# Import required base modules
from neo4j import GraphDatabase
from datetime import datetime
import os
from dotenv import load_dotenv, find_dotenv
from typing import Optional

# Import modules from FastAPI
from fastapi import APIRouter, Depends, HTTPException, status

# Internal modules to manage authorisations
from utils.schema import Query

# Load environment variables
env_loc = find_dotenv('.env')
load_dotenv(env_loc)

# Neo4j driver execution
uri = os.environ.get('DB_URI')
username = os.environ.get('DB_USERNAME')
password = os.environ.get('DB_PASSWORD')
neo4j_driver = GraphDatabase.driver(uri, auth=(username, password))

# Set the API Router
router = APIRouter()

# Query endpoint
@router.get('/q',response_model=Query,
            summary='Query the database with a custom Cypher string')
async def cypher_query(cypher_string: str):
    with neo4j_driver.session() as session:
        response = session.run(query=cypher_string)
        query_response = Query(response=response.data())
        return query_response