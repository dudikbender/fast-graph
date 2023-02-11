# **Fast-graph** - A ready-made FastAPI integration made for Neo4j's graph database
<br>
February 2023
<br>

### **Table of Contents**
- [**Getting Started**](#Getting-Started)
- [**Authorisation & Security**](#Authorisation-and-Security)
- [**User Management**](#User-Management)
- [**Graph Objects**](#Graph-Objects)
    - [Nodes & Relationships](#Nodes-&-Relationships)
- [**Next Steps**](#Next-Steps)
- [**Contact**](#Contact)

### **Getting Started**
First, after downloading or cloning this repository to use on your local machine. 

Create a Virtual Environment
> % python -m venv .venv<br>
> % source .venv/bin/activate<br>

Install project requirements
> % pip install -r requirements.txt

Create a '.env' file with all the necessary credentials and settings<br>
See .env.example to start. When you have the required Neo4j credentials set the environment file, and you've started you Neo4j database that you will be using, than you can start the server with
> % uvicorn app.main:app --reload

You will then be able to access the automatically generated documentation at http://127.0.0.1:8000/docs.

Before you can do any interesting thing with the API, you will need to create a user using the `/auth/launch_user` endpoint. For this to work, your application must have the APP_PASSWORD environment variable set. Once the initial user is created, its recommended to remove the APP_PASSWORD from your environment configuration.

Once created, you must authenticate using the built-in Authentication system of the Swagger API documentation


### **Default Endpoints** 

`/auth/token` - Used to generate an authentication token<br>
`/auth/launch_user` - Used to create the first user in the system after installation. See Getting Started section above<br>
`/users/*` - Interactions with the built-in user database<br>
`/graph/*` - Neo4j RESTful interactions<br>
`/q` - Neo4j Cypher Query<br>

<br>

#### **Built with Amazing Tools**
<br>

> [**FastAPI**](https://github.com/tiangolo/fastapi)<br>
> [**Neo4j**](https://neo4j.com/) & [**Neo4j Python Driver**](https://neo4j.com/docs/api/python-driver/current/)

<br>

### **Authorisation and Security**
This API is configured with Oauth2 password authentication flow. It uses FastAPI's Dependency Injection system to create this flow, so if you'd like a different one take a look at the FastAPI documentation on Security and/or Dependencies to modify it.

There is also built-in encryption for user passwords, as well as some constraints on types of nodes or relationships and certain edits are not allowed (e.g., you cannot edit a user's password for the 'update_node' endpoint). There are lots of opportunities to expand the functionality on user access and permissions - particularly for traversing the graph - so **any ideas or suggestions are more than welcome**.

You can also export the documentation to API tools, such as Postman. Go to http://127.0.0.1:8000/openapi.json to get the JSON for the OpenAPI that FastAPI generates, and simply import this into Postman (or other tools that can process the OpenAPI standard) to test calling the endpoints.

<br>

### **User Management**
In this configuration, Users are a special type of Node with their own BaseModel schema. This is largely based on the example application from the FastAPI documentation, but it is also there because there are unique characteristics that separate Users from your typical Node in the graph.

This means that operations like updating the user's password can only be done a particular way, etc. So it has it's own directory and operations - which could be a model for other special Node types.

<br>

### **Graph Objects**
#### ***Nodes & Relationships***
This API uses the Neo4j Cypher language, so in the same way that you can create Nodes with labels and properties, you can do the same with Fast-graph. I've put in a few constraints, but simply remove or edit these if you want to create different types of Nodes or Relationships. You can perform basic CRUD operations for Nodes and simple Relationships (triples, with source and target nodes linked by a relationships)

<br>

### **Next Steps**
I'd like to expand the query functionality, particularly in regards to query and graph traversal operation. Also, adding the ability to construct more complex relationships would be great for lots of potential use cases. Immediate next step is to build out the unit testing for each module.  **Would love any feedback or suggestions**.

<br>

### **Contact**
Github - [dudikbender](https://github.com/dudikbender) / Email - [bender2242@gmail.com](mailto:bender2242@gmail.com)<br>
Github - [jizaymes](https://github.com/jizaymes) / Twitter - [@jizaymes](https://twitter.com/jizaymes) / Email - [jizaymes@gmail.com](mailto:jizaymes@gmail.com)<br>