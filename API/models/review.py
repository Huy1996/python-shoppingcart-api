from db import db

review_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["user", "product", "rating", "comment", "timestamps"],
        "properties": {
            "user": {
                "bsonType": "objectId",
                "description": "must be an objectId and is required"
            },
            "product": {
                "bsonType": "objectId",
                "description": "must be an objectId and is required"
            },
            "rating": {
                "bsonType": "int",
                "description": "must be an integer and is required"
            },
            "comment": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "timestamps": {
                "bsonType": "date",
                "description": "must be a date and is required"
            }
        }
    }
}

try:
    db.create_collection("Review")
except Exception as e:
    print(e)

db.command("collMod", "Review", validator=review_validator)

Reviews = db.Review

