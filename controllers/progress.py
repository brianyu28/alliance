from flask import Blueprint, render_template, request, session, redirect, url_for
from model import helpers, dbmain, dbproj, dbtasks
from bson import ObjectId
import re

progress = Blueprint('progress', __name__,
                        template_folder='../templates/progress')

@progress.before_request
def check():
    if 'id' not in session:
        return redirect(url_for('home.homepage'))
    if not dbmain.isMentor():
        return render_template('errors/no_permissions.html', user=dbmain.currentUser())
    if dbmain.currentPFID() == None:
        return render_template('errors/no_primary_fair.html', user=dbmain.currentUser())
    
@progress.route('/')
def mentor_progress():
    fair = dbmain.currentFair()
    progresses = dbtasks.getProgressesForUser(ObjectId(session['id']), fair["_id"])
    return render_template('mentor_progress.html', user=dbmain.currentUser(), fair=fair, progresses=progresses)