from flask import Blueprint, render_template, request, session, redirect, url_for
from model import helpers, dbmain, dbproj, dbtasks
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
    roster = dbproj.roster(dbmain.currentPFID())
    students = roster['students']
    mentors = roster['mentors']
    return render_template('roster.html', user=dbmain.currentUser(), fair=dbmain.currentFair(), students=students, mentors=mentors)

@participants.route('/approvals/')
def approvals():
    roster = dbproj.rosterForApprovals(dbmain.currentPFID())
    rejected = roster["-2"]
    pending = roster["-1"]
    notsubmitted = roster["0"]
    approved = roster["1"]
    return render_template('approvals.html', user=dbmain.currentUser(), fair=dbmain.currentFair(), rejected=rejected, pending=pending, notsubmitted=notsubmitted, approved=approved)

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
    # check to see if mentor or student
    utype = user["acct_type"]
    if utype == "Administrator":
        return render_template('errors/generic_error.html', user=dbmain.currentUser(), title="No Profile for Administrators", contents="Users who are administrators do not have profile pages.")
    # get information about the project
    partners = []
    project = None
    if utype == "Mentor":
        pairlist = dbmain.pairingsForMentor(user["_id"])
        for student in pairlist:
            student["project_contents"] = dbproj.projectForUser(student["_id"])
            student["approval_status"] = db.proj.approvalStatusString(dbproj.approvalStatus(student["_id"], pfid))
            partners.append(student)
    elif utype == "Student":
        partners = dbmain.pairingsForStudent(user["_id"])
        project = dbproj.projectForUser(user["_id"])
        project["approval_status"] = dbproj.approvalStatusString(dbproj.approvalStatus(user["_id"], pfid))
    # render the profile
    return render_template('profile.html', user=dbmain.currentUser(), subject=user, partners=partners, project=project)

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

@participants.route('/tasks/')
def tasks():
    return render_template('tasks.html', user=dbmain.currentUser(), fair=dbmain.currentFair())

@participants.route('/progress/')
def progress():
    fair = dbmain.currentFair()
    progresses = dbtasks.progressReport(fair["_id"])
    return render_template('progress.html', user=dbmain.currentUser(), fair=fair, progresses=progresses)

@participants.route('/progress/<string:username>')
def user_progress(username):
    fair = dbmain.currentFair()
    # check to make sure user is valid
    user = dbmain.userIfExists(username)
    user_id = user["_id"]
    if user == None:
        return render_template('errors/generic_error.html', user=dbmain.currentUser(), title="User Does Not Exist", contents="The user you requested to access does not exist.")
    # check to make sure user is in fair
    if not dbmain.userIsRegisteredForFair(user_id, fair["_id"]):
        return render_template('errors/generic_error.html', user=dbmain.currentUser(), title="User Not In Fair", contents="The user you requested to access is not part of your current primary fair.")
    progresses = dbtasks.getProgressesForUser(user_id, fair["_id"])
    target = dbmain.userById(user_id)
    return render_template('user_progress.html', user=dbmain.currentUser(), fair=fair, progresses=progresses, target=target)

@participants.route('/tasks/<string:task_id>/')
def task_view(task_id):
    task_id = ObjectId(task_id)
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
    return render_template('task_view.html', user=dbmain.currentUser(), fair=fair, task=task, progresses=progresses)