from API.middleware.middleware import validate_request
from API.models.review import Reviews
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime


_review_parser = reqparse.RequestParser()
_review_parser.add_argument("rating", type=int)
_review_parser.add_argument("comment", type=str)


class UserReview(Resource):
    @validate_request()
    def get(self, user_id):
        _id = ObjectId(user_id)
        review_list = Reviews.aggregate([
            {
                "$match": {"user": _id}
            },
            {
                "$lookup": {
                    "from": "Product",
                    "localField": "product",
                    "foreignField": "_id",
                    "as": "product"
                }
            },
            {
                "$set": {
                    "product": {
                        "$arrayElemAt": ["$product", 0]
                    }
                }
            }
        ])
        review_list = [{**review,
                        "_id": str(review["_id"]),
                        "user": str(review["user"]),
                        "product": {**review["product"], "_id": str(review["product"]["_id"])},
                        "timestamps": review["timestamps"].isoformat()
                        } for review in review_list]
        return review_list, 200


class ProductReview(Resource):
    def get(self, product_id):
        _id = ObjectId(product_id)
        review_list = Reviews.aggregate([
            {
                "$match": {"product": _id}
            },
            {
                "$lookup": {
                    "from": "User",
                    "localField": "user",
                    "foreignField": "_id",
                    "as": "user"
                }
            },
            {
                "$set": {
                    "user": {
                        "$arrayElemAt": ["$user", 0]
                    }
                }
            },
            {
                "$project": {
                    "user": {"password": 0}
                }
            }
        ])
        review_list = [{**review,
                        "_id": str(review["_id"]),
                        "user": {**review["user"], "_id": str(review["user"]["_id"])},
                        "product": str(review["product"]),
                        "timestamps": review["timestamps"].isoformat()
                        } for review in review_list]
        return review_list, 200


class Review(Resource):
    @jwt_required()
    def post(self, review_id):
        user_id = ObjectId(get_jwt_identity()["_id"])
        product_id = ObjectId(review_id)
        if Reviews.find_one({"user": user_id, "product": product_id}):
            return {"message": 'You already made a comment on this product. According to our policy, each your can only make one review per product. Please consider modifying your posted review! Thank you'}, 400
        data = _review_parser.parse_args()
        data["user"] = user_id
        data["product"] = product_id
        data["timestamps"] = datetime.now()
        Reviews.insert_one(data)
        return {"message": "Review posted"}, 200

    @jwt_required()
    def put(self, review_id):
        _id = ObjectId(review_id)
        user_id = ObjectId(get_jwt_identity()["_id"])
        data = _review_parser.parse_args()
        review = Reviews.find_one({"_id": _id})
        if not review:
            return {"message": "Review Not Found"}, 404
        if review["user"] == user_id:
            review = {**review, **data}
            Reviews.update_one({"_id": _id}, {"$set": review})
            return {"message": "Review Updated"}, 200
        else:
            return {"message": "Unauthorized Request"}, 404

    @jwt_required()
    def delete(self, review_id):
        _id = ObjectId(review_id)
        identity = get_jwt_identity()
        user_id = ObjectId(identity["_id"])
        review = Reviews.find_one({"_id": _id})
        if not review:
            return {"message": "Review Not Found"}, 404
        if review["user"] == user_id or identity["isAdmin"]:
            Reviews.delete_one({"_id": _id})
            return {"message": "Review Deleted"}, 200
        else:
            return {"message": "Unauthorized Request"}, 404

