from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from dotenv import dotenv_values


from db import db

configuration = dotenv_values(".env")
app = Flask(__name__)
app.config['MONGOALCHEMY_DATABASE'] = 'Shopping-Cart'
app.config['MONGOALCHEMY_SERVER'] = 'localhost'
app.config['MONGOALCHEMY_PORT'] = 27017

api = Api(app)

app.config['JWT_SECRET_KEY'] = configuration['JWT_KEY']
jwt = JWTManager(app)

if __name__ == "__main__":
    db.init_app(app)
    app.run(port=3000, debug=True)