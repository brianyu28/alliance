from flask import Blueprint, render_template, request, session, redirect, url_for
from model import helpers, dbmain, dbproj, dbtasks, dbcomm
from bson import ObjectId
import re

# "Participants" is the name for the "Rosters" tab, was renamed on the interface earlier
participants = Blueprint('participants', __name__,
                        template_folder='../templates/participants')

@participants.before_request
def check():
    if 'id' not in session:
        return redirect(url_for('home.homepage'))
    if not dbmain.isAdmin():
        return render_template('errors/no_permissions.html', user=dbmain.currentUser())
    pfid = dbmain.currentPFID()
    if pfid == None:
        return render_template('errors/no_primary_fair.html', user=dbmain.currentUser())

@participants.route('/')
def roster():
    pfid = dbmain.currentPFID()
    roster = dbproj.roster(pfid)
    students = roster['students']
    mentors = roster['mentors']
    
    # if not full access, then filter approvals to only show allowed approvals
    if not dbmain.permissionCheck(ObjectId(session['id']), pfid, "full_access"):
        new_roster = {"students":[], "mentors":[]}
        for student in students:
            if not dbmain.someTrainingExists(pfid, student['_id'], ObjectId(session['id'])):
                student["access_permitted"] = False
            new_roster["students"].append(student)
        for mentor in mentors:
            if not dbmain.someTrainingExists(pfid, mentor['_id'], ObjectId(session['id'])):
                mentor["access_permitted"] = False
            new_roster["mentors"].append(mentor)
        students = new_roster["students"]
        mentors = new_roster["mentors"]
    
    return render_template('roster.html', user=dbmain.currentUser(), fair=dbmain.currentFair(), students=students, mentors=mentors)

# Permissions: Full Access or greater, or Partial Access with a relationship
@participants.route('/approvals/')
def approvals():
    pfid = dbmain.currentPFID()
    # if no access, then reject
    if not dbmain.permissionCheck(ObjectId(session['id']), pfid, "some_access"):
        return render_template('errors/no_permissions.html', user=dbmain.currentUser())
    
    roster = dbproj.rosterForApprovals(dbmain.currentPFID())
    
    # if not full access, then filter approvals to only show allowed approvals
    if not dbmain.permissionCheck(ObjectId(session['id']), pfid, "full_access"):
        new_roster = {"-2":[], "-1":[], "0":[], "1":[]}
        for group in roster:
            for student in roster[group]:
                if dbmain.someTrainingExists(pfid, student['_id'], ObjectId(session['id'])):
                    new_roster[str(int(student["proj_approved"]))].append(student)
        roster = new_roster
        
    rejected = roster["-2"]
    pending = roster["-1"]
    notsubmitted = roster["0"]
    approved = roster["1"]
    return render_template('approvals.html', user=dbmain.currentUser(), fair=dbmain.currentFair(), rejected=rejected, pending=pending, notsubmitted=notsubmitted, approved=approved)

# Permissions: Full Access or greater, or Partial Access with a relationship
@participants.route('/<string:username>/')
def profile(username):
    # check to make sure username exists
    user = dbmain.userIfExists(username)
    pfid = dbmain.currentPFID()
    if user == None:
        return render_template('errors/generic_error.html', user=dbmain.currentUser(), title="No User Exists", contents="There is no user with the username that you requested.")
    # check to make sure that the user is registered for the fair
    registered = dbmain.userIsRegisteredForFair(user['_id'], pfid)
    if not registered:
        return render_template('errors/generic_error.html', user=dbmain.currentUser(), title="User Not Registered", contents="The user you requested to view is not registered for this fair.")
    
    # check permissions
    if dbmain.accessLevelForUser(ObjectId(session['id']), pfid) == "No Access":
        return render_template('errors/no_permissions.html', user=dbmain.currentUser())
    if dbmain.permissionCheck(ObjectId(session['id']), pfid, "some_access") and not dbmain.someTrainingExists(pfid, user['_id'], ObjectId(session['id'])):
        return render_template('errors/no_permissions.html', user=dbmain.currentUser())
    
    # check to see if mentor or student
    utype = user["acct_type"]
    if utype == "Administrator":
        return render_template('errors/generic_error.html', user=dbmain.currentUser(), title="No Profile for Administrators", contents="Users who are administrators do not have profile pages.")
    # get information about the project
    partners = []
    project = None
    progress = None
    if utype == "Mentor":
        pairlist = dbmain.pairingsForMentor(user["_id"])
        for student in pairlist:
            student["project_contents"] = dbproj.projectForUser(student["_id"])
            student["approval_status"] = dbproj.approvalStatusString(dbproj.approvalStatus(student["_id"], pfid))
            student["conversation"] = dbcomm.getConversation([user['_id'], student['_id']])
            student["conversation"] = student["conversation"]["_id"] if student["conversation"] != None else None
            partners.append(student)
        progress = dbtasks.userProgressReport(user['_id'], pfid)
    elif utype == "Student":
        partners = dbmain.pairingsForStudent(user["_id"])
        project = dbproj.projectForUser(user["_id"])
        project["approval_status"] = dbproj.approvalStatusString(dbproj.approvalStatus(user["_id"], pfid))
    # render the profile
    return render_template('profile.html', user=dbmain.currentUser(), subject=user, partners=partners, project=project, progress=progress)

