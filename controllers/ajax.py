from flask import jsonify, Blueprint, render_template, request, session, redirect, url_for
from model import helpers, dbmain, dbproj, dbcomm, dbtasks
from time import time
from bson import ObjectId
import json
import mailer
import threading

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
    # get recipients of message
    members = dbcomm.otherUsersInConversation(ObjectId(author_id), dbcomm.conversationByID(ObjectId(conversation_id)))
    # send message
    t = threading.Thread(target=mailer.send_new_message_mail, args=[members, dbmain.currentUser(), message])
    t.setDaemon(False)
    t.start()
    return jsonify(result="Success")

@ajax.route('/get_conversations/', methods=['POST'])
def get_conversations():
    user_id = ObjectId(session['id'])
    conversations = dbcomm.conversationsForUser(user_id)
    return jsonify(conversations=conversations)

@ajax.route('/get_watched_conversations/', methods=['POST'])
def get_watched_conversations():
    user_id = ObjectId(session['id'])
    conversations = dbcomm.watchedConversationsForUser(user_id)
    return jsonify(conversations=conversations)

@ajax.route('/new_conversation/', methods=['POST'])
def new_conversation():
    members = []
    requested_members = json.loads(request.form['members'])
    if len(requested_members) == 0:
        return jsonify(result=0)
    for member in requested_members:
        members.append(ObjectId(member))
    members.append(ObjectId(session['id']))
    if dbcomm.conversationExists(members):
        return jsonify(result=-1)
    else:
        inserted_id = str(dbcomm.addConversation(members))
        return jsonify(result=1, convo_id=inserted_id)
    
@ajax.route('/submit_for_approval/', methods=['POST'])
def submit_for_approval():
    author_id = ObjectId(request.form['author_id'])
    fair_id = ObjectId(request.form['fair_id'])
    dbproj.changeApprovalStatus(author_id, fair_id, -1)
    return jsonify(result="Success")

@ajax.route('/change_approval_status/', methods=['POST'])
def change_approval_status():
    author_id = ObjectId(request.form['author_id'])
    fair_id = ObjectId(request.form['fair_id'])
    new_status = request.form['new_status']
    dbproj.changeApprovalStatus(author_id, fair_id, new_status)
    return jsonify(result="Success")

@ajax.route('/add_task/', methods=['POST'])
def add_task():
    name = request.form['name']
    value = request.form['value']
    fair_id = ObjectId(request.form['fair_id'])
    task_id = dbtasks.createTask(fair_id, name, value)
    dbtasks.generateProgressesForTask(task_id)
    return jsonify(result="Success")

@ajax.route('/get_tasks/', methods=['POST'])
def get_tasks():
    fair_id = ObjectId(request.form['fair_id'])
    tasks = dbtasks.tasksForFair(fair_id)
    return jsonify(tasks=tasks)

@ajax.route('/edit_task/', methods=['POST'])
def edit_task():
    name = request.form['name']
    value = request.form['value']
    task_id = ObjectId(request.form['task_id'])
    dbtasks.editTask(task_id, name, value)
    return jsonify(result="Success")

@ajax.route('/delete_task/', methods=['POST'])
def delete_task():
    task_id = ObjectId(request.form['task_id'])
    dbtasks.removeTask(task_id)
    return jsonify(result="Success")

@ajax.route('/update_progress/', methods=['POST'])
def update_progress():
    user_id = ObjectId(request.form['user_id'])
    task_id = ObjectId(request.form['task_id'])
    points = request.form['points']
    none = request.form['none'] == "true"
    dbtasks.updateProgress(user_id, task_id, None if none else points)
    return jsonify(result="Success")

@ajax.route('/change_password/', methods=['POST'])
def change_password():
    user = dbmain.currentUser()
    old_pass = request.form['old_pass']
    new_pass = request.form['new_pass']
    confirm_new_pass = request.form['confirm_new_pass']
    password = user['password']
    if not helpers.check_password(old_pass, password):
        return jsonify(success=False, reason="Password was incorrect.")
    if new_pass != confirm_new_pass:
        return jsonify(success=False, reason="Passwords did not match.")
    dbmain.changePassword(user['_id'], new_pass)
    return jsonify(success=True)

@ajax.route('/change_email/', methods=['POST'])
def change_email():
    user = dbmain.currentUser()
    email = request.form['email']
    dbmain.changeUserAttribute(user['_id'], "email", email)
    return jsonify(success=True)

@ajax.route('/add_contact_email/', methods=['POST'])
def add_contact_email():
    user = dbmain.currentUser()
    email = request.form['email']
    dbmain.addContactEmail(user['_id'], email)
    return jsonify(success=True)

@ajax.route('/delete_contact_email/', methods=['POST'])
def delete_contact_email():
    user = dbmain.currentUser()
    email = request.form['email']
    dbmain.deleteContactEmail(user['_id'], email)
    return jsonify(success=True)


            