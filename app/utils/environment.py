# Packages and functions for loading environment variables
import os
from dotenv import load_dotenv, find_dotenv

# Load environment from disk first, then apply any defaults
load_dotenv(find_dotenv('.env'))


class Config:
    # Application password for superadmin functions (/auth/launch_user endpoint for first-time setup)
    APP_PASSWORD = os.environ.get('APP_PASSWORD')

    # Settings for encryption
    SECRET_KEY = os.environ.get('SECRET_KEY', 'secret')
    ALGORITHM = os.environ.get('ALGORITHM', "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES', 10_080))  # one week

    # Neo4j driver execution
    NEO4J_URI = os.environ.get('NEO4J_URI','')
    NEO4J_USERNAME = os.environ.get('NEO4J_USERNAME', 'neo4j')
    NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD','')
