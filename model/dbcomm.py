import pymongo
from datetime import datetime
from pytz import timezone
from pymongo import MongoClient
from bson import ObjectId
from flask import session
from helpers import *
import dbmain
client = MongoClient('mongodb://allianceweb:crbysj2016!!@ds011765.mlab.com:11765/alliance')
db = client.alliance

def conversationExists(members):
    members.sort()
    return db.conversations.find({"members":members}).count() > 0

def addConversation(members):
    members.sort()
    if conversationExists(members):
        return None
    conversation = {
        "members": members
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
    return db.mesasges.insert_one(message).inserted_id

def messagesInConversation(conversation_id):
    messages = db.messages.find({"conversation":conversation_id}).sort("timestamp", -1)
    result = []
    for message in messages:
        message["_id"] = str(message["_id"])
        message["datetime"] = datetime.fromtimestamp(message['datetime'], timezone(tzForUser(user['_id']))).strftime("%m/%d/%Y %I:%M:%S %p")
        result.append(announce)
    return result


def conversationsForUser(user_id):
    convos = db.conversations.find({"members":user_id})
    result = []
    for convo in convos:
        convo["name"] = convoName(user_id, convo)
        result.append(convo)
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
