# **Fast-graph** - A ready-made FastAPI integration made for Neo4j's graph database
<br>

November 2020

<br>

### **Table of Contents**
- [**Getting Started**](#Getting-Started)

- [**Authorisation & Security**](#Authorisation-and-Security)

- [**User Management**](#User-Management)

- [**Graph Objects**](#Graph-Objects)

    - [Nodes & Relationships](#Nodes-&-Relationships)

- [**Next Steps**](#Next-Steps)

- [**Contact**](#Contact)


<br>

### **Getting Started**
<br>

First, download or clone this repository to use on your local machine. Then, 
>pip install -r requirements.txt

to install the required packages. Lastly, you'll want to make sure to create a '.env' file with the necessary credentials and settings (you can find what these are in the app/utils directory - you can set these directly but I think it's best to separate out into a hidden config file - like '.env'). When you have the required Neo4j credentials set in the **app/utils/db.py** file, and you've started the local Neo4j database that you will be using, than you can start the server with

> uvicorn main:app --reload

You will then be able to access the automatically generated documentation at http://127.0.0.1:8000/docs.

<br>

#### **Built with Amazing Tools**
<br>

> [**FastAPI**](https://github.com/tiangolo/fastapi)

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
Github - [dudikbender](https://github.com/dudikbender)

Email - [bender2242@gmail.com](mailto:bender2242@gmail.com)