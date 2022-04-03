from app.src.group import add_member, create_group, delete_group
from app.src.timeblock import create_timeblock, delete_timeblock
from app.src.user import get_member_invitations, get_user_conflicts, get_user_events, get_user_groups, get_user_from_netid, get_users
from app.src.event import create_event, create_event_invitations, delete_event, event_finalize, get_event, get_invitation_response_times
from app.src.invitation import invitation_update_finalized, invitation_update_response
from flask import render_template, current_app, redirect, url_for, session, request, make_response
from flask_login import login_user, logout_user, login_required 
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

# ------------------------------------------------------------------- #
#                           PAGE ROUTES                               #
# ------------------------------------------------------------------- #

# ----------------------------- TEST -------------------------------- #
@bp.route("/test", methods=["GET", "POST"])
def test():
    if 'username' in session:
        user = get_user_from_netid(session['username'])
        events = get_user_events(user.id)
        event = get_event(2)
        
        print(event.invitations)
        print("-----------")
        print(get_invitation_response_times(event.id))
        return render_template("about.html")
    return render_template("login.html", 
        title='Login to TigerPlan')

@bp.route("/eventtest", methods=["GET", "POST"])
def event_test():
    if 'username' in session:
        invitation_update_response(1, time_ids = [3, 5])
        invitation_update_response(2, time_ids = [3, 4])
        invitation_update_response(3, time_ids = [3])
        invitation_update_finalized(2, True)
        return render_template("about.html")
    return render_template("login.html", 
            title='Login to TigerPlan')

# ----------------------------- HOME -------------------------------- #
@bp.route("/", methods=["GET", "POST"])
def index():
    if 'username' in session:
        user = get_user_from_netid(session['username'])
        groups = get_user_groups(user.id)
        events = get_user_events(user.id)
        return render_template("index.html", 
            title='TigerPlan Homepage', user=session['username'], 
            groups=groups, events=events)
    return render_template("login.html", 
        title='Login to TigerPlan') 


@bp.route("/testingstuff", methods=["GET", "POST"])
def test_calendar():
    return render_template("calendar.html")
# ---------------------------- DASHBOARD ---------------------------- #
@bp.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if 'username' in session:
        user = get_user_from_netid(session['username'])
        conflicts = get_user_conflicts(user.id)
        invitations = get_member_invitations(user.id)
        return render_template("dashboard.html",
            title='TigerPlan User Dashboard', user=session['username'], 
            conflicts=conflicts, invitations=invitations)
    return render_template("login.html", 
        title='Login to TigerResearch') 

# -------------------------- MANAGE GROUPS -------------------------- #
@bp.route("/mygroups", methods=['GET', 'POST'])
def groups():
    if 'username' in session:
        user = get_user_from_netid(session['username'])
        groups = get_user_groups(user.id)
        users = get_users()
        return render_template("mygroups.html",
        title='TigerPlan Manage Groups', user=session['username'], groups=groups, users=users)
    return render_template("login.html", 
        title='Login to TigerResearch') 

# ---------------------------- SCHEDULER ---------------------------- #
@bp.route("/scheduler", methods=['GET', 'POST'])
def scheduler():
    if 'username' in session:
        user = get_user_from_netid(session['username'])
        groups = get_user_groups(user.id)
        events = get_user_events(user.id)
        return render_template("scheduler.html",
            title='TigerPlan Scheduler', user=session['username'], 
            groups=groups, events=events)
    return render_template("login.html", 
        title='Login to TigerResearch') 

@bp.route("/view_event_details/<id>", methods=['GET', 'POST'])
def view_event_details(id):
    if 'username' in session:
        user = get_user_from_netid(session['username'])
        # TODO: Make an error html file for these cases
        try:
            event = get_event(id)
        except:
            html = "<strong>Error fetching event<strong>"
            return make_response(html)
        if event.owner_id != user.id:
            html = "<strong>Error fetching event<strong>"
            return make_response(html)
        if not event.finalized:
            responses, num = get_invitation_response_times(event.id)
            return render_template("eventdetails.html", finalized=False, event=event, responses=responses, num=num)
        else:
            # TODO: Ensure that there is a time
            return render_template("eventdetails.html", finalized=True,event=event, time=event.times[0])
    return render_template("login.html", 
        title='Login to TigerResearch') 


