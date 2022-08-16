from API.models.product import Products
from API.models.review import Reviews
from flask_restful import request, reqparse, Resource
from flask_jwt_extended import jwt_required
from API.middleware.middleware import validate_request


# /product
class ProductsList(Resource):
    def get(self):
        pass

    @validate_request(admin_only=True)
    def post(self):
        pass


# /product/categories
class CategoryList(Resource):
    def get(self):
        pass


# /product/brands
class BrandList(Resource):
    def get(self):
        pass


# /product/<string:product_id>
class Product(Resource):
    def get(self, product_id):
        pass

    @validate_request(admin_only=True)
    def put(self, product_id):
        pass

    @validate_request(admin_only=True)
    def delete(self, product_id):
        pass


# /product/<string:product_id>/reviews
class ProductReview(Resource):
    @validate_request(admin_only=True)
    def post(self, product_id):
        pass

