from app import db, login
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.String(64))
    netid = db.Column(db.String(64), primary_key=True)
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
    # owner
    # members
    # events
    def __repr__(self):
        return '<Group {}>'.format(self.id)

class Event(db.Model):
    __tablename__ = "event"
    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(64)) #unique
    # owner
    # invitees
    # location
    # description
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
    # user

class Invitation(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    event = db.Column(Event)
    # metadata
    # response enum

@login.user_loader
def load_user(netid):
    return User.query.filter_by(id=netid).first()