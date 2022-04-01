from xmlrpc.client import DateTime
import app
from app.models.models import Invitation, Invitation_Timeblock, TimeBlock, Member_Group, User, Event
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
    del_responses = db.session.query(Invitation_Timeblock).filter(Invitation.event_id == id, Invitation_Timeblock.invitation_id == Invitation.id).all()
    for del_response in del_responses:
        db.session.delete(del_response)
    for del_invitation in del_invitations:
        db.session.delete(del_invitation)
    db.session.delete(del_event)
    db.session.commit()
    return del_event.id == None

#---------------------------- Spec Functions -------------------------#
# TODO: This should most likely also throw out old invitations
def set_proposed_times(id: int, datetimes: DateTime) -> Event:
    """Sets the proposed time for an event. Returns the modifed event.
    Takes in the parameters datetimes as an list of tuples, where the 
    tuple is organized as (starttime, endtime)."""
    event = get_event(id)

    # Throws out previous times
    for tb in event.times:
        db.session.delete(tb)

    for i, start_end in enumerate(datetimes):
        tb = TimeBlock(start = start_end[0], end = start_end[1], is_conflict = False, event_id = event.id)
        db.session.add(tb)

    db.commit()
    return event

# def create_event_unattached(name: str, owner: User, location: str, description: str) -> Event:
#     """Create an event. Returns created event."""
#     new_event = Event(name=name,
#                       owner_id=owner.id,
#                       location=location,
#                       description=description)
#     db.session.add(new_event)
#     db.session.commit()
#     return new_event

def create_event_invitations(id: int) -> Invitation:
    """Sends an invitation to every group member of the event."""
    members = db.session.query(User).filter(
        User.id == Member_Group.member_id, 
        Member_Group.group_id == Event.group_id, 
        Event.id == id).all()
    for member in members:
        create_invitation(member.id, id)
    return db.session.query(Invitation).filter(Invitation.event_id == id).all()

def get_invitation_response_times(id: int) -> dict:
    """Calculates time availabilites for an event by checking member 
    invitation reponses. Returns a dictionary mapping timeblock ids to 
    the amount of members available at that time."""
    event = get_event(id)
    time_counts = {}
    for invite in event.invitations:
        if not invite.finalized:
            continue
        for response in invite.responses:
            timeblock_id = response.timeblock_id
            if response.timeblock_id in time_counts:
                time_counts[timeblock_id] += 1
            else: 
                time_counts[timeblock_id] = 1
    return time_counts