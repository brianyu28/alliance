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
    if request.method == 'POST' and request.form['type'] == 'Register':
        name = request.form['name']
        date = request.form['date']
        location = request.form['location']
        private = 'private' in request.form
        # this is supposed to work but doesn't yet
        r = re.compile('\d/\d/\d{4}')
        if r.match(date) is None:
            print 'There is an error'
    return render_template('manage.html', user=dbmain.currentUser())