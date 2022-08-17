from API.middleware.middleware import validate_request
from API.models.order import Orders
from API.models.product import Products
from API.models.user import Users
from flask_restful import Resource, reqparse, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime
from pprint import PrettyPrinter
from pymongo import UpdateOne
from pymongo.errors import BulkWriteError
from API.middleware.constant import PAGE_SIZE
from math import ceil

printer = PrettyPrinter()

_order_parser = reqparse.RequestParser()
_order_parser.add_argument("orderItems", type=list, location='json')
_order_parser.add_argument("shippingAddress", type=dict)
_order_parser.add_argument("paymentMethod", type=str)
_order_parser.add_argument("itemsPrice", type=float)
_order_parser.add_argument("shippingPrice", type=float)
_order_parser.add_argument("taxPrice", type=float)
_order_parser.add_argument("totalPrice", type=float)
_order_parser.add_argument("paymentResult", type=dict)


def update_product(cart_items):
    bulk_ops = [
        UpdateOne({"_id": ObjectId(item["product"])},
                  {"$inc": {"countInStock": -int(item["qty"])}})
        for item in cart_items]
    try:
        Products.bulk_write(bulk_ops)
    except BulkWriteError as error:
        printer.pprint(error)


class OrderList(Resource):
    @validate_request(admin_only=True)
    def get(self):
        page = int(request.args.get("pageNumber") or 1)
        count = Orders.count_documents({})
        order_list = Orders.aggregate([
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
                    "user": {"password": 0, "_id": 0, "isAdmin": 0}
                }
            },
            {"$skip": PAGE_SIZE * (page - 1)},
            {"$limit": PAGE_SIZE}

        ])
        order_list = [{
            **order,
            "_id": str(order["_id"]),
            "timestamps": order["timestamps"].isoformat()
        } for order in order_list]
        return {
                   "order": order_list,
                   "page": page,
                   "pages": ceil(count / PAGE_SIZE)
               }, 200

    @jwt_required()
    def post(self):
        _id = ObjectId(get_jwt_identity()["_id"])
        data = _order_parser.parse_args()

        if not data["orderItems"]:
            return {"message": 'Cart is empty'}, 404

        data["user"] = _id
        printer.pprint(data)
        initial_data = {
            "timestamps": datetime.now(),
            "isDelivered": False,
            "requestCancel": False,
            "isCanceled": False
        }

        Orders.insert_one({**data, **initial_data})
        update_product(data["orderItems"])
        return {"message": "New Order Created"}, 201


class OrderSummary(Resource):
    @validate_request(admin_only=True)
    def get(self):
        orders = Orders.aggregate([
            {
                "$group": {
                    "_id": None,
                    "numOrders": {"$sum": 1},
                    "totalSales": {"$sum": '$totalPrice'}
                }
            }
        ])

        users = Users.aggregate([
            {
                "$group": {
                    "_id": None,
                    "numUsers": {"$sum": 1}
                }
            }
        ])

        dailyOrders = Orders.aggregate([
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$createdAt"
                        }
                    },
                    "orders": {"$sum": 1},
                    "sales": {"$sum": "$totalPrice"}
                }
            },
            {"$sort": {"_id": 1}}
        ])

        productCategories = Products.aggregate([
            {
                "$group": {
                    "_id": '$category',
                    "count": {"$sum": 1},
                },
            }
        ])

        return {
            "users": users.next(),
            "orders": orders.next(),
            "dailyOrders": dailyOrders.next(),
            "productCategories": productCategories.next()
        }, 200


class PersonalOrderList(Resource):
    @jwt_required()
    def get(self):
        page = int(request.args.get("pageNumber") or 1)
        _id = ObjectId(get_jwt_identity()["_id"])
        count = Orders.count_documents({"user": _id})
        order_list = Orders.find({"user": _id})\
            .sort("createdAt", -1) \
            .skip(PAGE_SIZE * (page - 1)) \
            .limit(PAGE_SIZE)

        order_list = [{
            **order,
            "_id": str(order["_id"]),
            "user": str(order["user"]),
            "timestamps": order["timestamps"].isoformat()
        } for order in order_list]

        return {
            "orders": order_list,
            "page": page,
            "pages": ceil(count / PAGE_SIZE)
        }


class Order(Resource):
    @jwt_required()
    def get(self, order_id):
        _id = ObjectId(order_id)
        order = Orders.find_one({"_id": _id})
        if order:
            return {
                **order,
                "_id": str(order["_id"]),
                "user": str(order["user"]),
                "timestamps": order["timestamps"].isoformat()
            }, 200
        return {"message": "Order Not Found"}, 404

    @validate_request(admin_only=True)
    def delete(self, order_id):
        _id = ObjectId(order_id)
        order = Orders.find_one({"_id": _id})
        if order:
            Orders.delete_one({"_id": _id})
            return {"message": "Order Deleted"}, 200
        else:
            return {"message": "Order Not Found"}, 404


class UserOrder(Resource):
    @validate_request()
    def get(self, user_id):
        _id = ObjectId(user_id)
        page = int(request.args.get("pageNumber") or 1)
        count = Orders.count_documents({"user": _id})
        order_list = Orders.find({"user": _id})

        order_list = [{
            **order,
            "_id": str(order["_id"]),
            "user": str(order["user"]),
            "timestamps": order["timestamps"].isoformat()
        } for order in order_list]

        return {
            "orders": order_list,
            "count": count
        }


class DeliverOrder(Resource):
    @validate_request(admin_only=True)
    def put(self, order_id):
        _id = ObjectId(order_id)
        Orders.update_one(
            {"_id": _id},
            {
                "$set": {
                    "isDelivered": True,
                    "deliveredAt": datetime.now()
                }
            }
        )
        return {"message": "Order Delivered"}, 200


class RequestCancel(Resource):
    @jwt_required()
    def put(self, order_id):
        _id = ObjectId(order_id)
        user = ObjectId(get_jwt_identity()["_id"])
        if Orders.find_one({"_id": _id, "user": user}):
            Orders.update_one(
                {"_id": _id, "user": user},
                {
                    "$set": {
                        "requestCancel": True,
                        "requestedAt": datetime.now()
                    }
                }
            )
            return {"message": "Cancel requested"}, 200
        return {"message": "Order Not Found"}, 404


class CanceledOrder(Resource):
    @validate_request(admin_only=True)
    def put(self, order_id):
        _id = ObjectId(order_id)
        Orders.update_one(
            {"_id": _id},
            {
                "$set": {
                    "isCanceled": True,
                    "canceledAt": datetime.now()
                }
            }
        )
        return {"message": "Order Canceled"}, 200