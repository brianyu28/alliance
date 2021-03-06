import pymongo
from datetime import datetime
from pytz import timezone
from pymongo import MongoClient
from bson import ObjectId
from flask import session
from helpers import *
import dbmain
import secrets
client = MongoClient(secrets.mongo_uri)
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
        user["access_permitted"] = True # might change to False based on permissions later, determines if admin has permissions
        if user["acct_type"] == "Student":
            students.append(user)
        elif user["acct_type"] == "Mentor":
            mentors.append(user)
    return {"students":students, "mentors":mentors}

# gets the roster, but includes approval information
def rosterForApprovals(fair_id):
    regs = db.registration.find({"fair":fair_id, "approved":True})
    students = {"-2":[], "-1":[], "0":[], "1":[]}
    for reg in regs:
        user = db.users.find_one({"_id":reg["user"]})
        if user["acct_type"] == "Student":
            user["title"] = projectForUser(user["_id"])["title"]
            if user["title"] == "":
                user["title"] = "Untitled"
            user["proj_approved"] = reg["proj_approved"]
            user["partner_list"] = dbmain.partners(user["_id"], fair_id)
            students[str(int(reg["proj_approved"]))].append(user)
    return students
        
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

# approval status
# rules for approval statuses: 0 = not submitted, -1 = submitted, awaiting approval, -2 = rejected, 1 = approved
def approvalStatus(user_id, fair_id):
    reg = db.registration.find_one({"user":user_id, "fair":fair_id})
    return reg["proj_approved"]

def changeApprovalStatus(user_id, fair_id, new_status):
    db.registration.update_one({"user":user_id, "fair":fair_id}, {"$set":{"proj_approved":new_status}})
    
def approvalStatusString(approval_status):
    approval_status = int(approval_status)
    if approval_status == 0:
        return "Not Submitted"
    elif approval_status == 1:
        return "Approved"
    elif approval_status == -1:
        return "Awaiting Approval"
    elif approval_status == -2:
        return "Rejected"
    else:
        return "Unknown"