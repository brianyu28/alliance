from flask import jsonify, Blueprint, render_template, request, session, redirect, url_for
from model import helpers, dbmain
from bson import ObjectId

ajax = Blueprint('ajax', __name__,
                        template_folder='../templates/ajax')

@ajax.route('/fair_details/', methods=['POST'])
def fair_details():
    fair = dbmain.fair(request.form['id'])
    return jsonify(name=fair['name'], location=fair['location'], date=fair['date'], id=str(fair['_id']), private=fair['private'])
    
@ajax.route('/fair_update/', methods=['POST'])
def fair_update():
    dbmain.updateFair(ObjectId(request.form['id']), request.form['name'], request.form['date'], request.form['location'], request.form['private'])
    return jsonify(result="Success")

@ajax.route('/make_primary/', methods=['POST'])
def make_primary():
    dbmain.changePrimaryFair(ObjectId(session['id']), ObjectId(request.form['id']))
    return jsonify(result="Success")

@ajax.route('/approve_user/', methods=['POST'])
def approve_user():
    dbmain.approveUser(ObjectId(request.form['user']), ObjectId(request.form['fair']))
    return jsonify(result="Success")

@ajax.route('/reject_user/', methods=['POST'])
def reject_user():
    dbmain.removeRegistration(ObjectId(request.form['user']), ObjectId(request.form['fair']))
    return jsonify(result="Success")

