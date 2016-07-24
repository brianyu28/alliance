import pymongo
from datetime import datetime
from pytz import timezone
from pymongo import MongoClient
from bson import ObjectId
from flask import session
from helpers import *
import dbmain, dbproj
client = MongoClient('mongodb://allianceweb:crbysj2016!!@ds011765.mlab.com:11765/alliance')
db = client.alliance

def conversationExists(members):
    members.sort()
    return db.conversations.find({"members":members}).count() > 0

def conversationWithIDExists(convo_id):
    return db.conversations.find({"_id":convo_id}).count() > 0

def userIsInConversation(user_id, convo_id):
    conversation = db.conversations.find_one({"_id":convo_id})
    return user_id in conversation["members"]

def addConversation(members):
    members.sort()
    if conversationExists(members):
        return None
    conversation = {
        "members": members,
        "last_message": None # keeps track of most recent message sent
    }
    return db.conversations.insert_one(conversation).inserted_id

def addMessage(conversation_id, author_id, timestamp, subject, body):
    message = {
        "conversation" : conversation_id,
        "author" : author_id,
        "timestamp" : timestamp,
        "subject" : subject,
        "body" : body
    }
    inserted_id = db.messages.insert_one(message).inserted_id
    db.conversations.update_one({"_id":conversation_id}, {"$set":{"last_message":inserted_id}})
    return inserted_id

def messagesInConversation(conversation_id):
    messages = db.messages.find({"conversation":conversation_id}).sort("timestamp", -1)
    result = []
    for message in messages:
        message["_id"] = str(message["_id"])
        message["timestamp"] = datetime.fromtimestamp(message['timestamp'], timezone(dbmain.tzForUser(ObjectId(session['id'])))).strftime("%m/%d/%Y %I:%M:%S %p")
        author = db.users.find_one({"_id":message["author"]})
        message["author"] = author["first"] + " " + author["last"]
        message["conversation"] = str(message["conversation"])
        result.append(message)
    return result

def conversationsForUser(user_id):
    convos = db.conversations.find({"members":user_id})
    result = []
    for convo in convos:
        convo["_id"] = str(convo["_id"])
        convo["name"] = convoName(user_id, convo)
        convo["members"] = ""
        last_message = db.messages.find_one({"_id":convo["last_message"]}) if convo["last_message"] != None else None
        convo["last_message"] = last_message["body"] if last_message != None else ""
        convo["last_update"] = last_message["timestamp"] if last_message != None else 0
        convo["timestamp"] = datetime.fromtimestamp(last_message['timestamp'], timezone(dbmain.tzForUser(ObjectId(session['id'])))).strftime("%m/%d %I:%M %p") if last_message != None else ""
        result.append(convo)
    result = sorted(result, key=lambda k: k["last_update"], reverse=True)
    return result

# gets a name for the conversation by taking names of participants, excluding current user
def convoName(user_id, conversation):
    members = conversation['members']
    participants = []
    # iterate through members, take names of anyone who isn't the current user
    for member in members:
        if member != user_id:
            user = db.users.find_one({"_id":member})
            participants.append(user["first"] + " " + user["last"])
    return ', '.join(participants)

def conversationByID(conversation_id):
    return db.conversations.find_one({"_id":conversation_id})

# gets a list of the conversation members, excluding the current user
def convoMembers(user_id, conversation, show_positions):
    members = conversation['members']
    participants = []
    for member in members:
        if member != user_id:
            user = db.users.find_one({"_id":member})
            if show_positions:
                participants.append(user["first"] + " " + user["last"] + "  (" + user["acct_type"] + ")")
            else:
                participants.append(user["first"] + " " + user["last"])
    return participants

# gets list of people who the user can converse with
# Students can communicate with: their mentor(s), and administrators
# Mentors can communicate with: their student(s), and administrators
# Administrators can communicate with anyone in fair
def availableConversers(user_id):
    user = db.users.find_one({"_id":user_id})
    fairs = dbmain.fairsForUser(user_id)
    conversers = []
    for fair in fairs:
        roster = dbproj.fullRoster(fair["_id"], user_id)
        if user["acct_type"] == "Administrator":
            conversers = roster["students"] + roster["mentors"] + roster["admins"]
        elif user["acct_type"] == "Mentor":
            conversers = dbmain.pairingsForMentor(user_id) + roster["admins"]
        elif user["acct_type"] == "Student":
            conversers = dbmain.pairingsForStudent(user_id) + roster["admins"]
    return conversers
            
