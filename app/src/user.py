from sqlite3 import Time
from tokenize import String
from app.models.models import Invitation, Member_Group, TimeBlock, User, Group, Event
from app import db

#---------------------------- Spec Functions -------------------------#
def get_user_from_id(id: int) -> User:
    """Get the user from the user's id"""
    return db.session.query(User).filter(User.id == id).one()

def get_users() -> User:
    """Get all users"""
    return db.session.query(User).all()

def get_user_from_netid(netid: String) -> User:
    """Get the user from the user's unique netid"""
    user = db.session.query(User).filter(User.netid == netid).one()
    return user

def get_user_conflicts(userid: int) -> TimeBlock:
    """Get the user's conflicts. Returns a list of time blocks."""
    return db.session.query(TimeBlock).filter(TimeBlock.user_id == userid).all()

def get_user_recurring_conflicts(userid: int) -> TimeBlock:
    """Get the user's recurring conflicts. Returns a list of time blocks."""
    return db.session.query(TimeBlock).filter(
        TimeBlock.user_id == userid,
        TimeBlock.is_recurring == True
    ).all()

def get_user_onetime_conflicts(userid: int) -> TimeBlock:
    """Get the user's onetime (non-recurring) conflicts. Returns a list of time blocks."""
    return db.session.query(TimeBlock).filter(
        TimeBlock.user_id == userid,
        TimeBlock.is_recurring == False
    ).all()

def get_user_groups(userid: int) -> Group:
    """Get the user(owner)'s groups. Returns a list of groups."""
    groups = db.session.query(Group).filter(Group.owner_id == userid).all()
    return groups

def get_user_events(userid: int) -> Event:
    """Get the user(owner)'s events. Returns a list of events."""
    events = db.session.query(Event).filter(Event.owner_id == userid).all()
    return events

def get_user_member_finalized_event_times(userid: int) -> TimeBlock:
    '''Get the timeblock for every finalized event the user is a part of.'''
    finalized_event_timeblocks = db.session.query(TimeBlock).filter(
        Event.group_id == Member_Group.group_id,
        Member_Group.member_id == userid,
        Event.finalized == True,
        TimeBlock.event_id == Event.id
    ).all()
    return finalized_event_timeblocks

def get_admin_groups(userid: int) -> Group:
    '''Get the user(admin)'s groups. Returns a list of groups.'''
    groups = db.session.query(Group).filter(Group.id == Member_Group.group_id, Member_Group.member_id == userid, Member_Group.is_admin == True).all()
    return groups

# TODO: TEST
def get_member_groups(memberid: int) -> Group:
    """Get the user(member)'s groups. Returns a list of groups."""
    mem_groups = db.session.query(Group).filter( 
        Member_Group.group_id == Group.id, Member_Group.member_id == memberid).all()
    return mem_groups

# TODO: TEST
def get_member_events(memberid: int) -> Event:
    """Get the user(member)'s events. Returns a list of events."""
    mem_events = db.session.query(Event).filter(
        Event.group_id == Member_Group.group_id, Member_Group.member_id == memberid).all()
    return mem_events

# TODO: TEST
def get_member_invitations(memberid: int) -> Invitation:
    """Get the user(member)'s invitations pending response. Returns a list of invitations."""
    mem_invs = db.session.query(Invitation).filter(
        Invitation.user_id == memberid).all()
    return mem_invs

