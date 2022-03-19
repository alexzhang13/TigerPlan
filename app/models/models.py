from app import db, login
from flask_login import UserMixin
# may need to import DateTime from SQL Alchemy

#---------------------------------------------------------------------#
class User(UserMixin, db.Model):
    __tablename__ = "users"

    # primitive fields
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    netid = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64))

    # 1-to-n relation fields
    owned_groups = db.relationship("Group") # may need backref
    owned_events = db.relationship("Event")
    conflicts = db.relationship("TimeBlock")
    invitations = db.relationship("Invitation")

    # n-to-n relation fields
    member_groups = db.relationship("Member_Group", backref='member')

    def __repr__(self):
        return '<User {}>'.format(self.netid)

#---------------------------------------------------------------------#
class Group(db.Model):
    __tablename__ = "groups"

    # primitive fields
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    # 1-to-n relation fields
    events = db.relationship("Event")

    # n-to-1 relation fields
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # n-to-n relation fields
    members = db.relationship("Member_Group", backref='group')

    def __repr__(self):
        return '<Group {}>'.format(self.id)

#---------------------------------------------------------------------#
class Event(db.Model):
    __tablename__ = "events"

    # primitive fields
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    description = db.Column(db.String(64))

    # 1-to-n relation fields
    invitations = db.relationship("Invitation")

    # n-to-1 relation fields
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))

    #IMPLEMENT: groups, individual invitees?

    def __repr__(self):
        return '<Model {}>'.format(self.id)

#---------------------------------------------------------------------#
class TimeBlock(db.Model): #DONE
    __tablename__ = "timeblocks"

    # primitive fields
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64)) 
    start = db.Column(db.DateTime())
    end = db.Column(db.DateTime())

    # n-to-1 relation fields
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<TimeBlock {}>'.format(self.id)

#---------------------------------------------------------------------#
class Invitation(db.Model): #DONE
    __tablename__ = "invitations"
    # primitive fields
    id = db.Column(db.Integer, primary_key=True)

    # n-to-1 relation fields
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<Invitation {}>'.format(self.id)

#---------------------------------------------------------------------#
# Associative table to facilitate n-to-n relationship between members, groups
class Member_Group(db.Model):
    __tablename__ = "member_group"
    id = db.Column(db.Integer, primary_key=True)

    # n-to-n relation fields
    member_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))


#---------------------------------------------------------------------#
@login.user_loader
def load_user(netid):
    return User.query.filter_by(id=netid).first()