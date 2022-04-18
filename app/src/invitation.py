from multiprocessing.sharedctypes import Value
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

# NOT USED
def invitation_update_finalized(id: int, finalized: bool) -> Invitation:
    """Changes the invitation's finalization state. Returns the updated invitation"""
    try:
        invitation = get_invitation(id)
        if (invitation.event.finalized):
            raise ValueError("Event is already finalized")
    except Exception as ex:
        raise ValueError(str(ex)) from ex
    invitation.finalized = finalized
    db.session.add(invitation)
    db.session.commit()
    return invitation

def invitation_finalize(id: int, timeblocks: int) -> Invitation:
    """Finalizes the invitation using the given timeblocks. Returns the updated invitation"""
    invitation = get_invitation(id)
    
    # TODO: Decide if we want this
    # if (invitation.event.finalized):
    #     raise ValueError("Event is already finalized")
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

# SHOULD NOT BE USED. SEE invitation_finalize
def invitation_add_response_time(id: int, timeid: int) -> Invitation:
    """Adds a specified time to the invitation. If such a time already exists, do nothing."""
    try:
        invitation = get_invitation(id)
        if (invitation.event.finalized):
            raise ValueError("Event is already finalized")
    except Exception as ex:
        raise ValueError(str(ex)) from ex

    itblock = db.session.query(Invitation_Timeblock).filter(Invitation_Timeblock.timeblock_id == timeid).first()

    if itblock is not None:
        return invitation
    
    try:
        _ = get_timeblock(timeid)
    except Exception as ex:
        raise ValueError("Issue with timeblock id: " + timeid) from ex

    new_response = Invitation_Timeblock(timeblock_id=timeid, invitation_id=id)
    db.session.add(new_response)
    db.session.commit()
        
    return invitation

def invitation_del_response_time(id: int, timeid: int) -> Invitation:
    """Removes a specified time from the invitation. If such a time doesn't already exist, do nothing."""
    try:
        invitation = get_invitation(id)
        if (invitation.event.finalized):
            raise ValueError("Event is already finalized")
    except Exception as ex:
        raise ValueError(str(ex)) from ex

    itblock = db.session.query(Invitation_Timeblock).filter(Invitation_Timeblock.timeblock_id == timeid).first()

    if itblock is None:
        return invitation
    
    db.session.delete(itblock)
    db.session.commit()
        
    return invitation

# TODO: not really being used right now, since AJAX adds one at a time
def invitation_update_response(id: int, time_ids: int) -> Invitation:
    """Store member's selected times. Returns the updated invitation."""
    try:
        updated_invite = get_invitation(id)
        # Manually retrieve to avoid circular import
        event = db.session.query(Event).filter(Event.id == id).one()
        if (event.finalized):
            raise Exception("Event is already finalized")
    except Exception as ex:
        raise ValueError("Issue fetching event") from ex

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