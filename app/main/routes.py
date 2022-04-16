from app.src.group import add_member, create_group, delete_group, delete_member, get_group, get_group_events, get_members, update_group_name, update_owner
from app.src.timeblock import create_event_timeblock, create_timeblock, delete_timeblock, update_timeblock
from app.src.user import get_member_invitations, get_user_conflicts, get_user_events, get_user_groups, get_user_from_netid, get_users
from app.src.event import create_event, create_event_invitations, delete_event, event_finalize, get_event, get_invitation_response_times
from app.src.invitation import get_invitation, invitation_add_response_time, invitation_del_response_time, invitation_update_finalized, invitation_update_response
from flask import render_template, current_app, redirect, url_for, session, request, make_response, jsonify
from flask_login import login_user, logout_user, login_required 
from cas import CASClient
from datetime import datetime
import json

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


@bp.route("/events1", methods=["GET", "POST"])
def event1():
    if 'username' in session:
        user = get_user_from_netid(session['username'])
        groups = get_user_groups(user.id)
        events = get_user_events(user.id)
        return render_template("event.html", 
            title='TigerPlan Event Page', user=session['username'], 
            groups=groups, events=events)
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


### Respond to an invitation as an invitee. Called using AJAX in dashboard ###
@bp.route("/respond_to_invitation/<id>", methods=['GET', 'POST'])
def respond_to_invitation(id):
    # TODO: Make JSON
    if 'username' in session:
        user = get_user_from_netid(session['username'])
        try:
            invitation = get_invitation(id)
        except:
            html = "<strong>Error fetching invitation<strong>"
            return make_response(html)
        if invitation.user_id != user.id:
            html = "<strong>Error fetching invitation<strong>"
            return make_response(html)
        
        response_timeblockids = []

        for invtb in invitation.responses:
            response_timeblockids.append(invtb.timeblock_id)

        return render_template("respondtoinvitation.html", invitation=invitation, response_timeblockids=response_timeblockids)

    return render_template("login.html", 
        title='Login to TigerPlan')
# -------------------------- MANAGE GROUPS -------------------------- #
@bp.route("/mygroups", methods=['GET', 'POST'])
def groups():
    if 'username' in session:
        user = get_user_from_netid(session['username'])
        groups = get_user_groups(user.id)
        users = get_users()
        groupId = request.args.get("groupId")
        if (groupId):
            group = get_group(groupId)
            members = get_members(groupId)
            events = get_group_events(groupId)
            return render_template("mygroups.html",
            title='TigerPlan Manage Groups', user=session['username'], groups=groups, users=users, members=members, this_group=group, events=events)
        return render_template("mygroups.html", title='TigerPlan Manage Groups', user=session['username'], groups=groups)
    return render_template("login.html", 
        title='Login to TigerResearch') 

# # -------------------------- MANAGE GROUPS -------------------------- #
# @bp.route("/managegroup/<groupId>", methods=['GET', 'POST'])
# def managegroup(groupId):
#     if 'username' in session:
#         user = get_user_from_netid(session['username'])
#         groups = get_user_groups(user.id)
#         group = get_group(groupId)
#         members = get_members(groupId)
#         users = get_users()
#         return render_template("mygroups.html",
#         title='TigerPlan Manage Groups', user=session['username'], groups=groups, users=users, members=members, this_group=group)
#     return render_template("login.html", 
#         title='Login to TigerResearch') 

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
@bp.route("/moveEvent/", methods=["POST"])
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
@bp.route("/saveNewSchedule/", methods=["GET", "POST"])
def saveNewSchedule():
    if 'username' in session:
        user = get_user_from_netid(session['username'])
        schedule = json.loads(request.get_data())
        start = datetime.fromisoformat(schedule['start']['_date'][:-1])
        end = datetime.fromisoformat(schedule['end']['_date'][:-1])

        tb = create_timeblock(name=schedule['title'], user=user, start=start, 
            end=end, isconflict=True)
        return make_response(jsonify(success=True, id=tb.id))
    return render_template("login.html", 
        title='Login to TigerResearch') 

@bp.route("/update_conflict/", methods=["GET", "POST"])
def update_conflict():
    if 'username' in session:
        user = get_user_from_netid(session['username'])
        schedule = json.loads(request.get_data())

        start = datetime.strptime(schedule['start'][5:], '%d %b %Y %H:%M:%S GMT')
        end = datetime.strptime(schedule['end'][5:], '%d %b %Y %H:%M:%S GMT')

         # retrieve database datetime
        update_timeblock(schedule['id'], schedule['title'], start, end)

        return make_response(jsonify(success=True))
    return render_template("login.html", 
        title='Login to TigerResearch') 

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
        create_group(name=name, owner=user)
        return redirect("/mygroups")
    return render_template("login.html", 
        title='Login to TigerResearch')