# Permissions: Full Access or greater, or Partial Access with a relationship
@participants.route('/<string:username>/project/')
def project(username):
    # check to make sure username exists
    user = dbmain.userIfExists(username)
    pfid = dbmain.currentPFID()
    if user == None:
        return render_template('errors/generic_error.html', user=dbmain.currentUser(), title="No User Exists", contents="There is no user with the username that you requested.")
    # check to make sure that the user is registered for the fair
    registered = dbmain.userIsRegisteredForFair(user['_id'], pfid)
    if not registered:
        return render_template('errors/generic_error.html', user=dbmain.currentUser(), title="User Not Registered", contents="The user you requested to view is not registered for this fair.")
    
    # check permissions
    if dbmain.accessLevelForUser(ObjectId(session['id']), pfid) == "No Access":
        return render_template('errors/no_permissions.html', user=dbmain.currentUser())
    if dbmain.permissionCheck(ObjectId(session['id']), pfid, "some_access") and not dbmain.someTrainingExists(pfid, user['_id'], ObjectId(session['id'])):
        return render_template('errors/no_permissions.html', user=dbmain.currentUser())
    
    # check to see if student
    utype = user["acct_type"]
    if utype != "Student":
        return render_template('errors/generic_error.html', user=dbmain.currentUser(), title="No Projects for Non-Students", contents="Only students have projects.")
    # get the user's project
    project = dbproj.projectForUser(user["_id"])
    # fields to show. Each is array of form [Human-Readable Name, Database Field, Rows for Editing]
    fields = []
    fields.append(["Title", "title", 1])
    fields.append(["Question", "question", 2])
    fields.append(["Purpose", "purpose", 2])
    fields.append(["Research Rationale", "rationale", 3])
    fields.append(["Hypothesis", "hypothesis", 3])
    fields.append(["Null Hypothesis", "nullhypo", 3])
    fields.append(["Independent Variable", "ivar", 1])
    fields.append(["Dependent Variable", "dvar", 1])
    fields.append(["Controlled Variables", "cvars", 3])
    fields.append(["Control", "control", 2])
    fields.append(["Background Research", "background", 7])
    fields.append(["Materials", "materials", 7])
    fields.append(["Procedure", "procedure", 7])
    fields.append(["Data", "data", 7])
    fields.append(["Discussion of Results", "discussion", 7])
    fields.append(["Conclusion", "materials", 5])
    fields.append(["Acknowledgements", "acknowledgements", 3])
    
    # get project approval information
    approval_status = dbproj.approvalStatus(user['_id'], pfid)
    return render_template('view_project.html', user=dbmain.currentUser(), fair=dbmain.currentFair(), fields=fields, project=project, author=user, approval_status=int(approval_status))

# Anyone can see tasks, only Full Access can edit
@participants.route('/tasks/')
def tasks():
    pfid = dbmain.currentPFID()
    can_edit = dbmain.permissionCheck(ObjectId(session['id']), pfid, "full_access")
    return render_template('tasks.html', user=dbmain.currentUser(), fair=dbmain.currentFair(), can_edit=can_edit)

# Permissions: anyone can see
@participants.route('/progress/')
def progress():
    fair = dbmain.currentFair()
    pfid = dbmain.currentPFID()
    progresses = dbtasks.progressReport(fair["_id"])
    
    # if not full access, then filter approvals to only show allowed approvals
    if not dbmain.permissionCheck(ObjectId(session['id']), pfid, "full_access"):
        new_roster = []
        for mentor in progresses:
            if not dbmain.someTrainingExists(pfid, mentor['_id'], ObjectId(session['id'])):
                mentor["access_permitted"] = False
            new_roster.append(mentor)
        progresses = new_roster
        
    return render_template('progress.html', user=dbmain.currentUser(), fair=fair, progresses=progresses)

