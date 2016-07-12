import pymongo
from pymongo import MongoClient
from bson import ObjectId
from flask import session
from helpers import *
client = MongoClient('mongodb://allianceweb:crbysj2016!!@ds011765.mlab.com:11765/alliance')
db = client.alliance

def addUser(username, hashed_pass, first, last, email, acct_type, school):
    users = db.users
    user = {
        "username": username,
        "password": hashed_pass,
        "first": first,
        "last": last,
        "email": email,
        "acct_type": acct_type,
        "school": school,
        "primary": None,
    }
    user_id = users.insert_one(user).inserted_id
    return user_id

# gets the user by their ID
def user(id):
    return db.users.find_one({"_id" : ObjectId(id)})

def userByUsername(username):
    return db.users.find_one({"username" : username})

def currentUser():
    return db.users.find_one({"_id" : ObjectId(session["id"])})

def authenticate(username, password):
    user = userByUsername(username)
    if user == None:
        return False
    hashed_pass = user["password"]
    return check_password(password, hashed_pass)

def usernameAvailable(username):
    matches = db.users.find({"username" : username}).count()
    return True if matches == 0 else False

def addFair(name, date, location, private):
    fairs = db.fairs
    fair = {
        "name" : name,
        "date" : date,
        "location" : location,
        "private" : private,
    }
    fair_id = fairs.insert_one(fair).inserted_id
    return fair_id

def fair(id):
    return db.fairs.find_one({"_id" : ObjectId(id)})

def updateFair(id, name, date, location, private):
    result = db.fairs.update_one({'_id' : id}, {'$set' : {
        "name" : name,
        "date" : date,
        "location" : location,
        "private" : private
    }})
    return (result == 1)

def changePrimaryFair(user, fair):
    result = db.users.update_one({'_id' : user}, {'$set' : {"primary" : fair}})
    return (result == 1)

def addRegistration(user, fair, approved):
    registration = db.registration
    reg = {
        "user" : user,
        "fair" : fair,
        "approved" : True if approved else False
    }
    reg_id = registration.insert_one(reg).inserted_id
    return reg_id

def removeRegistration(user, fair):
    result = db.registration.delete_one({"user":user, "fair":fair})
    return (result == 1)

def hasPermission(user, fair, permission):
    reg = db.registration.find_one({"user":user, "fair":fair})
    if "permissions" not in reg:
        return False
    permissions = reg["permissions"]
    return permission in permissions

def addPermission(user, fair, permission):
    if not hasPermission(user, fair, permission):
        db.registration.update({"user":user, "fair":fair}, {"$push" : {"permissions" : permission}})
    return True

def fairsForUser(user):
    registration = db.registration
    fairs = db.fairs
    regs = registration.find({"user" : user})
    fair_list = []
    for reg in regs:
        fair = fairs.find_one({"_id" : reg["fair"]})
        fair['approved'] = reg['approved']
        fair_list.append(fair)
    return fair_list

def unjoinedFairs(user):
    registration = db.registration
    fairs = db.fairs.find()
    unjoined = []
    for fair in fairs:
        if registration.find({"user":user, "fair":fair["_id"]}).count() == 0:
            unjoined.append(fair)
    return unjoined
