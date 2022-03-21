from tokenize import String
from xmlrpc.client import DateTime
from app.models.models import TimeBlock, User, Member_Group, Group
from app import db

def get_conflicts(userid: int) -> TimeBlock:
    """Get the user's conflicts. Returns a list of time blocks."""
    return db.session.query(TimeBlock).filter(TimeBlock.user_id == userid).all()

def user_from_netid(netid: String) -> User:
    """Get the user from the user's unique netid"""
    user = db.session.query(User).filter(User.netid == netid).one()
    return user

def get_user_groups(userid: int):
    """Get the user's member groups. Returns a list of groups."""
    groups = db.session.query(Group).filter(Group.owner_id == userid).all()
    return groups