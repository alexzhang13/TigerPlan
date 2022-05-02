from app.src.group import add_admin, add_member, create_group, delete_admin, delete_group, delete_member, get_group, get_group_admin, get_group_events, get_members, update_group_name, update_owner
from app.src.timeblock import create_timeblock, delete_timeblock, get_timeblock, update_timeblock
from app.src.user import get_admin_groups, get_member_groups, get_member_invitations, get_user_conflicts, get_user_events, get_user_from_id, get_user_groups, get_user_from_netid, get_user_member_finalized_event_times, get_user_onetime_conflicts, get_user_recurring_conflicts, get_users, is_admin
from app.src.event import create_event, create_event_invitations, delete_event, event_finalize, get_event, get_invitation_response_times
from app.src.invitation import get_invitation, invitation_finalize
from flask import render_template, current_app, redirect, url_for, session, request, make_response, jsonify
from flask_login import login_user, logout_user, login_required 
from cas import CASClient
from datetime import datetime, timedelta
import json

from app import db
from app.main import bp
from app.models import models

cas_client = CASClient(
    version=3,
    service_url='http://tigerplan.herokuapp.com/login',
    server_url='https://fed.princeton.edu/cas/login'
)

# ----------------------- HELPER FUNCTIONS -------------------------- #

'''
@bp.before_request
def before_request():
    if not request.is_secure:
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)
'''

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

def check_int(val):
    if isinstance(val, str) and val.isdigit(): return int(val)
    elif isinstance(val, int): return val
    elif val is None: return None
    raise Exception("Invalid integer value.", val, type(val))

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
            groups=groups, events=events, page='index')
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
            conflicts=conflicts, invitations=invitations, page='dashboard')
    return render_template("login.html", 
        title='Login to TigerResearch')

# ---------------------------- DASHBOARD ---------------------------- #
@bp.route("/memberships", methods=['GET'])
def memberships():
    if check_user_validity():
        user = get_user_from_netid(session['username'])
        membergroups = get_member_groups(user.id)
        return render_template("memberships.html",
            title='TigerPlan User Dashboard', user=session['username'], 
            memberships = membergroups, page='memberships')
    return render_template("login.html", 
        title='Login to TigerResearch')

# ---------------------------- DASHBOARD ---------------------------- #
@bp.route("/about", methods=['GET'])
def about():
    if check_user_validity():
        return render_template("about.html",
            title='TigerPlan User Dashboard', user=session['username'], page='about')
    return render_template("login.html", 
        title='Login to TigerResearch')

# -------------------------- EDIT CONFLICTS ------------------------- #
@bp.route("/editconflicts", methods=['GET'])
def editconflicts():
    if check_user_validity():
        user = get_user_from_netid(session['username'])
        groups = get_user_groups(user.id)
        events = get_user_events(user.id)
        return render_template("editconflicts.html",
            title='TigerPlan Conflicts', user=session['username'],
            groups=groups, events=events, page='editconflicts')
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
        groupId = check_int(request.args.get("groupId"))
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
                    user=session['username'], groups=groups, page='groups')
            return render_template("mygroups.html", 
                title='TigerPlan Manage Groups', 
                user=session['username'],
                groups=groups, admin_groups=admin_groups, 
                admins=admins, users=users, members=members, 
                this_group=group, events=events, page='groups')
        return render_template("mygroups.html", 
            title='TigerPlan Manage Groups', 
            user=session['username'], groups=groups, 
            admin_groups=admin_groups, page='groups')
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
            result.append(output)
    elif isinstance(userObj, models.User):
        output = {}
        output['id'] = userObj.id
        output['netid'] = userObj.netid
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
            output['finalized'] = event.finalized
            chosen_time = event.times[0]
            chosen_time_json = { 
                "start": (chosen_time.start - timedelta(hours=4)).strftime('%B %d, %Y %I:%M %p'),
                "end": (chosen_time.end - timedelta(hours=4)).strftime('%B %d, %Y %I:%M %p') if (chosen_time.start - timedelta(hours=4)).date() != (chosen_time.end - timedelta(hours=4)).date() else (chosen_time.end - timedelta(hours=4)).strftime('%I:%M %p'),
                "id": chosen_time.id
            }
            output['final_time'] =chosen_time_json
            result.append(output)
    elif isinstance(eventObj, models.Event):
        output = {}
        output['id'] = eventObj.id
        output['name'] = eventObj.name
        output['location'] = eventObj.location
        output['description'] = eventObj.description
        output['finalized'] = event.finalized
        chosen_time = eventObj.times[0]
        chosen_time_json = { 
            "start": (chosen_time.start - timedelta(hours=4)).strftime('%B %d, %Y %I:%M %p'),
            "end": (chosen_time.end - timedelta(hours=4)).strftime('%B %d, %Y %I:%M %p') if (chosen_time.start - timedelta(hours=4)).date() != (chosen_time.end - timedelta(hours=4)).date() else (chosen_time.end - timedelta(hours=4)).strftime('%I:%M %p'),
            "id": chosen_time.id
        }
        output['final_time'] =chosen_time_json
        return output
    return result

