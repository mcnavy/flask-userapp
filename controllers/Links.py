from flask_restplus import Resource, Namespace

from config import db
from models.relations.UserEventRelation import UserEventLink

api = Namespace('links', description='LinksApi')


@api.route('/link/<user_id>/<event_id>', methods=['POST', 'DELETE'])
class ManageLinks(Resource):
    def post(self, user_id, event_id):
        new_link = UserEventLink(user_id, event_id)
        db.session.add(new_link)
        db.session.commit()
        return 'Link created'

    def delete(self, user_id, event_id):
        link = UserEventLink.query.filter_by(
            user_id=user_id,
            event_id=event_id
        ).first()
        db.session.delete(link)
        db.session.commit()
        return 'Link deleted'
