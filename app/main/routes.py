from app.src.group import add_admin, add_member, create_group, delete_admin, delete_group, delete_member, get_group, get_group_admin, get_group_events, get_members, update_group_name, update_owner
from app.src.timeblock import create_timeblock, delete_timeblock, get_timeblock, update_timeblock
from app.src.user import get_admin_groups, get_member_invitations, get_user_conflicts, get_user_events, get_user_from_id, get_user_groups, get_user_from_netid, get_users
from app.src.event import create_event, create_event_invitations, delete_event, event_finalize, get_event, get_invitation_response_times
from app.src.invitation import get_invitation, invitation_finalize
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
    service_url='http://localhost/login',
    server_url='https://fed.princeton.edu/cas/login'
)

# ----------------------- HELPER FUNCTIONS -------------------------- #

def check_user_validity():
    if not 'username' in session:
        return False
    try:
        user = get_user_from_netid(session['username'])
        if user is None:
            return False
    except:
        return False
    return True

# ------------------------------------------------------------------- #
#                           PAGE ROUTES                               #
# ------------------------------------------------------------------- #

# ----------------------------- HOME -------------------------------- #
@bp.route("/", methods=["GET"])
def index():
    if check_user_validity():
        user = get_user_from_netid(session['username'])
        groups = get_user_groups(user.id)
        events = get_user_events(user.id)
        return render_template("index.html",
            title='TigerPlan Homepage', user=session['username'],
            groups=groups, events=events)
    return render_template("login.html",
        title='Login to TigerPlan')

# ---------------------------- DASHBOARD ---------------------------- #
@bp.route("/dashboard", methods=['GET'])
def dashboard():
    if check_user_validity():
        user = get_user_from_netid(session['username'])
        conflicts = get_user_conflicts(user.id)
        invitations = get_member_invitations(user.id)
        return render_template("dashboard.html",
            title='TigerPlan User Dashboard', user=session['username'], 
            conflicts=conflicts, invitations=invitations)
    return render_template("login.html", 
        title='Login to TigerResearch')

# -------------------------- MANAGE GROUPS -------------------------- #
@bp.route("/mygroups", methods=['GET'])
def groups():
    if check_user_validity():
        user = get_user_from_netid(session['username'])
        groups = get_user_groups(user.id)
        admin_groups = get_admin_groups(user.id)
        users = get_users()
        groupId = request.args.get("groupId")
        if (groupId):
            try:
                group = get_group(groupId)
                if group.owner_id != user.id:
                    raise Exception("User is not group owner")
                members = get_members(groupId)
                events = get_group_events(groupId)
                admins = get_group_admin(groupId)
            except:
                return render_template("mygroups.html", 
                    title='TigerPlan Manage Groups',
                    user=session['username'], groups=groups)
            return render_template("mygroups.html", 
                title='TigerPlan Manage Groups', 
                user=session['username'],
                groups=groups, admin_groups=admin_groups, 
                admins=admins, users=users, members=members, 
                this_group=group, events=events)
        return render_template("mygroups.html", 
            title='TigerPlan Manage Groups', 
            user=session['username'], groups=groups, 
            admin_groups=admin_groups)
    return render_template("login.html",
        title='Login to TigerResearch')

# ------------- JSON USER ENCODER ----------------------------------- #
def encodeUser(userObj):
    result = []
    if isinstance(userObj, list):
        for user in userObj:
            output = {}
            output['id'] = user.id
            output['netid'] = user.netid
            output['name'] = user.name
            result.append(output)
    elif isinstance(userObj, models.User):
        output = {}
        output['id'] = userObj.id
        output['netid'] = userObj.netid
        output['name'] = userObj.name
        return output
    return result

def encodeEvent(eventObj):
    result = []
    if isinstance(eventObj, list):
        for event in eventObj:
            output = {}
            output['id'] = event.id
            output['name'] = event.name
            output['location'] = event.location
            output['description'] = event.description
            result.append(output)
    elif isinstance(eventObj, models.Event):
        output = {}
        output['id'] = event.id
        output['name'] = event.name
        output['location'] = event.location
        output['description'] = event.description
        return output
    return result

