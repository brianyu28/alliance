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

@messenger.route('/', defaults={'convo_id':None})
@messenger.route('/<convo_id>/')
def message_page(convo_id):
    user = dbmain.currentUser()
    if convo_id != None:
        if not dbcomm.conversationWithIDExists(ObjectId(convo_id)):
            convo_id = None
        elif not dbcomm.userIsInConversation(ObjectId(session['id']), ObjectId(convo_id)) and not dbcomm.userWatchesConversation(ObjectId(session['id']), ObjectId(convo_id)):
            convo_id = None
    conversers = dbcomm.availableConversers(ObjectId(session['id']))
    return render_template('messenger/messages.html', conversers=conversers, user=user, selected=convo_id)