# -------------------------- MANAGE GROUPS -------------------------- #
@bp.route("/mygroupinfo", methods=['GET'])
def groupinfo():
    if check_user_validity():
        try:
            user = get_user_from_netid(session['username'])
            groupId = check_int(request.args.get('groupId'))
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
                        "events": events, "admins": admins,
                        "exclude_id": user.id, "name": group.name})
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
            admin_groups = admin_groups, page='scheduler')
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
            admin_groups = admin_groups, page='manage_events')
    return render_template("login.html", 
        title='Login to TigerResearch') 

# ------------------------- EVENT DETAILS --------------------------- #

@bp.route("/view_event_details/<id>", methods=['GET', 'POST'])
def view_event_details(id):
    if check_user_validity():
        try:
            user = get_user_from_netid(session['username'])
            event = get_event(id)

            if (event.owner_id != user.id):
                raise Exception("User is not event owner") 

            if not event.finalized:
                response_times, num = get_invitation_response_times(event.id)
                response_json = json.dumps({
                    "success":True,
                    "finalized":False,
                    "responseTimes": response_times,
                    "numResponses": num
                })
                response = make_response(response_json)
                response.headers['Content-Type'] = 'application/json'
                return response
            chosen_time = event.times[0]
            chosen_time_json = { 
                "start": chosen_time.start.strftime('%Y-%m-%dT%H:%M:%S'),
                "end": chosen_time.end.strftime('%Y-%m-%dT%H:%M:%S'),
                "id": chosen_time.id
            }
            response_json = json.dumps({
                "success":True,
                "finalized":True,
                "chosenTime":chosen_time_json,
                "eventName": event.name,
                "eventId": event.id
                })
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response
        except Exception as ex:
            print("An error occurred in view_event_details:", ex)
            response_json = json.dumps({"success":False})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response
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

# -------------------------- DELETE GROUP --------------------------- #
@bp.route("/del_group", methods=['POST'])
def del_group():
    if check_user_validity():
        try:
            user = get_user_from_netid(session['username'])
            group_id = check_int(request.args.get('group'))
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
            group_id = check_int(request.args.get('groupId'))
            member_id = check_int(request.args.get('memberId'))
            group = get_group(group_id)
            if (user.id != group.owner_id):
                raise Exception("User is not group owner.")
            old_member = get_user_from_id(member_id)
            if old_member is None:
                raise Exception("User was not found.")
            success = delete_member(group_id, member_id)
            response = make_response(json.dumps({"success":success, "old_member": encodeUser(old_member)}))
            response.headers['Content-Type'] = 'application/json'
            return response
        except Exception as ex:
            print("An exception occured at '/remove_member':", ex)
            response_json = json.dumps({"success":False})
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
            group_id = check_int(request.args.get('group'))
            group = get_group(group_id)
            if (group.owner_id != user.id):
                raise Exception("User is not group owner")
            member_id = check_int(request.args.get('member'))
            if (member_id is None): 
                raise Exception("New member not specified")
            redudant = not add_member(id=group_id, memberId=member_id)
            member = get_user_from_id(member_id)
            if (member is None):
                raise Exception("User does not exist")
            response_json = json.dumps({"success": True,
                "redundant": redudant,
                "memberNetid": member.netid, 
                "exclude_id": member.id == group.owner_id})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response
        except Exception as ex:
            print("An exception occured at '/add_new_member':", ex)
            response_json = json.dumps({"success":False, "error": str(ex)})
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
            groupId = check_int(request.args.get('group'))
            group = get_group(groupId)
            member = check_int(request.args.get('member'))
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

