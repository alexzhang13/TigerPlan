from tokenize import String
from app.models.models import TimeBlock, User, Group, Event
from app import db

#---------------------------- Spec Functions -------------------------#
def get_user_from_netid(netid: String) -> User:
    """Get the user from the user's unique netid"""
    user = db.session.query(User).filter(User.netid == netid).one()
    return user

def get_user_conflicts(userid: int) -> TimeBlock:
    """Get the user's conflicts. Returns a list of time blocks."""
    return db.session.query(TimeBlock).filter(TimeBlock.user_id == userid).all()

def get_user_groups(userid: int) -> Group:
    """Get the user(owner)'s groups. Returns a list of groups."""
    groups = db.session.query(Group).filter(Group.owner_id == userid).all()
    return groups

def get_user_events(userid: int) -> Event:
    """Get the user(owner)'s events. Returns a list of eents."""
    events = db.session.query(Event).filter(Event.owner_id == userid).all()
    return events