# Permissions: Full Access, or training with partial access
@participants.route('/progress/<string:username>')
def user_progress(username):
    fair = dbmain.currentFair()
    pfid = dbmain.currentPFID()
    # check to make sure user is valid
    user = dbmain.userIfExists(username)
    user_id = user["_id"]
    if user == None:
        return render_template('errors/generic_error.html', user=dbmain.currentUser(), title="User Does Not Exist", contents="The user you requested to access does not exist.")
    # check to make sure user is in fair
    if not dbmain.userIsRegisteredForFair(user_id, fair["_id"]):
        return render_template('errors/generic_error.html', user=dbmain.currentUser(), title="User Not In Fair", contents="The user you requested to access is not part of your current primary fair.")
    
    # check permissions
    if dbmain.accessLevelForUser(ObjectId(session['id']), pfid) == "No Access":
        return render_template('errors/no_permissions.html', user=dbmain.currentUser())
    if dbmain.permissionCheck(ObjectId(session['id']), pfid, "some_access") and not dbmain.someTrainingExists(pfid, user['_id'], ObjectId(session['id'])):
        return render_template('errors/no_permissions.html', user=dbmain.currentUser())
    
    progresses = dbtasks.getProgressesForUser(user_id, fair["_id"])
    target = dbmain.userById(user_id)
    return render_template('user_progress.html', user=dbmain.currentUser(), fair=fair, progresses=progresses, target=target)

@participants.route('/tasks/<string:task_id>/')
def task_view(task_id):
    task_id = ObjectId(task_id)
    pfid = dbmain.currentPFID()
    # check to make sure that task is valid
    if not dbtasks.taskExists(task_id):
        return render_template('errors/generic_error.html', user=dbmain.currentUser(), title="Task Does Not Exist", contents="The task you requested to view does not exist.")
    # check to make sure that the task is in the fair
    task = dbtasks.taskById(task_id)
    fair = dbmain.currentFair()
    if task["fair"] != fair["_id"]:
        return render_template('errors/generic_error.html', user=dbmain.currentUser(), title="Task Not In Fair", contents="The task you requested to view is not part of your current primary fair.")
    # get progresses
    progresses = dbtasks.getProgressesForTask(task_id)
    
    # if no complete access, then only show approved
    if dbmain.accessLevelForUser(ObjectId(session['id']), pfid) == "No Access":
        return render_template('errors/no_permissions.html', user=dbmain.currentUser())
    if not dbmain.permissionCheck(ObjectId(session['id']), pfid, "full_access"):
        new_progresses = []
        for user in progresses:
            if dbmain.someTrainingExists(pfid, user['_id'], ObjectId(session['id'])):
                new_progresses.append(user)
        progresses = new_progresses
    
    return render_template('task_view.html', user=dbmain.currentUser(), fair=fair, task=task, progresses=progresses)


@participants.route('/conversation/<string:conversation_id>')
def view_conversation(conversation_id):
    user = dbmain.currentUser()
    fair = dbmain.currentFair()
    pfid = dbmain.currentPFID()
    # check to make sure conversation is valid
    conversation = dbcomm.conversationIfExists(ObjectId(conversation_id))
    if conversation == None:
        return render_template('errors/generic_error.html', user=dbmain.currentUser(), title="Conversation Does Not Exist", contents="The conversation you requested to view does not exist.")
    
    # check to make sure people in conversation are in the fair
    conversers = dbcomm.usersInConversation(conversation)
    for converser in conversers:
        if not dbmain.userIsRegisteredForFair(converser['_id'], pfid):
            return render_template('errors/no_permissions.html', user=dbmain.currentUser())
    
    # check permissions
    if dbmain.accessLevelForUser(ObjectId(session['id']), pfid) == "No Access":
        return render_template('errors/no_permissions.html', user=dbmain.currentUser())
    if not dbmain.permissionCheck(ObjectId(session['id']), pfid, "full_access"):
        for converser in conversers:
            if not dbmain.someTrainingExists(pfid, converser['_id'], ObjectId(session['id'])):
                return render_template('errors/no_permissions.html', user=dbmain.currentUser())
    
    return render_template('conversation_view.html', user=user, fair=fair, selected=conversation_id)