# -------------------------- MANAGE GROUPS -------------------------- #
@bp.route("/mygroupinfo", methods=['GET'])
def groupinfo():
    if check_user_validity():
        try:
            user = get_user_from_netid(session['username'])
            groupId = request.args.get('groupId')
            group = get_group(groupId)
            if (group.owner_id != user.id):
                raise Exception("User is not group owner")
            # groups = get_user_groups(user.id)
            # admin_groups = get_admin_groups(user.id)
            users = encodeUser(get_users())
            if (groupId):
                try:
                    members = encodeUser(get_members(groupId))
                    events = encodeEvent(get_group_events(groupId))
                    admins = encodeUser(get_group_admin(groupId))
                    response_json = json.dumps({"success": True,
                        "users": users, "members": members, 
                        "events": events, "admins": admins})
                    response = make_response(response_json)
                    response.headers['Content-Type'] = 'application/json'
                    return response
                except Exception as ex:
                    raise ex
        except Exception as ex:
            print("An exception occured at '/mygroupinfo':", ex)
            response_json = json.dumps({"success":False})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response
    return render_template("login.html",
        title='Login to TigerResearch')

# ---------------------------- SCHEDULER ---------------------------- #
@bp.route("/scheduler", methods=['GET'])
def scheduler():
    if check_user_validity():
        user = get_user_from_netid(session['username'])
        groups = get_user_groups(user.id)
        admin_groups = get_admin_groups(user.id)
        events = get_user_events(user.id)
        return render_template("scheduler.html",
            title='TigerPlan Scheduler', 
            user=session['username'], 
            groups=groups, events=events,
            admin_groups = admin_groups)
    return render_template("login.html", 
        title='Login to TigerResearch') 

# -------------------------- MANAGE EVENTS -------------------------- #
@bp.route("/manage_events", methods=['GET'])
def manage_events():
    if 'username' in session:
        user = get_user_from_netid(session['username'])
        groups = get_user_groups(user.id)
        admin_groups = get_admin_groups(user.id)
        events = get_user_events(user.id)
        return render_template("manage_events.html",
            title='TigerPlan Scheduler', 
            user=session['username'], 
            groups=groups, events=events,
            admin_groups = admin_groups)
    return render_template("login.html", 
        title='Login to TigerResearch') 

# ----------------------------- ABOUT ------------------------------- #
@bp.route("/about", methods=['GET', 'POST'])
def about():
    if check_user_validity():
        return render_template("about.html",
        title='TigerPlan About', user=session['username'])
    return render_template("login.html", 
        title='Login to TigerResearch')

# ------------------------- EVENT DETAILS --------------------------- #

@bp.route("/view_event_details/<id>", methods=['GET', 'POST'])
def view_event_details(id):
    if check_user_validity():
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
            return render_template("eventdetails.html", 
                finalized=False, event=event, responses=responses,
                num=num)
        else:
            # TODO: Ensure that there is a time
            return render_template("eventdetails.html", finalized=True,
            event=event, time=event.times[0])
    return render_template("login.html", 
        title='Login to TigerResearch') 

# ------------------------------------------------------------------- #
#                         GROUP MUTATIONS                             #
# ------------------------------------------------------------------- #

# -------------------------- ADD GROUP ------------------------------ #
@bp.route("/add_custom_group", methods=['POST'])
def add_custom_group():
    if check_user_validity():
        try:
            user = get_user_from_netid(session['username'])
            name = request.args.get('name')
            if (name.strip() == ""):
                raise Exception("A name is required")
            create_group(name=name, owner=user)
            response_json = json.dumps({"success":True})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response
        except Exception as ex:
            print("An exception occured at '/add_custom_group':", ex)
            response_json = json.dumps({"success":False})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response
    return render_template("login.html", 
        title='Login to TigerResearch')

# -------------------------- DELETE GROUP --------------------------- # TODO: change to POST
@bp.route("/del_group", methods=['POST'])
def del_group():
    if check_user_validity():
        try:
            user = get_user_from_netid(session['username'])
            group_id = request.args.get('group')
            group = get_group(group_id)
            if user.id != group.owner_id:
                raise Exception("User is not group owner.")
            success = delete_group(group_id) 
            response = make_response(json.dumps({"success":success}))
            response.headers['Content-Type'] = 'application/json'
            return response
        except Exception as ex:
            print("An exception occured at '/del_group':", ex)
            response_json = json.dumps({"success":False})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response
    return render_template("login.html", 
        title='Login to TigerResearch')

# ------------------------ REMOVE MEMBER ----------------------------- #
@bp.route("/remove_member", methods=['POST'])
def remove_member():
    if check_user_validity():
        try:
            user = get_user_from_netid(session['username'])
            group_id = request.args.get('groupId')
            member_id = request.args.get('memberId')
            group = get_group(group_id)
            if (user.id != group.owner_id):
                raise Exception("User is not group owner.")
            success = delete_member(group_id, member_id)
            response = make_response(json.dumps({"success":success}))
        except Exception as ex:
            print("An exception occured at '/remove_member':", ex)
            response_json = json.dumps({"success":False})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response

        response_json = json.dumps({"success":True})
        response = make_response(response_json)
        response.headers['Content-Type'] = 'application/json'
        return response

    return render_template("login.html", 
        title='Login to TigerPlan')

