from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson import ObjectId
from app.models import Item
import json

router = APIRouter()

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
collection = db["items"]

@router.get("/")
async def home():
    return {"API":"Working"}

@router.post("/items/")
async def create_item(item: Item):
    try:
        inserted_item = collection.insert_one(item.dict())
        created_item = collection.find_one({"_id": inserted_item.inserted_id})
        return json.loads(json.dumps(created_item, default=str))  # Convert ObjectId to string before returning
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/items/")
async def read_items():
    try:
        items = []
        for item in collection.find():
            items.append(json.loads(json.dumps(item, default=str)))  # Convert ObjectId to string before appending
        return items
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/items/{item_id}")
async def read_item(item_id: str):
    try:
        item = collection.find_one({"_id": ObjectId(item_id)})
        if item:
            return json.loads(json.dumps(item, default=str))  # Convert ObjectId to string before returning
        else:
            raise HTTPException(status_code=404, detail="Item not found")
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/items/{item_id}")
async def update_item(item_id: str, item_updates: dict):
    try:
        item_updates = {key: value for key, value in item_updates.items() if value is not None}  # Remove None values
        if not item_updates:
            raise HTTPException(status_code=400, detail="No fields provided for update")
        
        collection.update_one({"_id": ObjectId(item_id)}, {"$set": item_updates})
        updated_item = collection.find_one({"_id": ObjectId(item_id)})
        
        if updated_item:
            return json.loads(json.dumps(updated_item, default=str))
        else:
            raise HTTPException(status_code=404, detail="Item not found")
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/items/{item_id}")
async def delete_item(item_id: str):
    try:
        deleted_item = collection.find_one_and_delete({"_id": ObjectId(item_id)})
        if deleted_item:
            return json.loads(json.dumps(deleted_item, default=str))  # Convert ObjectId to string before returning
        else:
            raise HTTPException(status_code=404, detail="Item not found")
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=str(e))
