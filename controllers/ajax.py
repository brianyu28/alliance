from flask import jsonify, Blueprint, render_template, request, session, redirect, url_for
from model import helpers, dbmain, dbproj, dbcomm
from time import time
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

@ajax.route('/students_to_pair/', methods=['POST'])
def students_to_pair():
    students = dbmain.studentsToPair(ObjectId(request.form['fair']), request.form['repeats'])
    result = []
    for student in students:
        result.append({"id":str(student['_id']), "first":student['first'], "last":student['last']})
    return jsonify(result)

@ajax.route('/mentors_to_pair/', methods=['POST'])
def mentors_to_pair():
    mentors = dbmain.mentorsToPair(ObjectId(request.form['fair']), request.form['repeats'])
    result = []
    for mentor in mentors:
        result.append({"id":str(mentor['_id']), "first":mentor['first'], "last":mentor['last']})
    return jsonify(result)

@ajax.route('/pair/', methods=['POST'])
def pair():
    if not dbmain.pairingExists(ObjectId(request.form['fair']), ObjectId(request.form['student']), ObjectId(request.form['mentor'])):
        dbmain.addPairing(ObjectId(request.form['fair']), ObjectId(request.form['student']), ObjectId(request.form['mentor']))
        if not dbmain.hasPrimaryPartner(ObjectId(request.form['student'])):
            dbmain.changePrimaryPartner(ObjectId(request.form['student']), ObjectId(request.form['mentor']))
        if not dbmain.hasPrimaryPartner(ObjectId(request.form['mentor'])):
            dbmain.changePrimaryPartner(ObjectId(request.form['mentor']), ObjectId(request.form['student']))
        # create a conversation between the two partners if it does not exist yet
        dbcomm.addConversation([ObjectId(request.form['student']), ObjectId(request.form['mentor'])])
    return jsonify(result="Success")

@ajax.route('/remove_pairing/', methods=['POST'])
def remove_pairing():
    dbmain.deletePairingByID(ObjectId(request.form['id']))
    return jsonify(result="Success")

@ajax.route('/mentors_needing_trainers/', methods=['POST'])
def mentors_needing_trainers():
    mentors = dbmain.mentorsNeedingTrainers(ObjectId(request.form['fair']), request.form['repeats'])
    result = []
    for mentor in mentors:
        result.append({"id":str(mentor['_id']), "first":mentor['first'], "last":mentor['last']})
    return jsonify(result)

@ajax.route('/fair_administrators/', methods=['POST'])
def fair_administrators():
    administrators = dbmain.administrators(ObjectId(request.form['fair']))
    result = []
    for admin in administrators:
        result.append({"id":str(admin["_id"]), "first":admin["first"], "last":admin["last"]})
    return jsonify(result)

@ajax.route('/pair_trainer/', methods=['POST'])
def pair_trainer():
    if not dbmain.trainingExists(ObjectId(request.form['fair']), ObjectId(request.form['mentor']), ObjectId(request.form['trainer'])):
        dbmain.assignTrainer(ObjectId(request.form['fair']), ObjectId(request.form['mentor']), ObjectId(request.form['trainer']))
    dbcomm.addConversation([ObjectId(request.form['mentor']), ObjectId(request.form['trainer'])])
    return jsonify(result="Success")

@ajax.route('/remove_training/', methods=['POST'])
def remove_training():
    dbmain.deleteTrainingByID(ObjectId(request.form['id']))
    return jsonify(result="Success")

@ajax.route('/post_announcement/', methods=['POST'])
def post_announcement():
    dbmain.addAnnouncement(ObjectId(request.form['fair']), ObjectId(request.form['author']), time(), request.form['title'], request.form['contents'])
    return jsonify(result="Success")

@ajax.route('/remove_announcement/', methods=['POST'])
def remove_announcement():
    dbmain.deleteAnnouncementByID(ObjectId(request.form['id']))
    return jsonify(result="Success")

@ajax.route('/update_permissions/', methods=['POST'])
def update_permissions():
    dbmain.setAccessLevel(ObjectId(request.form['user']), ObjectId(request.form['fair']), request.form['level'])
    return jsonify(result="Success")

@ajax.route('/make_primary_partner/', methods=['POST'])
def make_primary_partner():
    dbmain.changePrimaryPartner(ObjectId(session['id']), ObjectId(request.form['id']))
    return jsonify(result="Success")

@ajax.route('/update_project/', methods=['POST'])
def update_project():
    dbproj.editProject(ObjectId(request.form['project_id']), request.form['field'], request.form['value'])
    return jsonify(result="Success")

@ajax.route('/project_field/', methods=['POST'])
def project_field():
    result = dbproj.projectField(ObjectId(request.form['project_id']), request.form['field'])
    return jsonify(result=result)

@ajax.route('/messages_in_conversation/', methods=['POST'])
def messages_in_conversation():
    conversation_id = request.form['conversation_id']
    messages = dbcomm.messagesInConversation(ObjectId(conversation_id))
    members = dbcomm.convoMembers(ObjectId(session['id']), dbcomm.conversationByID(ObjectId(conversation_id)), True)
    return jsonify(messages=messages, members=members)

@ajax.route('/send_message/', methods=['POST'])
def send_message():
    conversation_id = request.form['conversation_id']
    author_id = session['id']
    timestamp = time()
    subject = request.form['subject']
    message = request.form['message']
    dbcomm.addMessage(ObjectId(conversation_id), ObjectId(author_id), timestamp, subject, message)
    return jsonify(result="Success")