# ----------------------- ADD GROUP MEMBER ------------------------- #
@bp.route("/add_new_member", methods=['POST'])
def add_new_member():
    if check_user_validity():
        try:
            user = get_user_from_netid(session['username'])
            group_id = request.args.get('group')
            group = get_group(group_id)
            if (group.owner_id != user.id):
                raise Exception("User is not group owner")
            member_id = request.args.get('member')
            redudant = not add_member(id=group_id, memberId=member_id)
            member = get_user_from_id(member_id)
            response_json = json.dumps({"success": True,
                "redundant": redudant, "memberName": member.name, 
                "memberNetid": member.netid})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response
        except Exception as ex:
            print("An exception occured at '/add_new_member':", ex)
            response_json = json.dumps({"success":False})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response

    return render_template("login.html", 
        title='Login to TigerResearch')

# ----------------------- TRANSFER OWNERSHIP ------------------------- #
@bp.route("/change_ownership", methods=['POST'])
def change_ownership():
    if check_user_validity():
        try:
            user = get_user_from_netid(session['username'])
            groupId = request.args.get('group')
            group = get_group(groupId)
            member = request.args.get('member')
            if (group.owner_id != user.id):
                raise Exception("User is not group owner")
            update_owner(groupid=groupId, newOwnerId=member)
            return redirect("/mygroups?groupId=" + groupId)
        except Exception as ex:
            print("An exception occured at '/change_ownership':", ex)
            response_json = json.dumps({"success":False})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response

    return render_template("login.html", 
        title='Login to TigerResearch')

# ----------------------- ADD GROUP OFFICER ------------------------- #
@bp.route("/add_group_admin", methods=['GET'])
def add_group_admin():
    if check_user_validity():
        try:
            user = get_user_from_netid(session['username'])
            groupId = request.args.get('group')
            group = get_group(groupId)
            member = request.args.get('member')
            if (group.owner_id != user.id):
                raise Exception("User is not group owner")
            success = add_admin(groupid=groupId, newAdminId=member)
            new_admin = get_user_from_id(member)
            response_json = json.dumps({"success":success, "admin": encodeUser(new_admin)})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response
        except Exception as ex:
            print("An exception occured at '/add_group_admin':", ex)
            response_json = json.dumps({"success":False})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response

    return render_template("login.html", 
        title='Login to TigerResearch')

# ----------------------- ADD GROUP OFFICER ------------------------- #
@bp.route("/remove_group_admin", methods=['POST'])
def remove_group_admin():
    if check_user_validity():
        try:
            user = get_user_from_netid(session['username'])
            groupId = request.args.get('group')
            group = get_group(groupId)
            member = request.args.get('member')
            if (group.owner_id != user.id):
                raise Exception("User is not group owner")
            success = delete_admin(groupid=groupId, newAdminId=member)
            response_json = json.dumps({"success":success})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response
        except Exception as ex:
            print("An exception occured at '/remove_group_admin':", ex)
            response_json = json.dumps({"success":False})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response

    return render_template("login.html", 
        title='Login to TigerResearch')

# ----------------------- CHANGE GROUP NAME ------------------------- #
@bp.route("/change_group_name", methods=['POST'])
def change_group_name():
    if check_user_validity():
        try:
            user = get_user_from_netid(session['username'])
            groupId = request.args.get('group')
            group = get_group(groupId)
            name = request.args.get('name')
            if (group.owner_id != user.id):
                raise Exception("User is not group owner")
            update_group_name(groupid=groupId, newName=name)
            return redirect("/mygroups?groupId=" + groupId)
        except Exception as ex:
            print("An exception occured at '/change_group_name':", ex)
            response_json = json.dumps({"success":False})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response

    return render_template("login.html", 
        title='Login to TigerResearch')

# ------------------------------------------------------------------- #
#                         EVENT MUTATIONS                             #
# ------------------------------------------------------------------- #