# ----------------------- TRANSFER OWNERSHIP ------------------------- #
@bp.route("/leaveGroup", methods=['POST'])
def leave_group():
    if check_user_validity():
        try:
            user = get_user_from_netid(session['username'])
            groupId = check_int(request.args.get('group'))
            success = delete_member(groupId, user.id)
            response_json = json.dumps({"success":success})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response
        except Exception as ex:
            print("An exception occured at '/leaveGroup':", ex)
            response_json = json.dumps({"success":False})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response

    return render_template("login.html", 
        title='Login to TigerResearch')

# ----------------------- ADD GROUP OFFICER ------------------------- #
@bp.route("/add_group_admin", methods=['POST'])
def add_group_admin():
    if check_user_validity():
        try:
            user = get_user_from_netid(session['username'])
            groupId = check_int(request.args.get('group'))
            group = get_group(groupId)
            member = check_int(request.args.get('member'))
            if (group.owner_id != user.id):
                raise Exception("User is not group owner")
            if (group.owner_id == member):
                raise Exception("Group owner can not be a group admin.")
            else:
                success = add_admin(groupid=groupId, newAdminId=member)
                new_admin = get_user_from_id(member)
                response_json = json.dumps({"success":success, "admin": encodeUser(new_admin)})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response
        except Exception as ex:
            print("An exception occured at '/add_group_admin':", ex)
            response_json = json.dumps({"success":False, "isOwner": False})
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
            groupId = check_int(request.args.get('group'))
            group = get_group(groupId)
            memberId = check_int(request.args.get('member'))
            if (group.owner_id != user.id):
                raise Exception("User is not group owner")
            old_admin = get_user_from_id(memberId)
            success = delete_admin(groupid=groupId, newAdminId=memberId)
            response_json = json.dumps({"success":success, "old_admin": encodeUser(old_admin)})
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
            groupId = check_int(request.args.get('group'))
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

def check_event_priviliges(group, user):
    if group.owner_id == user.id:
        return True
    elif is_admin(user.id, group.id):
        return True
    return False

# --------------------- CREATE CUSTOM EVENT ------------------------- # TODO: Lu Review Authorization - admins?
@bp.route("/add_event", methods=['POST'])
def add_event():
    if check_user_validity():
        try:
            user = get_user_from_netid(session['username'])
            schedule = json.loads(request.get_data())
            group_id = schedule['groupId']
            name = schedule['name']
            location = schedule['location']
            description = schedule['description']
            timeblocks = schedule['timeblocks']
            is_recurring = schedule['isRecurring']
            try:
                group = get_group(group_id)
            except Exception as ex:
                raise Exception("Group not found.") from ex
            if check_event_priviliges(group, user) == False:
                raise Exception("User is not authorized to create an event for this group.")
            if (len(group.members) == 0):
                raise Exception("Cannot create event for group with no members.")
            if (name is None or name.strip() == ""):
                raise Exception("Please specify a name for the event.")
            if (len(timeblocks) == 0):
                raise Exception("Please specify at least one time.")
            
            new_event = create_event(groupid=group_id, name=name,
                                    owner=user, location=location, 
                                    description=description,
                                    timeblocks=timeblocks,
                                    is_recurring=is_recurring)
            response_json = json.dumps({
                "success":True, 
                "newEventId":new_event.id,
                "groupName":new_event.group.name
            })
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response
        except Exception as ex:
            print("An exception occured at '/add_event':", ex)
            response_json = json.dumps({"success":False, "message": str(ex)})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response
    return render_template("login.html", 
        title='Login to TigerPlan')

