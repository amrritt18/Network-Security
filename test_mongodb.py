
from pymongo import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://amrritt1804_db_user:SPAvU2yZlOffhr9Z@amrit.t7eq499.mongodb.net/?appName=Amrit"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)