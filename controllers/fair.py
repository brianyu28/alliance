from flask import Blueprint, render_template, request, session, redirect, url_for
from model import helpers, dbmain
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
        r = re.compile('\d{1,2}/\d{1,2}/\d{2,4}')
        if r.match(date) is None:
            error = "You did not specify a valid date."
        else:
            dbmain.addFair(name, date, location, private)
    return render_template('manage.html', user=dbmain.currentUser(), error=error)