# --------------------- CREATE CUSTOM EVENT ------------------------- # TODO: Review Authorization
@bp.route("/add_event", methods=['POST'])
def add_event():
    if check_user_validity():
        try:
            user = get_user_from_netid(session['username'])
            schedule = json.loads(request.get_data())
            group_id = schedule['groupId']
            # TODO: Make sure group_id is valid?
            group_id = int(group_id)
            group = get_group(group_id)
            # TODO: Make this error handling more precise; probably specialized exceptions
            if (len(group.members) == 0):
                response_json = json.dumps({"success": False, 
                    "message": "Cannot create event for group with 0 members"
                    })
                response = make_response(response_json)
                response.headers['Content-Type'] = 'application/json'
                return response
            name = schedule['name']
            if (name is None or name.strip() == ""):
                raise Exception("Name is absent")
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

# ------------------------- FINALIZE EVENT -------------------------- # TODO: FIX THIS PLEASE!!!!!!!!
@bp.route("/finalize_event_time/<eventid>/<timeid>", methods=['GET', 'POST'])
def finalize_event(eventid, timeid):
    if check_user_validity():
        try:
            user = get_user_from_netid(session['username'])
            event = get_event(eventid)
            if user.id != event.owner_id:
                raise Exception("User is not event owner.")
            event_finalize(eventid, timeid)
            return redirect("/scheduler")
        except Exception as ex:
            print("An exception occured at '/finalize_event':", ex)
            response_json = json.dumps({"success":False})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response
    return render_template("login.html", 
        title='Login to TigerPlan')

# ------------------------ DELETE EVENT ----------------------------- #
@bp.route("/del_event/<id>", methods=['POST'])
def del_event(id):
    if check_user_validity():
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

# ------------------------------------------------------------------- #
#                    INVITATION MUTATIONS                             #
# ------------------------------------------------------------------- #

# ------------------------------------------------------------------- # TODO: Review Authorization
### Respond to an invitation as an invitee. Called using AJAX in dashboard ###
# @bp.route("/respond_to_invitation/<id>", methods=['GET']) 
# def respond_to_invitation(id):
#     # TODO: Make JSON
#     if check_user_validity():
#         user = get_user_from_netid(session['username'])
#         try:
#             invitation = get_invitation(id)
#         except:
#             html = "<strong>Error fetching invitation<strong>"
#             return make_response(html)
#         if invitation.user_id != user.id:
#             html = "<strong>Error fetching invitation<strong>"
#             return make_response(html)
        
#         response_timeblockids = []

#         for invtb in invitation.responses:
#             response_timeblockids.append(invtb.timeblock_id)

#         return render_template("respondtoinvitation.html",
#             invitation=invitation, 
#             response_timeblockids=response_timeblockids)

#     return render_template("login.html", 
#         title='Login to TigerPlan')

@bp.route("/respond_to_invitation/<id>", methods=['GET']) 
def respond_to_invitation(id):
    if check_user_validity():
        try:
            user = get_user_from_netid(session['username'])
            id = int(id)
            invitation = get_invitation(id)
            if invitation.user_id != user.id:
                raise Exception("User is not invitation owner")

            event_times = []

            for timeblock in invitation.event.times:
                event_times.append(timeblock.to_json())
            response_json = json.dumps({"success":True, 
                "eventTimes": event_times,
                "eventName": invitation.event.name,
                "eventId": invitation.event_id,
                "eventDescription": invitation.event.description,
                "eventLocation": invitation.event.location
                })
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response
        except Exception as ex:
            print("An exception occured at '/respond_to_invitation':", ex)
            response_json = json.dumps({"success":False})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response
    return render_template("login.html", 
        title='Login to TigerPlan')


# ------------------- CREATE EVENT INVITATIONS ---------------------- #
@bp.route("/cr_event_invitations/<id>", methods=['POST'])
def add_invitations(id):
    if check_user_validity():
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

# # ------------------- EDIT INVITATION RESPONSE ---------------------- #
# @bp.route("/add_invitation_response_time/<invitationid>/<timeid>", methods=['POST'])
# def add_invitation_response_time(invitationid, timeid):
#     if check_user_validity():
#         user = get_user_from_netid(session['username'])
#         invitation = get_invitation(invitationid)
#         if invitation.user_id != user.id:
#             html = "<strong>Error fetching invitation<strong>"
#             # TODO: Make JSON
#             print("Invitation is not owned by user")
#             return make_response(html, 400)
#         else:
#             try:
#                 invitation_add_response_time(invitationid, timeid)
#             except ValueError as ex:
#                 html = "<strong>%s<strong>" % str(ex)
#                 # TODO: Make JSON
#                 print("value error", str(ex))
#                 return make_response(html, 400)
#             # TODO: Make JSON
#             return "Success!"
#     # TODO: Make JSON
#     return render_template("login.html", 
#         title='Login to TigerPlan')

