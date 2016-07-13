from flask import Blueprint, render_template, request, session, redirect, url_for
from model import helpers, dbmain
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
        dbmain.changePrimaryFair(ObjectId(session['id']), ObjectId(request.form['fair']))
    if request.method == 'POST' and request.form['type'] == 'Leave':
        dbmain.removeRegistration(ObjectId(session['id']), ObjectId(request.form['fair']))
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