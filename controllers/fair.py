from flask import Blueprint, render_template, request, session, redirect, url_for
from model import helpers, dbmain

fair = Blueprint('fair', __name__,
                        template_folder='../templates/fair')

@fair.route('/fair/')
def manage():
    return render_template('manage.html', user=dbmain.currentUser())