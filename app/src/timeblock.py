from xmlrpc.client import DateTime
from app.models.models import TimeBlock, User, Event
from app import db

#---------------------------- CRUD Functions -------------------------#
def create_timeblock(name: str, user: User, start: DateTime, end: DateTime, isconflict: bool) -> TimeBlock:
    """Create a time block. Returns created time block."""
    new_tb = TimeBlock(name=name,
                      user_id=user.id,
                      start=start,
                      end=end,
                      is_conflict=isconflict)
    db.session.add(new_tb)
    db.session.commit()
    return new_tb

def create_event_timeblock(start: DateTime, end: DateTime, isconflict: bool, eventId: int, name: str, commit: bool = True) -> TimeBlock:
    """Create a time block. Returns created time block."""
    new_tb = TimeBlock(start=start,
                      end=end, name=name,
                      is_conflict=isconflict,
                      event_id=eventId)
    db.session.add(new_tb)
    
    if commit:
        db.session.commit()
    return new_tb

def get_timeblock(id: int) -> TimeBlock:
    """Get a time block. Returns time block."""
    return db.session.query(TimeBlock).filter(TimeBlock.id == id).one()

def update_timeblock(id: int, name: str, start: TimeBlock, end: TimeBlock) -> TimeBlock:
    """Update a time block. Returns updated time block."""
    updated_tb = db.session.query(TimeBlock).filter(TimeBlock.id == id).one()
    if name is not None:
        updated_tb.name = name
    updated_tb.start = start
    updated_tb.end = end
    
    db.session.add(updated_tb)
    db.session.commit()
    return updated_tb

def delete_timeblock(id: int) -> bool:
    """Delete a time block. Returns true if successful."""
    del_tb = db.session.query(TimeBlock).filter(TimeBlock.id == id).one()
    db.session.delete(del_tb)
    db.session.commit()
    return del_tb.id == None

#---------------------------- SPEC Functions -------------------------#
