from fastapi import APIRouter, HTTPException
from app.models import TodoModel
from app.database import todo_collection
from bson import ObjectId

router = APIRouter()

@router.post("/todos")
async def create_todo(todo: TodoModel):
    result = await todo_collection.insert_one(todo.dict())
    return {"id": str(result.inserted_id)}

@router.get("/todos")
async def list_todos():
    todos = []
    async for doc in todo_collection.find():
        doc["id"] = str(doc["_id"])
        doc.pop("_id")
        todos.append(doc)
    return todos

@router.get("/todos/{id}")
async def get_todo(id: str):
    todo = await todo_collection.find_one({"_id": ObjectId(id)})
    if todo:
        todo["id"] = str(todo["_id"])
        todo.pop("_id")
        return todo
    raise HTTPException(status_code=404, detail="Todo not found")

@router.put("/todos/{id}")
async def update_todo(id: str, todo: TodoModel):
    result = await todo_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": todo.dict()}
    )
    if result.modified_count:
        return {"msg": "Updated successfully"}
    raise HTTPException(status_code=404, detail="Todo not found or unchanged")

@router.delete("/todos/{id}")
async def delete_todo(id: str):
    result = await todo_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count:
        return {"msg": "Deleted successfully"}
    raise HTTPException(status_code=404, detail="Todo not found")
