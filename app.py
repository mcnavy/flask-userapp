import os

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from elasticsearch import Elasticsearch
from flask_restplus import Resource, Api, fields, reqparse

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
parser = reqparse.RequestParser()
parser.add_argument('name', required=False)
parser.add_argument('surname', required=False)
parser.add_argument('bio', required=False)


class UserModel(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    surname = db.Column(db.String())
    bio = db.Column(db.String())
    assigned_events = db.Column(db.String())

    def __init__(self, name, surname, bio, assigned_events):
        self.name = name
        self.surname = surname
        self.bio = bio
        self.assigned_events = assigned_events


class EventModel(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    description = db.Column(db.String())
    assigned_users = db.Column(db.String())

    def __init__(self, name, description, assigned_users):
        self.name = name
        self.description = description
        self.assigned_users = assigned_users


@api.route('/smart_get', methods=['GET'])
class SmartGet(Resource):
    @api.expect(parser)
    def get(self):
        match = 0
        name, surname, bio = '', '', ''
        args = request.args
        if 'name' in args.keys():
            match += 1
            name = args['name']
        if 'surname' in args.keys():
            match += 1
            surname = args['surname']
        if 'bio' in args.keys():
            match += 1
            bio = args['bio']
        res = es.search(index=INDEX, body={"query": {"bool": {"should": [
            {
                "match": {
                    "name": {
                        'query': name,
                        'fuzziness': 1

                    }

                }
            },
            {
                "match": {
                    "bio": {
                        'query': bio,

                    }

                }
            },
            {
                "match": {
                    "surname": {
                        'query': surname,
                        'fuzziness': 1,

                    }
                }
            }
        ],
            "minimum_should_match": match
        }}})
        results = [{
            'name': hit['_source']['name'],
            'surname': hit['_source']['surname'],
            'bio': hit['_source']['bio']

        } for hit in res['hits']['hits'] if 1.4 * hit['_score'] >= res['hits']['max_score']]

        return {"Users": results}


@api.route('/users', methods=['POST', 'GET'])
class Users(Resource):
    @api.expect(USER_DATA)
    def post(self):
        if request.is_json:
            data = request.get_json()
            new_user = UserModel(name=data['name'], surname=data['surname'], bio=data['bio'],
                                 assigned_events=data['events'])

            db.session.add(new_user)
            db.session.commit()
            es.index(index=INDEX, id=new_user.id, body=data)
            return f'User {new_user.name} has been created'
        else:
            return 'Error, make sure you passed JSON'

    def get(self):
        users = UserModel.query.all()
        results = [
            {
                'id': user.id,
                'name': user.name,
                'surname': user.surname,
                'bio': user.bio,
                'events': user.assigned_events

            } for user in users
        ]
        return {'users': results}


@api.route('/users/<user_id>', methods=['PUT', 'DELETE'])
class UpdateUsers(Resource):
    @api.expect(USER_DATA)
    def put(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        if request.is_json:

            data = request.get_json()
            if 'name' in data.keys():
                user.name = data['name']
            if 'surname' in data.keys():
                user.surname = data['surname']
            if 'bio' in data.keys():
                user.bio = data['bio']
            if 'events' in data.keys():
                user.assigned_events = data['events']

            db.session.add(user)
            db.session.commit()
            es.update(index=INDEX, id=user.id, body={"doc": data})
            return f'User {user.id} has been updated'
        else:
            return 'Error, make sure you passed JSON'

    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        es.delete(index=INDEX, id=user.id)
        events = EventModel.query.all()
        for event in events:
            users = event.assigned_users.split()
            if str(user.id) in users:
                del users[users.index(str(user.id))]
            event.assigned_users = ''.join(users)
            db.session.add(event)
            db.session.commit()

        db.session.delete(user)
        db.session.commit()

        return f'User {user.id} has been deleted'


@api.route('/events', methods=['POST', 'GET'])
class Events(Resource):
    @api.expect(EVENT_DATA)
    def post(self):
        if request.is_json:
            data = request.get_json()

            new_event = EventModel(name=data['name'], description=data['description'], assigned_users=data['users'])

            db.session.add(new_event)
            db.session.commit()
            return f'Event {new_event.name} has been created.'
        else:
            return 'Not json'

    def get(self):
        events = EventModel.query.all()
        results = [
            {
                'id': event.id,
                'name': event.name,
                'description': event.description,
                'users': event.assigned_users
            } for event in events
        ]
        return {'events': results}


@api.route('/events/<event_id>', methods=['PUT', 'DELETE'])
class UpdateEvents(Resource):
    @api.expect(EVENT_DATA)
    def put(self, event_id):
        event = EventModel.query.get_or_404(event_id)

        if request.method == 'PUT':
            if request.is_json:

                data = request.get_json()
                if 'name' in data.keys():
                    event.name = data['name']
                if 'description' in data.keys():
                    event.description = data['description']
                if 'users' in data.keys():
                    event.assigned_users = data['users']
                db.session.add(event)
                db.session.commit()

                return f'User {event.id} has been updated'
            else:
                return 'Error, make sure you passed JSON'

    def delete(self, event_id):
        event = EventModel.query.get_or_404(event_id)
        users = UserModel.query.all()
        for user in users:
            events = user.assigned_events.split()
            if str(event.id) in events:
                del events[events.index(str(event.id))]
            user.assigned_events = ''.join(events)
            db.session.add(user)

            db.session.delete(event)
            db.session.commit()

            return f'User {event.id} has been deleted'


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
