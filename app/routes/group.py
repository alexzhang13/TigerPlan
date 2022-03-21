from app.models.models import Member_Group, User, Group
from app import db

def create_group(name: str, owner: User, members: User) -> Group: #TODO: Update the Member_Groups table 
    """Create a group. Returns created group."""
    new_group = Group(name=name,
                      owner_id=owner.id,
                      members=members)
    db.session.add(new_group)
    db.session.commit()
    new_member_group = Member_Group(group_id=new_group.id, member_id=owner.id)
    db.session.add(new_member_group)
    db.session.commit()
    return new_group

def get_group(id: int) -> Group:
    """Get a group. Returns group."""
    return db.session.query(Group).filter(Group.id == id).one()

def update_group(id: int, name: str, members: User) -> Group:
    """Update a group. Returns updated group."""
    updated_group = db.session.query(Group).filter(Group.id == id).one()
    if name is not None:
        updated_group.name = name
    if members is not None:
        updated_group.members = members
    db.session.add(updated_group)
    db.commit()
    return updated_group

def delete_group_on_id(id: int) -> bool:
    """Delete a group. Returns true if successful."""
    del_group = db.session.query(Group).filter(Group.id == id).one()
    db.session.query(Member_Group).filter(Member_Group.group_id == id).delete()
    db.session.delete(del_group)
    db.session.commit()
    
    # if successfully deleted, del_group.id should be None
    return del_group.id == None
