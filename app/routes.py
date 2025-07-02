from fastapi import APIRouter, HTTPException, Depends
from app.models import TodoModel
from app.database import todo_collection
from app.auth import get_current_user
from bson import ObjectId



router = APIRouter()

@router.post("/todos")
async def create_todo(todo: TodoModel, current_user: dict = Depends(get_current_user)):
    todo_dict = todo.dict()
    todo_dict["owner"] = current_user["username"]
    result = await todo_collection.insert_one(todo.dict())
    return {"id": str(result.inserted_id)}

@router.get("/todos")
async def list_todos(current_user: dict = Depends(get_current_user)):
    todos = []
    async for doc in todo_collection.find({"owner": current_user["username"]}):
        doc["id"] = str(doc["_id"])
        doc.pop("_id")
        todos.append(doc)
    return todos

@router.get("/todos/{id}")
async def get_todo(id: str, current_user: dict = Depends(get_current_user)):
    todo = await todo_collection.find_one({"_id": ObjectId(id), "owner": current_user})
    if todo:
        todo["id"] = str(todo["_id"])
        todo.pop("_id")
        return todo
    raise HTTPException(status_code=404, detail="Todo not found")

@router.put("/todos/{id}")
async def update_todo(id: str, todo: TodoModel, current_user: dict = Depends(get_current_user)):
    result = await todo_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": todo.dict(), "owner": current_user["username"]}
    )
    if result.modified_count:
        return {"msg": "Updated successfully"}
    raise HTTPException(status_code=404, detail="Todo not found or unchanged")

@router.delete("/todos/{id}")
async def delete_todo(id: str, current_user: dict = Depends(get_current_user)):
    result = await todo_collection.delete_one({"_id": ObjectId(id), "owner": current_user["username"]})
    if result.deleted_count:
        return {"msg": "Deleted successfully"}
    raise HTTPException(status_code=404, detail="Todo not found")