# ------------------------- FINALIZE EVENT -------------------------- #
@bp.route("/finalize_event_time", methods=['POST'])
def finalize_event():
    if check_user_validity():
        eventid = check_int(request.args.get('eventid'))
        timeid = check_int(request.args.get('timeid'))
        try:
            user = get_user_from_netid(session['username'])
            event = get_event(eventid)
            if user.id != event.owner_id:
                raise Exception("User is not event owner.")
            event_finalize(eventid, timeid)
            response_json = json.dumps({"success": True})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response
        except Exception as ex:
            print("An exception occured at '/finalize_event':", ex)
            response_json = json.dumps({"success": False})
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

            conflicts = get_user_conflicts(user.id)
            conflicts = [conflict.to_json() for conflict in conflicts]

            response_json = json.dumps({"success":True, 
                "eventTimes": event_times,
                "eventName": invitation.event.name,
                "eventId": invitation.event_id,
                "eventDescription": invitation.event.description,
                "eventLocation": invitation.event.location,
                "userConflicts": conflicts,
                "eventIsRecurring": invitation.event.is_recurring
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
        try:
            user = get_user_from_netid(session['username'])
            event = get_event(id)
            if (event.owner_id != user.id):
                raise Exception("User is not event owner")
            create_event_invitations(id) 
            response_json = json.dumps({"success":True})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response
        except Exception as ex:
            print("An exception occured at '/cr_event_invitations':", ex)
            response_json = json.dumps({"success":False})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response
    return render_template("login.html", 
        title='Login to TigerPlan')

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
#                      CALENDAR MUTATIONS                             #
# ------------------------------------------------------------------- #

# --------------------- ADD DEFAULT CONFLICT ------------------------ #
@bp.route("/saveNewSchedule", methods=["GET", "POST"])
def saveNewSchedule():
    if check_user_validity():
        user = get_user_from_netid(session['username'])
        schedule = json.loads(request.get_data())
        start = datetime.fromisoformat(schedule['start']['_date'][:-1])
        end = datetime.fromisoformat(schedule['end']['_date'][:-1])
        is_recurring = schedule['isRecurring']

        tb = create_timeblock(name=schedule['title'], user=user, start=start, 
            end=end, isconflict=True, is_recurring=is_recurring)
        return make_response(jsonify(success=True, id=tb.id))
    return render_template("login.html", 
        title='Login to TigerResearch') 

# ------------------------------------------------------------------- #
@bp.route("/update_conflict", methods=["GET", "POST"])
def update_conflict():
    if check_user_validity():
        user = get_user_from_netid(session['username'])
        schedule = json.loads(request.get_data())
        start = None
        end = None
        
        if schedule['start'] is not None:
            start = datetime.strptime(schedule['start'][5:], '%d %b %Y %H:%M:%S GMT')
        if schedule['end'] is not None:
            end = datetime.strptime(schedule['end'][5:], '%d %b %Y %H:%M:%S GMT')

         # retrieve database datetime
        try:
            conflict = get_timeblock(schedule['id'])
            if conflict.user_id != user.id:
                raise Exception("User is not conflict owner")
            update_timeblock(schedule['id'], schedule['title'], start, end)
        except Exception as ex:
            print("An error occured at /update_conflict:", ex)
            return make_response(jsonify(success=False))

        return make_response(jsonify(success=True))
    return render_template("login.html", 
        title='Login to TigerResearch') 

# ------------------------------------------------------------------- #
@bp.route("/add_conflict", methods=['GET', 'POST'])
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
            print("An error occurred at /del_conflict:", ex)
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

    if check_user_validity():
        try:
            user = get_user_from_netid(session['username'])
            conflicts = get_user_conflicts(user.id)
            conflicts = [conflict.to_json() for conflict in conflicts]
            event_times = get_user_member_finalized_event_times(user.id)
            event_times_json = []
            for event_time in event_times:
                event = get_event(event_time.event_id)
                event_json = event_time.to_json()
                event_json['name'] = event.name
                event_times_json.append(event_json)
            response_json = json.dumps({
                "success":True,
                "conflicts":conflicts,
                "finalizedEvents":event_times_json
                })
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response
        except Exception as ex:
            print("An error occurred at /load_conflicts:", ex)
            response_json = json.dumps({"success":False})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response
    return render_template("login.html", 
        title='Login to TigerResearch') 

@bp.route("/load_edit_conflicts", methods=['GET', 'POST'])
def load_edit_conflicts():

    if check_user_validity():
        try:
            user = get_user_from_netid(session['username'])
            recurring_conflicts = get_user_recurring_conflicts(user.id)
            recurring_conflicts = [conflict.to_json() for conflict in recurring_conflicts]
            onetime_conflicts = get_user_onetime_conflicts(user.id)
            onetime_conflicts = [conflict.to_json() for conflict in onetime_conflicts]
            response_json = json.dumps({
                "success": True,
                "recurringConflicts": recurring_conflicts,
                "onetimeConflicts": onetime_conflicts,
                })
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response
        except Exception as ex:
            print("An error occurred at /load_edit_conflicts:", ex)
            response_json = json.dumps({"success":False})
            response = make_response(response_json)
            response.headers['Content-Type'] = 'application/json'
            return response
    return render_template("login.html", 
        title='Login to TigerResearch') 
