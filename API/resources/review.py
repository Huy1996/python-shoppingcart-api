from API.middleware.middleware import validate_request
from API.models.review import Reviews
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required


class UserReview(Resource):
    @validate_request()
    def get(self, user_id):
        pass


class ProductReview(Resource):
    def get(self, product_id):
        pass


class Review(Resource):
    @jwt_required()
    def post(self, review_id):
        pass

    @jwt_required()
    def put(self, review_id):
        pass

    @jwt_required()
    def delete(self, review_id):
        pass

