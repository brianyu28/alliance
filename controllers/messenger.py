from flask import Blueprint, render_template, request, session, redirect, url_for
from model import helpers, dbmain, dbproj, dbcomm
from bson import ObjectId
import re

messenger = Blueprint('messenger', __name__,
                        template_folder='../templates/messenger')

@messenger.before_request
def check():
    if 'id' not in session:
        return redirect(url_for('home.homepage'))
    pfid = dbmain.currentPFID()
    if pfid == None:
        return render_template('errors/no_primary_fair.html', user=dbmain.currentUser())

@messenger.route('/')
def message_page():
    user = dbmain.currentUser()
    conversations = dbcomm.conversationsForUser(user['_id'])
    return render_template('messenger/messages.html', user=user, conversations=conversations)
