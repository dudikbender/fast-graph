# Import required base modules
#from neo4j import GraphDatabase, Query
from datetime import datetime
import os
from dotenv import load_dotenv
from typing import Optional

# Import modules from FastAPI
from fastapi import APIRouter, Depends, HTTPException, status

# Import internal utilities for database access, authorisation, and schemas
from app.utils.db import neo4j_driver
from app.authorisation.auth import get_current_active_user, create_password_hash
from app.utils.schema import User

# Load environment variables
load_dotenv('.env')

# Set the API Router
router = APIRouter()

# GET Current user's information
@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

# GET Specified user's information by username
@router.get('/{username}', response_model=User)
async def read_user(username: str):
    query = 'MATCH (user:User) WHERE user.username = $username RETURN user'

    with neo4j_driver.session() as session:
        user_in_db = session.run(query=query, parameters={'username':username})
        user_data = user_in_db.data()[0]['user']
    
    user_id = user_data['id']

    return User(**user_data)

# CREATE User
@router.post("/create", response_model=User)
async def create_user(username: str, password: str, 
                      full_name: Optional[str] = None,
                      disabled: Optional[bool] = None):

    # Create dictionary of new user attributes
    attributes = {'username':username,
                  'full_name':full_name,
                  'hashed_password':create_password_hash(password),
                  'joined':str(datetime.utcnow()),
                  'disabled':disabled}

    # Write Cypher query and run against the database
    cypher_search = 'MATCH (user:User) WHERE user.username = $username RETURN user'
    cypher_create = 'CREATE (user:User $params) RETURN user'

    with neo4j_driver.session() as session:
        # First, run a search of users to determine if username is already in use
        check_users = session.run(query=cypher_search, parameters={'username':username})
        
        # Return error message if username is already in the database
        if check_users.data():
            raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Operation not permitted, user with username {username} already exists.",
            headers={"WWW-Authenticate": "Bearer"})

        response = session.run(query=cypher_create, parameters={'params':attributes})
        user_data = response.data()[0]['user']
    user = User(**user_data)
    return user

# UPDATE User profile
@router.put('/{username}/update', response_model=User)
async def update_user(attributes: dict, username: str):
    # Add check to stop call if password is being changed
    for k in attributes:
        if k == 'hashed_password':
            raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Operation not permitted, cannot update password with this method.",
            headers={"WWW-Authenticate": "Bearer"})
    
    if relationship_attributes:
        unpacked_attributes = 'SET ' + ', '.join(f'user.{key}=\'{value}\'' for (key, value) in relationship_attributes.items())
    else:
        unpacked_attributes = ''

    # Execute Cypher query to reset the hashed_password attribute
    cypher_update_user = ('MATCH (user: User) WHERE user.username = $user\n'
                          f'{unpacked_attributes}\n'
                          'RETURN user')

    with neo4j_driver.session() as session:
        updated_user = session.run(query=cypher_update_user,
                                   parameters={'user':username})
        user_data = updated_user.data()[0]['user']
    
    user = User(**user_data)
    return user

# RESET User password
@router.put('/me/reset_password', response_model=User)
async def reset_password(new_password: str, current_user: User = Depends(get_current_active_user)):
    # Get current user's username and encrypt new password
    username = current_user.username
    new_password_hash = create_password_hash(new_password)

    # Execute Cypher query to reset the hashed_password attribute
    cypher_reset_password = ('MATCH (user:User) WHERE user.username = $username\n'
                             'SET user.hashed_password = $new_password_hash\n'
                             'RETURN user')
    
    with neo4j_driver.session() as session:
        updated_user = session.run(query=cypher_reset_password, 
                                   parameters={'username':username,
                                               'new_password_hash':new_password_hash})
        user_data = updated_user.data()[0]['user']
    user = User(**user_data)
    return user