# @bp.route("/del_invitation_response_time/<invitationid>/<timeid>", methods=['POST'])
# def del_invitation_response_time(invitationid, timeid):
#     if check_user_validity():
#         user = get_user_from_netid(session['username'])
#         invitation = get_invitation(invitationid)
#         if (invitation.user_id != user.id):
#             # TODO: Make JSON
#             html = "<strong>Error fetching invitation<strong>"
#             print("Invitation is not owned by user")
#             return make_response(html, 400)
#         else:
#             try:
#                 invitation_del_response_time(invitationid, timeid)
#             except ValueError as ex:
#                 # TODO: Make JSON
#                 html = "<strong>%s<strong>" % str(ex)
#                 print("value error", str(ex))
#                 return make_response(html, 400)
#             # TODO: Make JSON
#             return "Success!"
#     return render_template("login.html", 
#         title='Login to TigerPlan')

# ---------------------- FINALIZE INVITATION ------------------------ #
@bp.route("/finalize_invitation/<invitationid>", methods=['POST'])
def finalize_invitation(invitationid):
    if check_user_validity():
        try:
            print("finalizing invitation", invitationid)
            invitationid = int(invitationid)
            user = get_user_from_netid(session['username'])
            invitation = get_invitation(invitationid)
            if (invitation.user_id != user.id):
                raise Exception("Invitiation is not owned by user")
            timeblocks_chosen = json.loads(request.get_data())
            invitation_finalize(invitationid, timeblocks_chosen)
            response_json = json.dumps({"success":True})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response

        except Exception as ex:
            print("An exception occured at '/add_event':", ex)
            response_json = json.dumps({"success":False})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response
    else:
        return render_template("login.html", title='Login to TigerPlan')


# ------------------------------------------------------------------- #
#                      CALENDAR MUTATIONS                             # TODO: Review Authorization
# ------------------------------------------------------------------- #

# --------------------- ADD DEFAULT CONFLICT ------------------------ #
@bp.route("/saveNewSchedule/", methods=["GET", "POST"])
def saveNewSchedule():
    if check_user_validity():
        user = get_user_from_netid(session['username'])
        schedule = json.loads(request.get_data())
        start = datetime.fromisoformat(schedule['start']['_date'][:-1])
        end = datetime.fromisoformat(schedule['end']['_date'][:-1])

        tb = create_timeblock(name=schedule['title'], user=user, start=start, 
            end=end, isconflict=True)
        return make_response(jsonify(success=True, id=tb.id))
    return render_template("login.html", 
        title='Login to TigerResearch') 

# ------------------------------------------------------------------- #
@bp.route("/update_conflict/", methods=["GET", "POST"])
def update_conflict():
    if check_user_validity():
        user = get_user_from_netid(session['username'])
        schedule = json.loads(request.get_data())

        start = datetime.strptime(schedule['start'][5:], '%d %b %Y %H:%M:%S GMT')
        end = datetime.strptime(schedule['end'][5:], '%d %b %Y %H:%M:%S GMT')

         # retrieve database datetime
        update_timeblock(schedule['id'], schedule['title'], start, end)

        return make_response(jsonify(success=True))
    return render_template("login.html", 
        title='Login to TigerResearch') 

# ------------------------------------------------------------------- #
@bp.route("/add_conflict/", methods=['GET', 'POST'])
def add_conflict():
    if check_user_validity():
        user = get_user_from_netid(session['username'])
        a = datetime(2018, 11, 28)
        b = datetime(2018, 12, 28)
        create_timeblock(name="example", user=user, start=a, end=b, 
            isconflict=True)
        return redirect("/dashboard")
    return render_template("login.html", 
        title='Login to TigerResearch') 

# ------------------------ DELETE CONFLICT -------------------------- #
@bp.route("/del_conflict/<id>", methods=['POST'])
def del_conflict(id):
    if check_user_validity():
        try:
            user = get_user_from_netid(session['username'])
            id = int(id)
            timeblock = get_timeblock(id)
            if (user.id != timeblock.user_id):
                raise Exception("User is not Timeblock owner")        
            delete_timeblock(id)
            response_json = json.dumps({"success":True})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response
        except Exception as ex:
            print("An error occurred at del_conflict:", ex)
            response_json = json.dumps({"success":False})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response
    return render_template("login.html", 
        title='Login to TigerResearch') 

# ------------------------------------------------------------------- #
#                       AUTHORIZATION ROUTES                          #
# ------------------------------------------------------------------- #

# -------------------------- LOGIN PAGE ----------------------------- #

@bp.route("/login", methods=['GET', 'POST'])
def login():
    # Already logged in
    if check_user_validity():
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