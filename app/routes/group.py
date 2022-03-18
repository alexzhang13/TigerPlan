from app.models.models import User
from app import db
from models import Group

def create_group(name: str, owner: User, members: list(User)) -> Group:
    """Create a group. Returns created group."""
    new_group = Group(name=name,
                      owner=owner,
                      members=members)
    db.session.add(new_group)
    db.session.commit()
    return new_group

def get_group(id: int) -> Group:
    """Get a group. Returns group."""
    return db.session.query(Group).filter(Group.id == id).one()

def update_group(id: int, name: str, members: list(User)) -> Group:
    """Update a group. Returns updated group."""
    updated_group = db.session.query(Group).filter(Group.id == id).one()
    if name is not None:
        updated_group.name = name
    if members is not None:
        updated_group.members = members
    db.session.add(updated_group)
    db.commit()
    return updated_group

def delete_group(id: int) -> bool:
    """Delete a group. Returns true if successful."""
    del_group = db.session.query(Group).filter(Group.id == id).one()
    db.session.delete(del_group)
    db.session.commit()
    # if successfully deleted, del_group.id should be None
    return del_group.id == None
