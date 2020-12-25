from flask import request

from config import EVENT_DATA, db
from flask_restplus import Resource, Namespace
from models.EventModel import EventModel
from models.relations.UserEventRelation import UserEventLink

api = Namespace('event', description='EventsRelatedApi')


@api.route('/', methods=['POST', 'GET'])
class Events(Resource):
    @api.expect(EVENT_DATA)
    def post(self):
        if request.is_json:
            data = request.get_json()

            new_event = EventModel(name=data['name'], description=data['description'])

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
                'users': [link.user_id for link in UserEventLink.query.filter_by(event_id=event.id).all()]
            } for event in events
        ]
        return {'events': results}


@api.route('/<event_id>', methods=['PUT', 'DELETE'])
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
                db.session.add(event)
                db.session.commit()

                return f'User {event.id} has been updated'
            else:
                return {'code': 400, 'message': 'Error, make sure you passed JSON'}

    def delete(self, event_id):
        event = EventModel.query.get_or_404(event_id)

        db.session.delete(event)
        db.session.commit()
        links = UserEventLink.query.filter_by(
            user_id=event.id
        ).all()
        for link in links:
            db.session.delete(link)
            db.session.commit()

        return f'User {event.id} has been deleted'
