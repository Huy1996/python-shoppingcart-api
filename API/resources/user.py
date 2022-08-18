from API.models.user import Users
from flask_restful import Resource, reqparse, request
from bson.objectid import ObjectId
from configuration import flask_bcrypt
from pymongo import ReturnDocument
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from API.middleware.middleware import validate_request
from API.middleware.constant import PAGE_SIZE
from math import ceil

_user_parser = reqparse.RequestParser()
_user_parser.add_argument("name", type=str)
_user_parser.add_argument("password", type=str)
_user_parser.add_argument("email", type=str)


class UserRegister(Resource):
    def post(self):
        data = _user_parser.parse_args()
        data["password"] = flask_bcrypt.generate_password_hash(data["password"]).decode('utf8')
        if Users.find_one({"email": data["email"]}):
            return {'message': "This email already existed"}, 400
        Users.insert_one({**data, "isAdmin": False})
        return {'message': "Account create successful"}, 200


class User(Resource):
    @jwt_required()
    def get(self, user_id):
        _id = ObjectId(user_id)
        user = Users.find_one({"_id": _id}, {"password": 0})
        if user:
            return user, 200
        return {'message': "User is not exist"}, 400

    @validate_request(admin_only=True)
    def put(self, user_id):
        _id = ObjectId(user_id)

        data = _user_parser.parse_args()

        user = Users.find_one({"email": data["email"]})
        if user and user["_id"] != _id:
            return {'message': 'This is email already used by other account.'}, 400
        user = Users.find_one_and_update({"_id": _id},
                                         {"$set": {**data}},
                                         projection={"password": 0},
                                         return_document=ReturnDocument.AFTER)
        if user:
            user["_id"] = user_id
            return user, 200
        return {'message': "User is not exist."}, 400

    @validate_request(admin_only=True)
    def delete(self, user_id):
        _id = ObjectId(user_id)
        Users.delete_one({"_id": _id})
        return {'message': "User is deleted."}, 200


class UserLogin(Resource):
    def post(self):
        data = _user_parser.parse_args()

        user = Users.find_one({"email": data["email"]})
        if user and flask_bcrypt.check_password_hash(user["password"], data["password"]):
            return {
                "_id": str(user["_id"]),
                "name": user["name"],
                "email":  user["email"],
                "isAdmin": user["isAdmin"],
                "token": create_access_token(identity={"_id": str(user["_id"]), "isAdmin": user["isAdmin"]}, fresh=True),
                "refresh_token": create_refresh_token(str(user["_id"]))
            }, 200
        return {"message": "Invalid Credentials!"}, 401


class UserProfile(Resource):
    @jwt_required()
    def put(self):
        _id = ObjectId(get_jwt_identity()["_id"])
        data = _user_parser.parse_args()

        user = Users.find_one({"email": data["email"]})
        if user and user["_id"] != _id:
            return {'message': 'This is email already used by other account.'}, 400
        if data["password"]:
            data["password"] = flask_bcrypt.generate_password_hash(data["password"]).decode('utf8')

        user = Users.find_one_and_update({"_id": _id},
                                         {"$set": {**data}},
                                         projection={"password": 0},
                                         return_document=ReturnDocument.AFTER)
        return {
            "message": 'User Updated',
            "user": user
        }, 200


class UserList(Resource):
    @validate_request(admin_only=True)
    def get(self):
        page = int(request.args.get("pageNumber") or 1)
        count = Users.count_documents({})

        users_list = Users.find({}, {"password": 0})\
            .skip(PAGE_SIZE * (page - 1))\
            .limit(PAGE_SIZE)

        return {
            "users": list(users_list),
            "page": page,
            "pages": ceil(count / PAGE_SIZE)
        }, 200
