from email.policy import default
from app import db, login
from flask_login import UserMixin

#---------------------------------------------------------------------#
class User(UserMixin, db.Model):
    __tablename__ = "users"

    # primitive fields
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    netid = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64))

    # 1-to-n relation fields
    owned_groups = db.relationship("Group")
    owned_events = db.relationship("Event")
    conflicts = db.relationship("TimeBlock")
    invitations = db.relationship("Invitation")

    # n-to-n relation fields
    groups = db.relationship("Member_Group", backref='member')

    def __repr__(self):
        return '<User {}>'.format(self.netid)

#---------------------------------------------------------------------#
class Group(db.Model):
    __tablename__ = "groups"

    # primitive fields
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    # 1-to-n relation fields
    events = db.relationship("Event", backref="group")

    # n-to-1 relation fields
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # n-to-n relation fields TODO: FIX
    members = db.relationship("Member_Group", backref="group")

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
    finalized = db.Column(db.Boolean, default=False)
    
    # 1-to-1 relation fields
    # chosen_time_id = db.Column(db.Integer, db.ForeignKey('timeblocks.id'))
    # chosen_time = db.relationship("TimeBlock",
    #     foreign_keys = "Event.chosen_time_id", uselist=False)
   
    # 1-to-n relation fields
    invitations = db.relationship("Invitation", backref="event")
    times = db.relationship("TimeBlock")

    # n-to-1 relation fields
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))

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
    is_conflict = db.Column(db.Boolean)
    is_recurring = db.Column(db.Boolean, default=False)

    # n-to-1 relation fields
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))

    # n-to-n 
    # invitee_responses = db.relationship("Invitation_Timeblock", backref='timeblock')

    def __repr__(self):
        return '<TimeBlock {}>'.format(self.id)

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "start": self.start.strftime('%Y-%m-%dT%H:%M:%S'),
            "end": self.end.strftime('%Y-%m-%dT%H:%M:%S'),
            "is_conflict": self.is_conflict,
            "is_recurring": self.is_recurring
        }

#---------------------------------------------------------------------#
class Invitation(db.Model): #DONE
    __tablename__ = "invitations"

    # primitive fields
    id = db.Column(db.Integer, primary_key=True)
    finalized = db.Column(db.Boolean, default=False)

    # n-to-1 relation fields
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # n-to-n
    responses = db.relationship("Invitation_Timeblock", backref='invitation')

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

    is_admin = db.Column(db.Boolean, default=False)

#---------------------------------------------------------------------#
# Associative table to facilitate n-to-n relationship between invitations, timeblocks
class Invitation_Timeblock(db.Model):
    __tablename__ = "invitation_timeblock"
    id = db.Column(db.Integer, primary_key=True)

    # n-to-n relation fields
    timeblock_id = db.Column(db.Integer, db.ForeignKey('timeblocks.id'))
    timeblock = db.relationship("TimeBlock", foreign_keys="Invitation_Timeblock.timeblock_id")

    invitation_id = db.Column(db.Integer, db.ForeignKey('invitations.id'))

    def __repr__(self):
        return '<Initation_Timeblock {}>'.format(self.id)

#---------------------------------------------------------------------#
@login.user_loader
def load_user(netid):
    return User.query.filter_by(netid=netid).first()