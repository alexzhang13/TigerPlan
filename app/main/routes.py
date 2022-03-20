from app.routes.timeblock import create_timeblock, delete_timeblock
from app.routes.user import get_conflicts, user_from_netid
from flask import render_template, current_app, redirect, url_for, session, request
from flask_login import current_user, login_user, logout_user, login_required
from cas import CASClient
from datetime import datetime

from app import db
from app.main import bp
from app.models import models

cas_client = CASClient(
    version=3,
    service_url='http://localhost:80/login',
    server_url='https://fed.princeton.edu/cas/login'
)

# ------------------------ HOME PAGE LOGIN -------------------------- #
@bp.route("/", methods=["GET", "POST"])
def index():
    if 'username' in session:
        return render_template("index.html", 
        title='TigerPlan Homepage', user=session['username'])
    return render_template("login.html", 
        title='Login to TigerResearch') 

# ------------------------ USER DASHBOARD --------------------------- #
@bp.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if 'username' in session:
        user = user_from_netid(session['username'])
        a = datetime(2018, 11, 28)
        b = datetime(2018, 12, 28)
        create_timeblock(name="example", user=user, start=a, end=b)
        conflicts = get_conflicts(user.id)
        return render_template("dashboard.html",
        title='TigerPlan User Dashboard', user=session['username'], conflicts=conflicts)

# ------------------------ DELETE CONFLICT -------------------------- #
@bp.route("/delete_conflict", methods=['GET', 'POST'])
def delete_conflict():
    if 'username' in session:
        user = user_from_netid(session['username'])
        delete_timeblock(1) # THIS IS MANUAL RIGHT NOW V BAD
        conflicts = get_conflicts(user.id)
        return render_template("dashboard.html",
        title='TigerPlan User Dashboard', user=session['username'], conflicts=conflicts)
# -------------------------- LOGIN PAGE ----------------------------- #

@bp.route("/login", methods=['GET', 'POST'])
def login():
    # Already logged in
    if 'username' in session:
        return redirect(url_for('main.index'))
    
    next = request.args.get('next')
    ticket = request.args.get('ticket')
    if not ticket:
        # No ticket, the request come from end user, send to CAS login
        cas_login_url = cas_client.get_login_url()
        current_app.logger.debug('CAS login URL: %s', cas_login_url)
        return redirect(cas_login_url)

    # There is a ticket, the request come from CAS as callback.
    # need call `verify_ticket()` to validate ticket
    current_app.logger.debug('ticket: %s', ticket)
    current_app.logger.debug('next: %s', next)

    user, attributes, pgtiou = cas_client.verify_ticket(ticket)

    current_app.logger.debug(
        'CAS verify ticket response: user: %s,' +\
        'attributes: %s, pgtiou: %s', user, attributes, pgtiou)

    if not user:
        return redirect(url_for('main.login'))
    else:  
        # Login successfully, redirect according `next` query parameter
        session['username'] = user
        user_id = models.User.query.filter_by(netid=user).first()
        if user_id is None:
            user_id = models.User(netid=user, 
            email=(user + "@princeton.edu"))
            db.session.add(user_id)
            db.session.commit()
        login_user(user_id)
        return redirect(url_for('main.index'))

# -------------------------- LOGOUT PAGE ---------------------------- #

@login_required
@bp.route("/logout")
def logout():
    redirect_url = url_for('main.logout_callback', _external=True)
    cas_logout_url = cas_client.get_logout_url(redirect_url)
    current_app.logger.debug('CAS logout URL: %s', cas_logout_url)
    logout_user()
    return redirect(cas_logout_url)

@bp.route('/logout_callback')
def logout_callback():
    # redirect from CAS logout request after CAS logout successfully
    session.pop('username', None)
    return redirect(url_for('main.index'))