from flask import jsonify, Blueprint, render_template, request, session, redirect, url_for
from model import helpers, dbmain
from bson import ObjectId

ajax = Blueprint('ajax', __name__,
                        template_folder='../templates/ajax')

@ajax.route('/fair_details/', methods=['GET', 'POST'])
def fair_details():
    if request.method == 'GET':
        return jsonify(result="Failed. Data must be submitted via POST request.")
    elif request.method == 'POST':
        fair = dbmain.fair(request.form['id'])
        return jsonify(name=fair['name'], location=fair['location'], date=fair['date'], id=str(fair['_id']), private=fair['private'])