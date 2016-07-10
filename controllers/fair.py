from flask import Blueprint, render_template, request, session, redirect, url_for
from model import helpers, dbmain

fair = Blueprint('fair', __name__,
                        template_folder='../templates/fair')

@fair.route('/')
def fair_page():
    return redirect(url_for('fair.manage'))

@fair.route('/manage/')
def manage():
    return render_template('manage.html', user=dbmain.currentUser())

@fair.route('/register/')
def register():
    return redirect(url_for('fair.manage'))