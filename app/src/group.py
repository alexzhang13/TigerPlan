from app.models.models import Invitation, Invitation_Timeblock, Member_Group, User, Group, Event
from app import db
from app.src.event import delete_event

#---------------------------- CRUD Functions -------------------------#
def create_group(name: str, owner: User) -> Group: 
    """Create a group. Returns created group."""
    new_group = Group(name=name,
                      owner_id=owner.id)
    db.session.add(new_group)
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
    if members is not None:                         #TODO: Test
        for member in members:
            add_member(id=id, member=member)
    db.session.add(updated_group)
    db.commit()
    return updated_group

def delete_group(id: int) -> bool:
    """Delete a group. Returns true if successful."""
    del_group = db.session.query(Group).filter(Group.id == id).one()
    db.session.query(Member_Group).filter(Member_Group.group_id == id).delete()
    events = db.session.query(Event).filter(Event.group_id == id).all()
    for event in events:
        del_responses = db.session.query(Invitation_Timeblock).filter(Invitation.event_id == id, Invitation_Timeblock.invitation_id == Invitation.id).all()
        for del_response  in del_responses:
            db.session.delete(del_response)
        del_invitations = db.session.query(Invitation).filter(Invitation.event_id == id).all()
        for del_inv in del_invitations:
            db.session(del_inv)
        db.session.delete(event)
    db.session.delete(del_group)
    db.session.commit()
    return del_group.id == None

#---------------------------- Spec Functions -------------------------#
def add_member(id: int, memberId: int) -> bool:
    new_mem_group = Member_Group(member_id=memberId, group_id=id)
    db.session.add(new_mem_group)
    db.session.commit()
    return new_mem_group.id != None

def delete_member(id: int, member: User) -> bool:
    del_mem_group = db.session.query(Member_Group).filter(Member_Group.group_id == id, Member_Group.member_id==member.id)
    db.session.delete(del_mem_group)
    db.session.commit()
    return del_mem_group.id == None
    

