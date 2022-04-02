from multiprocessing.sharedctypes import Value
from turtle import update
from app.models.models import Invitation, Invitation_Timeblock, TimeBlock, User, Event
from app.src.timeblock import get_timeblock
from app import db

#---------------------------- CRUD Functions -------------------------#
def create_invitation(userId: int, eventid: int) -> Invitation:
    """Create a invitation. Returns created invitation."""
    new_invite = Invitation(event_id=eventid, user_id = userId)
    db.session.add(new_invite)
    db.session.commit()
    return new_invite

def get_invitation(id: int) -> Invitation:
    """Get a invitation. Returns invitation."""
    return db.session.query(Invitation).filter(Invitation.id == id).one()

def delete_invitation(id: int) -> bool:
    """Delete a invitation. Returns true if successful."""
    del_invite = db.session.query(Invitation).filter(Invitation.id == id).one()
    db.session.delete(del_invite)
    db.session.commit()
    return del_invite.id == None

#------------------- Invitation_Timeblock Functions -------------------#
def create_invitation_timeblock(invitation_id: int, timeblock_id: int) -> Invitation:
    """Create a invitation. Returns created invitation."""
    new_invite = Invitation(event_id=eventid, user_id = userId)
    db.session.add(new_invite)
    db.session.commit()
    return new_invite

#---------------------------- Spec Functions -------------------------#
def get_proposed_times(id: int) -> TimeBlock:
    """Get the proposed times for this invitation's related event. Returns a list of Timeblocks."""
    times = db.session.query(TimeBlock).filter(TimeBlock.event_id == Invitation.event_id, Invitation.id == id).all()
    return times

def invitation_update_finalized(id: int, finalized: bool) -> Invitation:
    """Changes the invitation's finalization state. Returns the updated invitation"""
    updated_invite = db.session.query(Invitation).filter(Invitation.id == id).one()
    updated_invite.finalized = finalized
    db.session.add(updated_invite)
    db.session.commit()
    return updated_invite

def invitation_update_response(id: int, time_ids: int) -> Invitation:
    """Store member's selected times. Returns the updated invitation."""
    updated_invite = db.session.query(Invitation).filter(Invitation.id == id).one()

    for it_block in updated_invite.responses:
            db.session.delete(it_block)
    
    for time in time_ids:
        try:
            _ = get_timeblock(time)
        except Exception as ex:
            raise ValueError("Issue with timeblock id: " + time) from ex

        new_response = Invitation_Timeblock(timeblock_id=time, invitation_id=id)
        db.session.add(new_response)
    db.session.commit()
        
    return updated_invite