from API.models.product import Products
from flask_restful import request, reqparse, Resource
from API.middleware.middleware import validate_request
from pprint import PrettyPrinter
from API.middleware.constant import PAGE_SIZE
from math import ceil
from bson.objectid import ObjectId

_product_parser = reqparse.RequestParser()
_product_parser.add_argument("name", type=str)
_product_parser.add_argument("image", type=str)
_product_parser.add_argument("price", type=float)
_product_parser.add_argument("category", type=str)
_product_parser.add_argument("brand", type=str)
_product_parser.add_argument("countInStock", type=int)
_product_parser.add_argument("attribute", type=list, location='json')
_product_parser.add_argument("description", type=str)


# /product
class ProductsList(Resource):
    def get(self):
        # Query parameter
        page = int(request.args.get("pageNumber") or 1)
        name = request.args.get("name") or ''
        category = request.args.get("category") or ''
        brand = request.args.get("brand") or ''
        order = request.args.get("order") or ''
        _min = int(request.args.get("min") or 0)
        _max = int(request.args.get("max") or 0)
        rating = int(request.args.get("rating") or 0)

        name_filter = {"name": {"$regex": name, "$options": 'i'}} if name else {}
        category_filter = {"category": category} if category else {}
        brand_filter = {"brand": brand} if brand else {}
        price_filter = {"price": {"$gte": _min, "$lte": _max}} if _max and _min else {}
        rating_filter = {"rating": {"$gte": rating}} if rating else {}
        sort_order = ["price", 1] if order == "lowest" else \
            ["price", -1] if order == "highest" else \
                ["rating", -1] if order == "toprated" else \
                    ["_id", -1]


        # count matching data
        count = Products.count_documents({
            **name_filter,
            **category_filter,
            **brand_filter,
            **price_filter,
            **rating_filter
        })

        product_list = Products.find({
            **name_filter,
            **category_filter,
            **brand_filter,
            **price_filter,
            **rating_filter
        })\
            .sort(*sort_order)\
            .skip(PAGE_SIZE * (page - 1))\
            .limit(PAGE_SIZE)


        return {
            "products": list(product_list),
            "page": page,
            "pages": ceil(count / PAGE_SIZE)
        }, 200

    @validate_request(admin_only=True)
    def post(self):
        data = _product_parser.parse_args()
        product = Products.insert_one({**data, "rating": 0, "numReviews": 0})

        printer = PrettyPrinter()
        printer.pprint(data)
        return {}, 200



# /product/categories
class CategoryList(Resource):
    def get(self):
        categories = Products.find().distinct("category")
        return {"categories": list(categories)}, 200


# /product/brands
class BrandList(Resource):
    def get(self):
        brands = Products.find().distinct("brand")
        return {"brands": list(brands)}, 200


# /product/<string:product_id>
class Product(Resource):
    def get(self, product_id):
        _id = ObjectId(product_id)
        product = Products.find_one({"_id": _id})
        if product:
            return product, 200
        else:
            return {"message": "Product Not Found"}, 404

    @validate_request(admin_only=True)
    def put(self, product_id):
        _id = ObjectId(product_id)
        data = _product_parser.parse_args()
        product = Products.find_one({"_id": _id})
        if product:
            product = {**product, **data}
            Products.update_one({"_id": _id},{"$set": product})
            return {"message": "Product Updated"}, 200
        else:
            return {"message": "Product Not Found"}, 404

    @validate_request(admin_only=True)
    def delete(self, product_id):
        _id = ObjectId(product_id)
        product = Products.find_one({"_id": _id})
        if product:
            Products.delete_one({"_id": _id})
            return {"message": "Product Deleted"}, 200
        else:
            return {"message": "Product Not Found"}, 404


