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

def createTask(fair_id, name, value):
    task = {
        "fair": fair_id,
        "name": name,
        "value": value
    }
    return db.tasks.insert_one(task).inserted_id

def removeTask(task_id):
    db.progress.delete_many({"task":task_id})
    result = db.tasks.delete_one({"_id":task_id})
    return (result == 1)

def editTask(task_id, name, value):
    result = db.tasks.update_one({"_id":task_id}, {"$set":{"name":name, "value":value}})
    return (result == 1)

# adjusted tasks for fair, with ObjectIds converted to Strings
def tasksForFair(fair_id):
    tasks = db.tasks.find({"fair":fair_id})
    result = []
    for task in tasks:
        task["_id"] = str(task["_id"])
        task["fair"] = str(task["fair"])
        result.append(task)
    return result

def createProgress(user_id, task_id, points):
    progress = {
        "user": user_id,
        "task": task_id,
        "points": points
    }
    return db.progress.insert_one(progress).inserted_id

def progressExists(user_id, task_id):
    result = db.progress.find({"user":user_id, "task":task_id}).count()
    return result > 0

# generates statuses for all tasks in fair for user
def generateProgressesForUser(user_id, fair_id):
    tasks = db.tasks.find({"fair":fair_id})
    for task in tasks:
        if not progressExists(user_id, task["_id"]):
            createProgress(user_id, task["_id"], None)

def generateProgressesForTask(task_id):
    task = db.tasks.find_one({"_id":task_id})
    users = db.registration.find({"fair":task["fair"]})
    for user in users:
        user = db.users.find_one({"_id":user["user"]})
        if user["acct_type"] == "Mentor":
            if not progressExists(user["_id"], task_id):
                createProgress(user["_id"], task_id, None)

# use this before a user leaves a fair
def deleteProgressesForUserInFair(user_id, fair_id):
    tasks = db.tasks.find({"fair":fair_id})
    for task in tasks:
        db.progress.delete_one({"user":user_id, "task":task_id})
        
def getProgress(user_id, task_id):
    result = db.progress.find({"user":user_id, "task":task_id})
    if result.count() > 0:
        return result[0]
    else:
        prog_id = createProgress(user_id, task_id, None)
        return db.progress.find_one({"_id":prog_id})