# ----------------------------- ABOUT ------------------------------- #
@bp.route("/about", methods=['GET', 'POST'])
def about():
    if 'username' in session:
        return render_template("about.html",
        title='TigerPlan About', user=session['username'])
    return render_template("login.html", 
        title='Login to TigerResearch') 


# ------------------------------------------------------------------- #
#                         MUTATION ROUTES                             #
# ------------------------------------------------------------------- #

# ------------------------------------------------------------------- #
@bp.route("/moveEvent", methods=["POST"])
def move_event():
    if 'username' in session:
        user = get_user_from_netid(session['username'])
        print(request.form['data'])
        a = datetime(2018, 11, 28)
        b = datetime(2018, 12, 28)
        create_timeblock(name="example", user=user, start=a, end=b)
        
    return render_template("login.html", 
        title='Login to TigerResearch') 

# --------------------- ADD DEFAULT CONFLICT ------------------------ #
@bp.route("/add_conflict/", methods=['GET', 'POST'])
def add_conflict():
    if 'username' in session:
        user = get_user_from_netid(session['username'])
        a = datetime(2018, 11, 28)
        b = datetime(2018, 12, 28)
        create_timeblock(name="example", user=user, start=a, end=b, isconflict=True)
        return redirect("/dashboard")
    return render_template("login.html", 
        title='Login to TigerResearch') 

# ----------------------- ADD CUSTOM GROUP ------------------------- #
@bp.route("/add_custom_group", methods=['GET', 'POST'])
def add_custom_group():
    if 'username' in session:
        user = get_user_from_netid(session['username'])
        name = request.args.get('name')
        member = request.args.get('member')
        new_group = create_group(name=name, owner=user)
        add_member(id=new_group.id, memberId=member)
        return redirect("/mygroups")
    return render_template("login.html", 
        title='Login to TigerResearch') 

# --------------------- CREATE CUSTOM EVENT ------------------------ #
@bp.route("/add_event", methods=['GET', 'POST'])
def add_event():
    if 'username' in session:
        user= get_user_from_netid(session['username'])
        id = request.args.get('id')
        name = request.args.get('name')
        location = request.args.get('location')
        description = request.args.get('description')
        create_event(groupid=id, name=name, owner=user, 
            location=location, description=description) 
        return redirect("/scheduler")
    return render_template("login.html", 
        title='Login to TigerPlan')

# ------------------------- FINALIZE EVENT -------------------------- #
@bp.route("/finalize_event_time/<eventid>/<timeid>", methods=['GET', 'POST'])
def finalize_event(eventid, timeid):
    if 'username' in session:
        user = get_user_from_netid(session['username'])
        event_finalize(eventid, timeid)
        return redirect("/scheduler")
    return render_template("login.html", 
        title='Login to TigerPlan')

# ------------------------ DELETE CONFLICT -------------------------- #
@bp.route("/del_conflict/<id>", methods=['GET', 'POST'])
def del_conflict(id):
    if 'username' in session:
        delete_timeblock(id) 
        return redirect("/dashboard")
    return render_template("login.html", 
        title='Login to TigerResearch') 

# -------------------------- DELETE GROUP --------------------------- #
@bp.route("/del_group/<id>", methods=['GET', 'POST'])
def del_group(id):
    if 'username' in session:
        delete_group(id) 
        return redirect("/mygroups")
    return render_template("login.html", 
        title='Login to TigerResearch') 

# ------------------------ DELETE EVENT ----------------------------- #
@bp.route("/del_event/<id>", methods=['GET', 'POST'])
def del_event(id):
    if 'username' in session:
        delete_event(id) 
        return redirect("/scheduler")

# ------------------- CREATE EVENT INVITATIONS ---------------------- #
@bp.route("/cr_event_invitations/<id>", methods=['GET', 'POST'])
def add_invitations(id):
    if 'username' in session:
        create_event_invitations(id) 
        return redirect("/scheduler")
    return render_template("login.html", 
        title='Login to TigerResearch') 

# ------------------------------------------------------------------- #
#                       AUTHORIZATION ROUTES                          #
# ------------------------------------------------------------------- #

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