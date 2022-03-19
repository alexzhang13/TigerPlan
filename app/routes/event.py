import app
from app.models.models import User
from flask import request
from app import db, login
from models import Event

def create_event(name: str, owner: User, invitees: list(User), location: str, description: str) -> Event:
    """Create an event. Returns created event."""
    new_event = Event(name=name,
                      owner=owner,
                      invitees=invitees,
                      location=location,
                      description=description)
    db.session.add(new_event)
    db.session.commit()
    return new_event

def update_event(id: int, name: str, invitees: list(User), location: str, description: str) -> Event:
    """Update an event. Returns updated event."""
    updated_event = db.session.query(Event).filter(Event.id == id).one()
    if name is not None:
        updated_event.name = name
    if invitees is not None:
        updated_event.invitees = invitees
    if location is not None:
        updated_event.location = location
    if description is not None:
        updated_event.description = description
    db.session.add(updated_event)
    db.session.commit()
    return updated_event

def delete_event(id: int) -> bool:
    """Delete an event. Returns true if successful."""
    del_event = db.session.query(Event).filter(Event.id == id).one()
    db.session.delete(del_event)
    db.session.commit()
    # if successfully deleted, del_event.id should be None
    return del_event.id == None