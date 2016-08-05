from flask import Blueprint, render_template, request, session, redirect, url_for
from model import helpers, dbmain, dbproj, dbtasks, dbcomm
from bson import ObjectId
import re

settings = Blueprint('settings', __name__,
                        template_folder='../templates/settings')

@settings.before_request
def check():
    if 'id' not in session:
        return redirect(url_for('home.homepage'))

@settings.route('/')
def settings_page():
    user = dbmain.currentUser()
    return render_template('settings.html', user=user)