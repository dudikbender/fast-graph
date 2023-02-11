# Import required base modules
from dotenv import load_dotenv, find_dotenv

# Import modules from FastAPI
from fastapi import APIRouter

# Import internal utilities for database access and schemas
from app.utils.db import neo4j_driver
from app.utils.schema import Query

# Load environment variables
env_loc = find_dotenv('.env')
load_dotenv(env_loc)

# Set the API Router
router = APIRouter()


# Query endpoint
@router.get('/q', response_model=Query, summary='Query the database with a custom Cypher string')
async def cypher_query(cypher_string: str):
    with neo4j_driver.session() as session:
        response = session.run(query=cypher_string)
        return Query(response=response.data())
