from config import db


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
