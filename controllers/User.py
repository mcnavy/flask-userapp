from flask import request

from config import INDEX, db, es, USER_DATA
from flask_restplus import Resource, Namespace
from models.UserModel import UserModel
from models.relations.UserEventRelation import UserEventLink

api = Namespace('user', description='UsersRelatedApi')


@api.route('/', methods=['POST', 'GET'])
class Users(Resource):
    def get(self):
        users = UserModel.query.all()

        results = [
            {
                'id': user.id,
                'name': user.name,
                'surname': user.surname,
                'bio': user.bio,
                'events': [link.event_id for link in UserEventLink.query.filter_by(user_id=user.id).all()]
            } for user in users
        ]
        return {'users': results}

    @api.expect(USER_DATA)
    def post(self):
        if request.is_json:
            data = request.get_json()

            new_user = UserModel(name=data['name'], surname=data['surname'], bio=data['bio'])
            db.session.add(new_user)
            db.session.commit()
            es.index(index=INDEX, id=new_user.id, body=data)
            return f'User {new_user.name} has been created'
        else:
            return 'Error, make sure you passed JSON'


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

            db.session.add(user)
            db.session.commit()
            es.update(index=INDEX, id=user.id, body={"doc": data})
            return f'User {user.id} has been updated'
        else:
            return 'Error, make sure you passed JSON'

    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        es.delete(index=INDEX, id=user.id)
        db.session.delete(user)
        db.session.commit()
        links = UserEventLink.query.filter_by(user=user.id).all()
        for link in links:
            db.session.delete(link)
            db.session.commit()
        return f'User {user.id} has been deleted'
