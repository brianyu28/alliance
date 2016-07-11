from flask import Blueprint, render_template, request, session, redirect, url_for
from model import helpers, dbmain
from bson import ObjectId
import re

fair = Blueprint('fair', __name__,
                        template_folder='../templates/fair')

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
            dbmain.changePrimaryFair(ObjectId(session['id']), fair_id)
    # get a list of fairs that the user is registered for
    registration = dbmain.fairsForUser(ObjectId(session['id']))
    return render_template('manage.html', user=dbmain.currentUser(), registration=registration, error=error)