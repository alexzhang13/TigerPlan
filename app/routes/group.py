import app
from app.models.models import User
from flask import request
from app import db, login
from models import Group


def create_group(name: str, owner: User, members: list(User)) -> Group:
    """Endpoint to create a group."""
    new_group = Group(name=name,
                      owner=owner,
                      members=members)
    db.session.add(new_group)
    db.session.commit()
    return new_group