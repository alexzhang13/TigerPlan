from tokenize import String
from xmlrpc.client import DateTime
from app.models.models import TimeBlock, User
from app import db

def get_conflicts(userid: int) -> TimeBlock:
    """Get the user's conflicts. Returns a list of time blocks."""
    return db.session.query(TimeBlock).filter(TimeBlock.user_id == userid).all()

def user_from_netid(netid: String) -> User:
    """Get the user from the user's unique netid"""
    user = db.session.query(User).filter(User.netid == netid).one()
    return user

