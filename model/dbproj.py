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

# sets up an empty project for user, if it doesn't already exist
def createProjectForUser(user_id):
    query = db.projects.find({"user":user_id})
    # only create a project if one doesn't exist
    if (query.count() == 0):
        project = {
            "user" : user_id,
            "title" : "",
            "question" : "",
            "purpose" : "",
            "rationale" : "",
            "hypothesis" : "",
            "nullhypo" : "",
            "ivar" : "",
            "dvar" : "",
            "cvars" : "",
            "control" : "",
            "background" : "",
            "materials" : "",
            "procedure" : "",
            "data" : "",
            "discussion" : "",
            "conclusion" : "",
            "acknowledgements" : "",
            "notes" : ""
        }
        return db.projects.insert_one(project).inserted_id
    else:
        return False
    
def projectForUser(user_id):
    return db.projects.find_one({"user":user_id})

def editProject(project_id, field, value):
    project = db.projects.update_one({"_id" : project_id}, {"$set": {field : value}})
    return True

def projectField(project_id, field):
    project = db.projects.find_one({"_id" : project_id})
    return project[field]

def projectOwner(project_id):
    return db.users.find_one({"_id":db.projects.find_one({"_id":project_id})["user"]})

def roster(fair_id):
    regs = db.registration.find({"fair":fair_id, "approved":True})
    students = []
    mentors = []
    for reg in regs:
        user = db.users.find_one({"_id":reg["user"]})
        user["partner_list"] = dbmain.partners(user["_id"], fair_id)
        if user["acct_type"] == "Student":
            students.append(user)
        elif user["acct_type"] == "Mentor":
            mentors.append(user)
    return {"students":students, "mentors":mentors}

# roster, but includes administrators too
def fullRoster(fair_id, current_user):
    regs = db.registration.find({"fair":fair_id, "approved":True})
    students = []
    mentors = []
    admins = []
    for reg in regs:
        if current_user != reg["user"]:
            user = db.users.find_one({"_id":reg["user"]})
            if user["acct_type"] == "Student":
                students.append(user)
            elif user["acct_type"] == "Mentor":
                mentors.append(user)
            elif user["acct_type"] == "Administrator":
                admins.append(user)
    return {"students":students, "mentors":mentors, "admins":admins}