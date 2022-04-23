from datetime import datetime
from webbrowser import get
from xmlrpc.client import DateTime
import app
from app.models.models import Invitation, Invitation_Timeblock, TimeBlock, Member_Group, User, Event
from app.src.invitation import create_invitation
from app.src.timeblock import create_event_timeblock, get_timeblock
from flask import request
from app import db, login

#---------------------------- CRUD Functions -------------------------#

def create_event(name: str, owner: User, location: str, description: str, groupid: int, timeblocks) -> Event:
    """Create an event. Returns created event."""
    new_event = Event(group_id=groupid, 
                      name=name,
                      owner_id=owner.id,
                      location=location,
                      description=description)
    db.session.add(new_event)
    
    # make sure id is accessable
    db.session.flush()

    for timeblock in timeblocks:
        start = datetime.fromisoformat(timeblock['start']['_date'][:-1])
        end = datetime.fromisoformat(timeblock['end']['_date'][:-1])
        name = timeblock['name']
        _ = create_event_timeblock(eventId=new_event.id, start=start, end=end, name=name, isconflict=False, commit=False)

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
    for timeblock in del_event.times:
        db.session.delete(timeblock)

    db.session.delete(del_event)
    db.session.commit()
    return del_event.id == None

#---------------------------- Spec Functions -------------------------#
def set_proposed_times(id: int, datetimes: DateTime) -> Event:
    """Sets the proposed time for an event. Returns the modifed event.
    Takes in the parameters datetimes as an list of tuples, where the 
    tuple is organized as (starttime, endtime)."""
    event = get_event(id)

    # Throws out previous times
    for tb in event.times:
        db.session.delete(tb)

    for start_end in datetimes:
        tb = TimeBlock(start = start_end[0], end = start_end[1], is_conflict = False, event_id = event.id)
        db.session.add(tb)

    db.commit()
    return event

def event_finalize(eventid: int, timeid: int) -> Invitation:
    """Changes the event's finalization state. Returns the updated event. If the event is already finalized, throws an exception."""
    event = get_event(eventid)
    if event.finalized:
        raise Exception("Event is already finalized")
    
    # TODO: Should make sure timeblock exists/exists in event (although
    # could just add back if not in event)



    # throw out all invitation responses
    for invitation in event.invitations:
        for response in invitation.responses:
            db.session.delete(response)
    # throw out all timeblocks except matching timeblock
    selected_timeblock = get_timeblock(timeid)
    for tb in event.times:
        print(tb.id)
        if (tb == selected_timeblock):
            print("not deleting", tb)
            continue
        print("deleting", tb)
        db.session.delete(tb)

    event.finalized = True

    db.session.add(event)
    db.session.commit()
    return event

def event_set_chosen_time(id: int, timeblockid: int) -> Event:
    """Sets the chosen time for the event. Returns the updated event."""
    event = get_event(id)
    event.chosen_time = timeblockid
    db.session.add(event)
    db.session.commit()
    return event

def create_event_invitations(id: int) -> Invitation:
    """Sends an invitation to every group member of the event."""
    event = get_event(id)
    if len(event.invitations) != 0:
        return
    members = db.session.query(User).filter(
        User.id == Member_Group.member_id, 
        Member_Group.group_id == Event.group_id, 
        Event.id == id).all()
    for member in members:
        create_invitation(member.id, id)
    return db.session.query(Invitation).filter(Invitation.event_id == id).all()

def get_invitation_response_times(id: int) -> dict:
    """Calculates time availabilites for an event by checking member 
    invitation reponses. Returns a dictionary mapping timeblocks to 
    the amount of members available at that time, and a count of the
    total number of responses."""
    event = get_event(id)
    time_counts = {}
    num_responses = 0

    for invite in event.invitations:
        if not invite.finalized:
            continue
        num_responses += 1
        for response in invite.responses:
            timeblock = get_timeblock(response.timeblock_id)
            if timeblock in time_counts:
                time_counts[timeblock] += 1
            else: 
                time_counts[timeblock] = 1

    response_times = []
    for time in event.times:
        availability = 0
        if time in time_counts:
            availability = time_counts[time]
        block = {
            "id": time.id,
            "start": time.start.strftime('%Y-%m-%dT%H:%M:%S'),
            "end": time.end.strftime('%Y-%m-%dT%H:%M:%S'),
            "availability": availability
        }

        response_times.append(block)
    print("Response times!:", response_times)

    return response_times, num_responses