# --------------------- CREATE CUSTOM EVENT ------------------------ #
@bp.route("/add_event", methods=['GET', 'POST'])
def add_event():
    if 'username' in session:
        try:
            user = get_user_from_netid(session['username'])
            schedule = json.loads(request.get_data())
            group_id = schedule['groupId']
            # TODO: Make sure group_id is valid?
            group_id = int(group_id)
            name = schedule['name']
            if (name is None or name.strip() == ""):
                raise Exception("Name is abscent")
            location = schedule['location']
            description = schedule['description']
            timeblocks = schedule['timeblocks']
            if (len(timeblocks) == 0):
                raise Exception("No timeblocks included")
            
            new_event = create_event(groupid=group_id, name=name,
                                    owner=user, location=location, 
                                    description=description,
                                    timeblocks=timeblocks)
            response_json = json.dumps({"success":True, 
                "newEventId":new_event.id,
                "groupName":new_event.group.name
                })
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response
        except Exception as ex:
            print("An exception occured at '/add_event':", ex)
            response_json = json.dumps({"success":False})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response
    return render_template("login.html", 
        title='Login to TigerPlan')

# ------------------------- FINALIZE EVENT -------------------------- #
@bp.route("/finalize_event_time/<eventid>/<timeid>", methods=['GET', 'POST'])
def finalize_event(eventid, timeid):
    if 'username' in session:
        user = get_user_from_netid(session['username'])
        #TODO: check authorization
        event_finalize(eventid, timeid)
        return redirect("/scheduler")
    return render_template("login.html", 
        title='Login to TigerPlan')

# ------------------------ DELETE CONFLICT -------------------------- #
@bp.route("/del_conflict/<id>", methods=['GET', 'POST'])
def del_conflict(id):
    if 'username' in session:
        #TODO: check authorization
        delete_timeblock(id) 
        return redirect("/dashboard")
    return render_template("login.html", 
        title='Login to TigerResearch') 

# -------------------------- DELETE GROUP --------------------------- #
@bp.route("/del_group/<id>", methods=['GET', 'POST'])
def del_group(id):
    if 'username' in session:
        #TODO: check authorization
        delete_group(id) 
        return redirect("/mygroups")
    return render_template("login.html", 
        title='Login to TigerResearch') 

# ------------------------ DELETE EVENT ----------------------------- #
@bp.route("/del_event/<id>", methods=['GET', 'POST'])
def del_event(id):
    if 'username' in session:
        try:
            user = get_user_from_netid(session['username'])
            event = get_event(id)
            if (event.owner_id != user.id):
                raise Exception("User is not event owner")
            delete_event(id)
        except Exception as ex:
            print("An exception occured at '/del_event':", ex)
            response_json = json.dumps({"success":False})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response

        response_json = json.dumps({"success":True})
        response = make_response(response_json)
        response.headers['Content-Type'] = 'application/json'
        return response

# ------------------- CREATE EVENT INVITATIONS ---------------------- #
@bp.route("/cr_event_invitations/<id>", methods=['GET', 'POST'])
def add_invitations(id):
    if 'username' in session:
        user = get_user_from_netid(session['username'])
        event = get_event(id)
        if (event.owner_id != user.id):
            # TODO: Make this JSON
            html = "<strong>Error fetching event<strong>"
            return make_response(html)
        create_event_invitations(id) 
        return redirect("/scheduler")
    return render_template("login.html", 
        title='Login to TigerPlan') 

# # ------------------- MEMBERs ---------------------- #
# @bp.route("/members", methods=['GET', 'POST'])
# def manage_members():
#     if 'username' in session:
#         groupId = request.args.get('group')
#         group = get_group(groupId)
#         members = get_members(groupId)
#         users = get_users()
#         return make_response("groupmembers.html", group=group, members=members, users=users)
#     return make_response("login.html", 
#         title='Login to TigerPlan')

# # ------------------- GROUP ADMIN ---------------------- #
# @bp.route("/admin/<groupid>", methods=['GET', 'POST'])
# def admin(groupid):
#     if 'username' in session:
#         group = get_group(groupid)
#         members = get_members(groupid)
#         return render_template("groupadmin.html", group=group, members=members)
#     return render_template("login.html", 
#         title='Login to TigerPlan')

# # ------------------- GROUP EVENTS ---------------------- #
# @bp.route("/groupevents/<groupid>", methods=['GET', 'POST'])
# def groupevents(groupid):
#     if 'username' in session:
#         group = get_group(groupid)
#         events = get_group_events(groupid)
#         return render_template("groupevent.html", group=group, events=events)
#     return render_template("login.html", 
#         title='Login to TigerPlan')

