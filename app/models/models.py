from app import db, login
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.String(64), primary_key=True)
    netid = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64))
    name = db.Column(db.String(64))
    # owned groups
    # member groups
    # conflicts
    # owned events
    # invitations

    def __repr__(self):
        return '<User {}>'.format(self.netid)

class Group(db.Model):
    __tablename__ = "group"
    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(64)) #unique
    owner = db.Column(User)
    members = db.Column(list(User))
    # events
    def __repr__(self):
        return '<Group {}>'.format(self.id)

class Event(db.Model):
    __tablename__ = "event"
    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(64)) #unique
    owner = db.Column(User)
    invitees = db.Column(list(User))
    location = db.Column(db.String(64))
    description = db.Column(db.String(64))
    # time(s)
    # duration
    # status
    def __repr__(self):
        return '<Model {}>'.format(self.id)

class TimeBlock(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(64)) 
    # start
    # end
    user = db.Column(User)
    def __repr__(self):
        return '<TimeBlock {}>'.format(self.id)

class Invitation(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    event = db.Column(Event)
    # metadata
    # response enum
    def __repr__(self):
        return '<Invitation {}>'.format(self.id)

@login.user_loader
def load_user(netid):
    return User.query.filter_by(id=netid).first()