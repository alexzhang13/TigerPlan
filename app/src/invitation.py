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
    """Create a invitation_timeblock. Returns created 
    invitation_timeblock. DOES NOT COMMIT CREATION"""
    new_invtb = Invitation_Timeblock(timeblock_id=timeblock_id, invitation_id=invitation_id)
    db.session.add(new_invtb)
    return new_invtb

#---------------------------- Spec Functions -------------------------#
def get_proposed_times(id: int) -> TimeBlock:
    """Get the proposed times for this invitation's related event. Returns a list of Timeblocks."""
    times = db.session.query(TimeBlock).filter(TimeBlock.event_id == Invitation.event_id, Invitation.id == id).all()
    return times

def invitation_finalize(id: int, timeblocks: int) -> Invitation:
    """Finalizes the invitation using the given timeblocks. Returns the updated invitation"""
    invitation = get_invitation(id)
    
    if (invitation.finalized):
        raise ValueError("Invitation is already finalized")
    invitation.finalized = True
    for timeid in timeblocks:
        try:
            _ = get_timeblock(timeid)
        except Exception as ex:
            raise ValueError("Issue with timeblock id: " + timeid) from ex
        new_response = Invitation_Timeblock(timeblock_id=timeid, invitation_id=id)
        db.session.add(new_response)
    db.session.add(invitation)
    db.session.commit()
    return invitation