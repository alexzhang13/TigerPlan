from app.models.models import Invitation, User, Event
from app import db

def create_invitation(invitee: User, event: Event) -> Invitation:
    """Create a invitation. Returns created invitation."""
    new_invite = Invitation(event=event,
                      invitee=invitee)
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
    # if successfully deleted, del_invite.id should be None
    return del_invite.id == None
