import app
from app.models.models import Invitation, Invitation_Timeblock, Member_Group, User, Event
from app.src.invitation import create_invitation
from flask import request
from app import db, login

#---------------------------- CRUD Functions -------------------------#

def create_event(name: str, owner: User, location: str, description: str, groupid: int) -> Event:
    """Create an event. Returns created event."""
    new_event = Event(group_id=groupid, 
                      name=name,
                      owner_id=owner.id,
                      location=location,
                      description=description)
    db.session.add(new_event)
    db.session.commit()
    return new_event

def get_event(id: int) -> Event:
    """Get an event. Returns event."""
    return db.session.query(Event).filter(Event.id == id).one()

def update_event(id: int, name: str, location: str, description: str) -> Event:
    """Update an event. Returns updated event."""
    updated_event = db.session.query(Event).filter(Event.id == id).one()
    if name is not None:
        updated_event.name = name
    if location is not None:
        updated_event.location = location
    if description is not None:
        updated_event.description = description
    db.session.add(updated_event)
    db.session.commit()
    return updated_event

def delete_event(id: int) -> bool:
    """Delete an event and its associated invitations, if any. Returns true if successful."""
    del_event = db.session.query(Event).filter(Event.id == id).one()
    del_invitations = db.session.query(Invitation).filter(Invitation.event_id == id).all()
    del_responses = db.session.query(Invitation_Timeblock).filter(Invitation.event_id == id, Invitation_Timeblock.invitation_id == Invitation.id)
    db.session.delete(del_event)
    db.session.delete(del_invitations)
    db.session.delete(del_responses)
    db.session.commit()
    return del_event.id == None

#---------------------------- Spec Functions -------------------------#
def create_event_unattached(name: str, owner: User, location: str, description: str) -> Event:
    """Create an event. Returns created event."""
    new_event = Event(name=name,
                      owner_id=owner.id,
                      location=location,
                      description=description)
    db.session.add(new_event)
    db.session.commit()
    return new_event

def create_event_invitations(id: int) -> Invitation:
    members = db.session.query(User).filter(
        User.id == Member_Group.member_id, 
        Member_Group.group_id == Event.group_id, 
        Event.id == id).all()
    for member in members:
        create_invitation(member, id)
    return db.session.query(Invitation).filter(Invitation.event_id == id)