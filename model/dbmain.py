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
        "primary_partner": None
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

# returns current primary fair ID
def currentPFID():
    pfid = currentUser()['primary']
    if db.registration.find({"user":currentUser()['_id'], "fair":pfid}).count() > 0:
        return pfid
    else:
        return None

def currentFair():
    return db.fairs.find_one({"_id":currentPFID()})

def isAdmin():
    return (currentUser()['acct_type'] == "Administrator")

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

def changePrimaryPartner(user, partner):
    result = db.users.update_one({'_id':user}, {'$set' : {"primary_partner" : partner}})
    return (result == 1)

def primaryPartner(user):
    partner = db.users.find_one({"_id":user})["primary_partner"]
    if db.registration

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

def approveUser(user, fair):
    result = db.registration.update_one({"user":user, "fair":fair}, {"$set": {"approved":True}})
    return (result == 1)

def hasPermission(user, fair, permission):
    reg = db.registration.find_one({"user":user, "fair":fair})
    if "permissions" not in reg:
        return False
    permissions = reg["permissions"]
    return permission in permissions

# checks to see if user is allowed to perform operation:
def permissionCheck(user, fair, permission):
    reg = db.registration.find_one({"user":user, "fair":fair})
    if "permissions" not in reg:
        return False
    permissions = reg["permissions"]
    return (permission in permissions) or ("is_owner" in permissions) or ("full_access" in permissions)

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

def pendingRequestsForFair(fair):
    regs = db.registration.find({"fair":fair, "approved":False})
    lst = []
    for reg in regs:
        lst.append(db.users.find_one({"_id":reg['user']}))
    return lst

def studentsToPair(fair, repeats):
    repeats = (repeats == 'true')
    regs = db.registration.find({"fair":fair, "approved":True})
    lst = []
    for reg in regs:
        user = db.users.find_one({"_id":reg['user']})
        if user['acct_type'] == "Student":
            if repeats or (db.pairings.find({"fair":fair, "student":reg['user']}).count() == 0):
                lst.append(user)
    return sorted(lst, key=lambda k: k['last'])

def mentorsToPair(fair, repeats):
    repeats = (repeats == 'true')
    regs = db.registration.find({"fair":fair, "approved":True})
    lst = []
    for reg in regs:
        user = db.users.find_one({"_id":reg['user']})
        if user['acct_type'] == "Mentor":
            if repeats or (db.pairings.find({"fair":fair, "mentor":reg['user']}).count() == 0):
                lst.append(user)
    return sorted(lst, key=lambda k: k['last'])

def addPairing(fair, student, mentor):
    pairing = {
        "fair" : fair,
        "student" : student,
        "mentor" : mentor
    }
    return db.pairings.insert_one(pairing).inserted_id

def deletePairing(fair, student, mentor):
    return db.pairings.delete_one({"fair":fair, "student":student, "mentor":mentor})

def deletePairingByID(id):
    return db.pairings.delete_one({"_id":id})

def pairingExists(fair, student, mentor):
    return (db.pairings.find({"fair":fair, "student":student, "mentor":mentor}).count() > 0)

def pairingsForFair(fair):
    pairings = db.pairings.find({"fair":fair})
    lst = []
    for pairing in pairings:
        lst.append({"_id":pairing["_id"], "student":db.users.find_one({"_id":pairing["student"]}), "mentor":db.users.find_one({"_id":pairing["mentor"]})})
    return lst

