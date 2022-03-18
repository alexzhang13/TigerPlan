from app.models.models import TimeBlock, User
from app import db
from models import Group

def create_timeblock(name: str, user: User) -> TimeBlock:
    """Create a time block. Returns created time block."""
    new_tb = TimeBlock(name=name,
                      user=user)
    db.session.add(new_tb)
    db.session.commit()
    return new_tb

def get_timeblock(id: int) -> Group:
    """Get a time block. Returns time block."""
    return db.session.query(TimeBlock).filter(TimeBlock.id == id).one()

def update_timeblock(id: int, name: str) -> TimeBlock:
    """Update a time block. Returns updated time block."""
    updated_tb = db.session.query(TimeBlock).filter(TimeBlock.id == id).one()
    if name is not None:
        updated_tb.name = name
    db.session.add(updated_tb)
    db.session.commit()
    return updated_tb

def delete_timeblock(id: int) -> bool:
    """Delete a time block. Returns true if successful."""
    del_tb = db.session.query(TimeBlock).filter(TimeBlock.id == id).one()
    db.session.delete(del_tb)
    db.session.commit()
    # if successfully deleted, del_tb.id should be None
    return del_tb.id == None
