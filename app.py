from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from configuration import flask_bcrypt
import os

from API.resources.user import UserRegister, User, UserLogin, UserList
from API.resources.upload import Upload
from API.resources.product import ProductsList, CategoryList, BrandList, Product

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['PROPAGATE_EXCEPTIONS'] = True
api = Api(app)


## JWT setup
jwt = JWTManager(app)




## Route setup
api.add_resource(UserRegister, '/users/register')
api.add_resource(User, '/users/<string:user_id>')
api.add_resource(UserLogin, '/users/login')
api.add_resource(UserList, '/users')

api.add_resource(Upload, '/uploads')

api.add_resource(ProductsList, '/products')
api.add_resource(CategoryList, '/products/categories')
api.add_resource(BrandList, '/products/brands')
api.add_resource(Product, '/products/<string:product_id>')

if __name__ == "__main__":
    flask_bcrypt.init_app(app)
    app.run(port=3000, debug=True)

