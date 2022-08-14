from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from configuration import flask_bcrypt
import os

from API.resources.user import UserRegister, User, UserLogin, UserList
from API.resources.upload import Upload

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
api = Api(app)


## JWT setup
jwt = JWTManager(app)




## Route setup
api.add_resource(UserRegister, '/user/register')
api.add_resource(User, '/user/<string:user_id>')
api.add_resource(UserLogin, '/user/login')
api.add_resource(UserList, '/user')

api.add_resource(Upload, '/upload')

if __name__ == "__main__":
    flask_bcrypt.init_app(app)
    app.run(port=3000, debug=True)

