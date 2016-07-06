from flask import Blueprint, render_template, request, session, redirect, url_for
from model import helpers, dbmain

portal = Blueprint('portal', __name__,
                        template_folder='../templates/portal')

@portal.route('/portal/')
def portal_page():
    return render_template('portal.html')
