from app.models.models import Invitation, Invitation_Timeblock, TimeBlock, User, Event
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

def update_invitation(id: int, name: str) -> Invitation:
    """Update a invitation. Returns updated invitation."""
    updated_invite = db.session.query(Invitation).filter(Invitation.id == id).one()
    if name is not None:
        updated_invite.name = name
    db.session.add(updated_invite)
    db.session.commit()
    return updated_invite

def delete_invitation(id: int) -> bool:
    """Delete a invitation. Returns true if successful."""
    del_invite = db.session.query(Invitation).filter(Invitation.id == id).one()
    db.session.delete(del_invite)
    db.session.commit()
    return del_invite.id == None

#---------------------------- Spec Functions -------------------------#
def get_proposed_times(id: int) -> TimeBlock:
    """Get the proposed times for this invitation's related event. Returns a list of Timeblocks."""
    times = db.session.query(TimeBlock).filter(TimeBlock.event_id == Invitation.event_id, Invitation.id == id).all()
    return times

def update_response(id: int, time_ids: int) -> Invitation:
    """Store member's selected times. Returns the updated invitation."""
    for time in time_ids:
        new_response = Invitation_Timeblock(timeblock_id=time, invitation_id=id)
        db.session.add(new_response)
    db.session.commit()
    return db.Query(Invitation).filter(Invitation.id == id).one()