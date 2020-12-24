from flask import request

from config import INDEX, db, es,USER_DATA
from flask_restplus import Resource, Namespace
from models.UserModel import UserModel
from models.EventModel import EventModel

api = Namespace('user', description='UsersRelatedApi')


@api.route('/', methods=['POST', 'GET'])
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


@api.route('/<user_id>', methods=['PUT', 'DELETE'])
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
