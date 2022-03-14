from app import db, login
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "user"
    netid = db.Column(db.String(64), primary_key=True)
    id = db.Column(db.String(64))
    email = db.Column(db.String(64))

    def __repr__(self):
        return '<User {}>'.format(self.netid)

@login.user_loader
def load_user(netid):
    return User.query.filter_by(id=netid).first()