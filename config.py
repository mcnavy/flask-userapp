from elasticsearch import Elasticsearch
from flask import Flask
from flask_migrate import Migrate
from flask_restplus import Api, fields
from flask_sqlalchemy import SQLAlchemy

INDEX = 'my_users'
es = Elasticsearch()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://USER:PASSWORD@localhost:5432/DB_NAME"

api = Api(app)


db = SQLAlchemy(app)
migrate = Migrate(app, db)
USER_DATA = api.model('User', {'name': fields.String('test'), 'surname': fields.String('test_surname'),
                               'bio': fields.String('this user has been born...'), 'events': fields.String('1 3 5 ')})
EVENT_DATA = api.model('Event', {'name': fields.String('example_event'), 'description': fields.String('description'),
                                 'users': fields.String('1 2 3')})