# ------------------------ REMOVE MEMBER ----------------------------- #
@bp.route("/remove_member/<groupid>/<id>", methods=['GET', 'POST'])
def remove_member(groupid, id):
    if 'username' in session:
        # TODO: Authorization checking
        delete_member(groupid, id)
        return redirect("/mygroups?groupId=" + groupid)
    return render_template("login.html", 
        title='Login to TigerPlan')

# ----------------------- ADD GROUP MEMBER ------------------------- #
@bp.route("/add_new_member", methods=['GET', 'POST'])
def add_new_member():
    if 'username' in session:
        # TODO: Authorization checking
        groupId = request.args.get('group')
        member = request.args.get('member')
        add_member(id=groupId, memberId=member)
        return redirect("/mygroups?groupId=" + groupId)
    return render_template("login.html", 
        title='Login to TigerResearch')

# ----------------------- TRANSFER OWNERSHIP ------------------------- #
@bp.route("/change_ownership", methods=['GET', 'POST'])
def change_ownership():
    if 'username' in session:
        # TODO: Authorization checking
        groupId = request.args.get('group')
        member = request.args.get('member')
        update_owner(groupid=groupId, memberId=member)
        return redirect("/mygroups?groupId=" + groupId)
    return render_template("login.html", 
        title='Login to TigerResearch')

# ----------------------- CHANGE GROUP NAME ------------------------- #
@bp.route("/change_group_name", methods=['GET', 'POST'])
def change_group_name():
    if 'username' in session:
        # TODO: Authorization checking
        groupId = request.args.get('group')
        name = request.args.get('name')
        update_group_name(groupid=groupId, newName=name)
        return redirect("/mygroups?groupId=" + groupId)
    return render_template("login.html", 
        title='Login to TigerResearch')

# ------------------- EDIT INVITATION RESPONSE ---------------------- #
@bp.route("/add_invitation_response_time/<invitationid>/<timeid>", methods=['POST'])
def add_invitation_response_time(invitationid, timeid):
    if 'username' in session:
        user = get_user_from_netid(session['username'])
        invitation = get_invitation(invitationid)
        if invitation.user_id != user.id:
            html = "<strong>Error fetching invitation<strong>"
            # TODO: Make JSON
            print("Invitation is not owned by user")
            return make_response(html, 400)
        else:
            try:
                invitation_add_response_time(invitationid, timeid)
            except ValueError as ex:
                html = "<strong>%s<strong>" % str(ex)
                # TODO: Make JSON
                print("value error", str(ex))
                return make_response(html, 400)
            # TODO: Make JSON
            return "Success!"
    # TODO: Make JSON
    return render_template("login.html", 
        title='Login to TigerPlan')

@bp.route("/del_invitation_response_time/<invitationid>/<timeid>", methods=['POST'])
def del_invitation_response_time(invitationid, timeid):
    if 'username' in session:
        user = get_user_from_netid(session['username'])
        invitation = get_invitation(invitationid)
        if (invitation.user_id != user.id):
            # TODO: Make JSON
            html = "<strong>Error fetching invitation<strong>"
            print("Invitation is not owned by user")
            return make_response(html, 400)
        else:
            try:
                invitation_del_response_time(invitationid, timeid)
            except ValueError as ex:
                # TODO: Make JSON
                html = "<strong>%s<strong>" % str(ex)
                print("value error", str(ex))
                return make_response(html, 400)
            # TODO: Make JSON
            return "Success!"
    return render_template("login.html", 
        title='Login to TigerPlan')

# ---------------------- FINALIZE INVITATION ------------------------ #
@bp.route("/finalize_invitation/<invitationid>", methods=['POST'])
def finalize_invitation(invitationid):
    if 'username' in session:
        user = get_user_from_netid(session['username'])
        invitation = get_invitation(invitationid)
        if (invitation.user_id != user.id):
            html = "<strong>Error fetching invitation<strong>"
            print("Invitation is not owned by user")
            # TODO: Make JSON
            return make_response(html, 400)
        else:
            try:
                invitation_update_finalized(invitationid, True)
            except ValueError as ex:
                # TODO: Make JSON
                html = "<strong>%s<strong>" % str(ex)
                print("value error", str(ex))
                return make_response(html, 400)
            return "Success!"
    return render_template("login.html", 
        title='Login to TigerPlan')

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

# ------------------------ LOAD CONFLICTS --------------------------- #
@bp.route("/load_conflicts", methods=['GET', 'POST'])
def load_conflicts():
    user = get_user_from_netid(session['username'])
    conflicts = get_user_conflicts(user.id)
    conflicts = [conflict.to_json() for conflict in conflicts]

    return jsonify(conflicts)