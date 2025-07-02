from motor.motor_asyncio import AsyncIOMotorClient

Mongo_URL = "mongodb://localhost:27017"
client = AsyncIOMotorClient(Mongo_URL)
db=client.todo_db
todo_collection = db.get_collection("todos")
user_collection = db.get_collection("users")