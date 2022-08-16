from API.middleware.middleware import validate_request
from API.models.order import Orders
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity


class OrderList(Resource):
    @validate_request(admin_only=True)
    def get(self):
        pass

    @jwt_required()
    def post(self):
        pass


class OrderSummary(Resource):
    @validate_request(admin_only=True)
    def get(self):
        pass


class PersonalOrderList(Resource):
    @jwt_required()
    def get(self):
        pass


class Order(Resource):
    @jwt_required()
    def get(self, order_id):
        pass

    @validate_request(admin_only=True)
    def delete(self, order_id):
        pass


class UserOrder(Resource):
    @validate_request()
    def get(self, user_id):
        pass


class PayOrder(Resource):
    @jwt_required()
    def put(self, order_id):
        pass


class DeliverOrder(Resource):
    @validate_request(admin_only=True)
    def put(self, order_id):
        pass


class RequestCancel(Resource):
    @jwt_required()
    def put(self, order_id):
        pass


class CanceledOrder(Resource):
    @validate_request(admin_only=True)
    def put(self, order_id):
        pass

