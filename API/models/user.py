from db import db

user_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [ "name", "email", "password", "isAdmin"],
        "properties": {
            "name": {
               "bsonType": "string",
               "description": "must be a string and is required"
            },
            "email": {
               "bsonType": "string",
               "description": "must be a string and is required"
            },
            "password": {
               "bsonType": "string",
               "description": "must be a string and is required"
            },
            "isAdmin": {
               "bsonType": "bool",
               "description": "must be a bool and is required"
            }
        }
    }
}

try:
    db.create_collection("user")
except Exception as e:
    print(e)

db.command("collMod", "user", validator=user_validator)

Users = db.user

