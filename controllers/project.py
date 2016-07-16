from flask import Blueprint, render_template, request, session, redirect, url_for
from model import helpers, dbmain, dbproj
from bson import ObjectId
import re

project = Blueprint('project', __name__,
                        template_folder='../templates/project')

@project.before_request
def check():
    if 'id' not in session:
        return redirect(url_for('home.homepage'))
    if dbmain.isMentor() and dbmain.currentPartner() == None:
        return render_template('errors/no_primary_partner.html', user=dbmain.currentUser())

@project.route('/')
def project_page():
    return redirect(url_for('project.edit'))

@project.route('/edit/')
def edit():
    # get the user's project
    project = None
    if dbmain.isStudent():
        project = dbproj.projectForUser(ObjectId(session['id']))
    else:
        project =dbproj.projectForUser(dbmain.currentPartner())
    # fields to show. Each is array of form [Human-Readable Name, Database Field, Rows for Editing]
    fields = []
    fields.append(["Title", "title", 1])
    fields.append(["Question", "question", 2])
    fields.append(["Purpose", "purpose", 2])
    fields.append(["Research Rationale", "rationale", 3])
    return render_template('project.html', user=dbmain.currentUser(), fair=dbmain.currentFair(), fields=fields, project=project)