from flask import Blueprint, render_template, request, session, redirect, url_for
from model import helpers, dbmain

portal = Blueprint('portal', __name__,
                        template_folder='../templates/portal')

@portal.route('/portal/')
def portal_page():
    if 'id' not in session:
        return redirect(url_for('home.homepage')) #possibly change to a must be logged in page
    user = dbmain.currentUser()
    pfid = dbmain.currentPFID()
    announcements = dbmain.announcements(user, pfid)
    return render_template('portal.html', user=user, announcements=announcements)

@portal.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('home.homepage'))
