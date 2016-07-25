from flask import Blueprint, render_template, request, session, redirect, url_for
from model import helpers, dbmain, dbtasks
from bson import ObjectId
import re

fair = Blueprint('fair', __name__,
                        template_folder='../templates/fair')

@fair.before_request
def check():
    if 'id' not in session:
        return redirect(url_for('home.homepage'))

@fair.route('/')
def fair_page():
    return redirect(url_for('fair.manage'))

@fair.route('/manage/', methods=['GET', 'POST'])
def manage():
    error = None
    if request.method == 'POST' and request.form['type'] == 'Register':
        name = request.form['name']
        date = request.form['date']
        location = request.form['location']
        private = 'private' in request.form
        r = re.compile('\d{1,2}/\d{1,2}/\d{4}')
        if name == "":
            error = "You did not specify a name for the fair."
        elif r.match(date) is None:
            error = "You did not specify a valid date."
        elif location == "":
            error = "You did not specify a valid location."
        else:
            fair_id = dbmain.addFair(name, date, location, private)
            dbmain.addRegistration(ObjectId(session['id']), fair_id, True)
            dbmain.addPermission(ObjectId(session['id']), fair_id, "is_owner")
            dbmain.changePrimaryFair(ObjectId(session['id']), fair_id)
    if request.method == 'POST' and request.form['type'] == 'Join':
        fair = dbmain.fair(request.form['fair'])
        approved = False if fair['private'] else True
        dbmain.addRegistration(ObjectId(session['id']), ObjectId(request.form['fair']), approved)
        dbtasks.generateProgressesForUser(ObjectId(session['id']), ObjectId(request.form['fair']))
        dbmain.changePrimaryFair(ObjectId(session['id']), ObjectId(request.form['fair']))
    if request.method == 'POST' and request.form['type'] == 'Leave':
        dbmain.removeRegistration(ObjectId(session['id']), ObjectId(request.form['fair']))
        dbtasks.deleteProgressesForUserInFair(ObjectId(session['id']), ObjectId(request.form['fair']))
        if ObjectId(request.form['fair']) == dbmain.currentUser()['primary']:
            dbmain.changePrimaryFair(ObjectId(session['id']), None)
    registration = dbmain.fairsForUser(ObjectId(session['id']))
    unjoined = dbmain.unjoinedFairs(ObjectId(session['id']))
    return render_template('manage.html', user=dbmain.currentUser(), registration=registration, unjoined=unjoined, error=error)

@fair.route('/requests/')
def requests():
    if not dbmain.isAdmin():
        return render_template('errors/no_permissions.html', user=dbmain.currentUser())
    pfid = dbmain.currentPFID()
    if pfid == None:
        return render_template('errors/no_primary_fair.html', user=dbmain.currentUser())
    if not dbmain.permissionCheck(ObjectId(session['id']), pfid, "can_approve_users"):
        return render_template('errors/no_permissions.html', user=dbmain.currentUser())
    requests = dbmain.pendingRequestsForFair(pfid)
    students = []
    mentors = []
    admins = []
    for request in requests:
        if request['acct_type'] == "Student":
            students.append(request)
        elif request['acct_type'] == "Mentor":
            mentors.append(request)
        elif request['acct_type'] == "Administrator":
            admins.append(request)
    return render_template('requests.html', user=dbmain.currentUser(), fair=dbmain.currentFair(), students=students, mentors=mentors, admins=admins)

@fair.route('/pair/')
def pair():
    if not dbmain.isAdmin():
        return render_template('errors/no_permissions.html', user=dbmain.currentUser())
    pfid = dbmain.currentPFID()
    if pfid == None:
        return render_template('errors/no_primary_fair.html', user=dbmain.currentUser())
    if not dbmain.permissionCheck(ObjectId(session['id']), pfid, "can_pair_users"):
        return render_template('errors/no_permissions.html', user=dbmain.currentUser())
    pairings = dbmain.pairingsForFair(pfid)
    return render_template('pair.html', user=dbmain.currentUser(), fair=dbmain.currentFair(), pairings=pairings)

@fair.route('/trainers/')
def trainers():
    if not dbmain.isAdmin():
        return render_template('errors/no_permissions.html', user=dbmain.currentUser())
    pfid = dbmain.currentPFID()
    if pfid == None:
        return render_template('errors/no_primary_fair.html', user=dbmain.currentUser())
    if not dbmain.permissionCheck(ObjectId(session['id']), pfid, "can_pair_trainers"):
        return render_template('errors/no_permissions.html', user=dbmain.currentUser())
    pairings = dbmain.trainersForFair(pfid)
    return render_template('trainers.html', user=dbmain.currentUser(), fair=dbmain.currentFair(), pairings=pairings)

@fair.route('/announcements/')
def announcements():
    if not dbmain.isAdmin():
        return render_template('errors/no_permissions.html', user=dbmain.currentUser())
    pfid = dbmain.currentPFID()
    if pfid == None:
        return render_template('errors/no_primary_fair.html', user=dbmain.currentUser())
    if not dbmain.permissionCheck(ObjectId(session['id']), pfid, "can_post_announcements"):
        return render_template('errors/no_permissions.html', user=dbmain.currentUser())
    announcements = dbmain.announcements(dbmain.currentUser(), pfid)
    return render_template('announcements.html', user=dbmain.currentUser(), fair=dbmain.currentFair(), announcements=announcements)

@fair.route('/permissions/')
def permissions():
    if not dbmain.isAdmin():
        return render_template('errors/no_permissions.html', user=dbmain.currentUser())
    pfid = dbmain.currentPFID()
    if pfid == None:
        return render_template('errors/no_primary_fair.html', user=dbmain.currentUser())
    if not dbmain.hasPermission(ObjectId(session['id']), pfid, "is_owner"):
        return render_template('errors/no_permissions.html', user=dbmain.currentUser())
    administrators = dbmain.administrators(dbmain.currentFair()['_id'])
    adminlist = []
    for administrator in administrators:
        administrator['alevel'] = dbmain.accessLevelForUser(administrator['_id'], dbmain.currentPFID())
        adminlist.append(administrator)
    return render_template('permissions.html', user=dbmain.currentUser(), fair=dbmain.currentFair(), admins=adminlist)

@fair.route('/partner/')
def partner():
    if (not dbmain.isStudent()) and (not dbmain.isMentor()):
        return render_template('errors/no_permissions.html', user=dbmain.currentUser())
    pfid = dbmain.currentPFID()
    partners = []
    if dbmain.isStudent():
        partners = dbmain.pairingsForStudent(dbmain.currentUser()['_id'])
    else:
        partners = dbmain.pairingsForMentor(dbmain.currentUser()['_id'])
    primary = dbmain.primaryPartner(dbmain.currentUser()['_id'])
    return render_template('partner.html', user=dbmain.currentUser(), partners=partners, primary=primary)