from config import db
from sqlalchemy import Index


class UserEventLink(db.Model):
    __tablename__ = 'user_event'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    event_id = db.Column(db.Integer)

    idx1 = Index('idx_user_event', user_id, event_id, id)
    idx2 = Index('idx_event_user', event_id, user_id, id)


    def __init__(self, user_id, event_id):
        self.user_id = user_id
        self.event_id = event_id

