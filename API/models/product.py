from db import db

product_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [ "name", "image", "brand", "category", "description",
                      "price", "countInStock", "rating", "numReviews"],
        "properties": {
            "name": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "image": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "brand": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "category": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "description": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "price": {
                "bsonType": "double",
                "minimum": 0,
                "description": "must be an double and is required"
            },
            "countInStock": {
                "bsonType": "int",
                "minimum": 0,
                "description": "must be an integer and is required"
            },
            "rating": {
                "bsonType": "int",
                "maximum": 5,
                "minimum": 0,
                "description": "must be an integer between 0 and 5 and is required"
            },
            "numReviews": {
                "bsonType": "int",
                "minimum": 0,
                "description": "must be an integer and is required"
            },
            "attribute": {
                "bsonType": ["array"],
                "minItems": 0,
                "items": {
                    "bsonType": "object",
                    "required": ["name", "options"],
                    "properties": {
                        "name": {
                            "bsonType": "string",
                            "description": "must be a string and is required"
                        },
                        "options": {
                            "bsonType": "array",
                            "items": {
                                "bsonType": ["string", "int"]
                            }
                        }
                    }
                },
                "description": "must be an array and is required"
            }
        }
    }
}

try:
    db.create_collection("Product")
except Exception as e:
    print(e)

db.command("collMod", "Product", validator=product_validator)

Products = db.Product