# Import main FastAPI modules
from fastapi import FastAPI, Depends

# Internal packages
from authorisation import auth
from authorisation.auth import get_current_active_user
from user_management import users
from graph import crud
from query import cypher

app = FastAPI(title='FastGraph',
              description='API built for Neo4j with FastAPI',
              version=0.1)

app.include_router(
    auth.router,
    prefix='/auth',
    tags=['Authorisation']
)

app.include_router(
    users.router,
    prefix='/users',
    tags=['Users'],
    dependencies=[Depends(get_current_active_user)]
)

app.include_router(
    crud.router,
    prefix='/graph',
    tags=['Graph Objects'],
    dependencies=[Depends(get_current_active_user)]
)

app.include_router(
    cypher.router,
    tags=['Query Database'],
    dependencies=[Depends(get_current_active_user)]
)