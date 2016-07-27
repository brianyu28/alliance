import pymongo
from datetime import datetime
from pytz import timezone
from pymongo import MongoClient
from bson import ObjectId
from flask import session
from helpers import *
client = MongoClient('mongodb://allianceweb:crbysj2016!!@ds011765.mlab.com:11765/alliance')
db = client.alliance

# database queries for handling fair-level action

def addUser(username, hashed_pass, first, last, email, acct_type, school, timezone):
    users = db.users
    user = {
        "username": username,
        "password": hashed_pass,
        "first": first,
        "last": last,
        "email": email,
        "acct_type": acct_type,
        "school": school,
        "timezone": timezone,
        "primary": None,
        "primary_partner": None
    }
    user_id = users.insert_one(user).inserted_id
    return user_id

# gets the user by their ID
def user(id):
    return db.users.find_one({"_id" : ObjectId(id)})

def userById(id):
    return db.users.find_one({"_id":id})

def userExists(user_id):
    return db.users.find({"_id":user_id}).count() > 0

def userByUsername(username):
    return db.users.find_one({"username" : username})

# gets the user by username, or None if there is none
def userIfExists(username):
    query = db.users.find({"username":username})
    return query[0] if query.count() == 1 else None

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

def currentPartner():
    partner = currentUser()['primary_partner']
    if db.pairings.find({"student":ObjectId(session['id']), "mentor":partner}).count() > 0:
        return partner
    elif db.pairings.find({"mentor":ObjectId(session['id']), "student":partner}).count() > 0:
        return partner
    else:
        return None

def isAdmin():
    return (currentUser()['acct_type'] == "Administrator")

def isStudent():
    return (currentUser()['acct_type'] == "Student")

def isMentor():
    return (currentUser()['acct_type'] == "Mentor")

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
    if (db.pairings.find({"student":user, "mentor":partner}).count() > 0) or (db.pairings.find({"mentor":user, "student":partner}).count() > 0):
        return partner
    else:
        return None

def hasPrimaryPartner(user):
    return (primaryPartner(user) != None)

def addRegistration(user, fair, approved):
    registration = db.registration
    reg = {
        "user" : user,
        "fair" : fair,
        "approved" : True if approved else False,
        "title" : None,
        "proj_approved" : 0
    }
    reg_id = registration.insert_one(reg).inserted_id
    return reg_id

def removeRegistration(user, fair):
    db.pairings.delete_many({"student":user})
    db.pairings.delete_many({"mentor":user})
    db.trainings.delete_many({"mentor":user})
    db.trainings.delete_many({"trainer":user})
    result = db.registration.delete_one({"user":user, "fair":fair})
    return (result == 1)

# determines if registration exists
def userIsRegisteredForFair(user, fair):
    return db.registration.find({"user":user, "fair":fair}).count() == 1

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

def clearPermissions(user, fair):
    db.registration.update({"user":user, "fair":fair}, {"$set" : {"permissions":[]}})

def permissionsForUser(user, fair):
    reg = db.registration.find_one({"user":user, "fair":fair})
    if "permissions" not in reg:
        return []
    else:
        return reg["permissions"]

def accessLevelForUser(user_id, fair_id):
    permissions = permissionsForUser(user_id, fair_id)
    if "is_owner" in permissions:
        return "Owner"
    elif "full_access" in permissions:
        return "Full Access"
    elif permissions == []:
        return "No Access"
    else:
        return "Partial Access"

def setAccessLevel(user, fair, level):
    if level == "Owner":
        db.registration.update({"user":user, "fair":fair}, {"$set" : {"permissions" : ["is_owner"]}})
    elif level == "Full Access":
        db.registration.update({"user":user, "fair":fair}, {"$set" : {"permissions" : ["full_access"]}})
    elif level == "Partial Access":
        db.registration.update({"user":user, "fair":fair},
                               {"$set" : {"permissions" : ["can_approve_users", "can_pair_users"]}})
    elif level == "No Access":
        db.registration.update({"user":user, "fair":fair}, {"$set" : {"permissions" : []}})

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

# gets mentors of student
def pairingsForStudent(user_id):
    pairings = db.pairings.find({"student":user_id})
    lst = []
    for pairing in pairings:
        lst.append(db.users.find_one({"_id":pairing["mentor"]}))
    return lst

# gets students of mentor
def pairingsForMentor(user_id):
    pairings = db.pairings.find({"mentor":user_id})
    lst = []
    for pairing in pairings:
        lst.append(db.users.find_one({"_id":pairing["student"]}))
    return lst

def assignTrainer(fair, mentor, trainer):
    training = {
        "fair" : fair,
        "mentor" : mentor,
        "trainer" : trainer
    }
    return db.trainings.insert_one(training).inserted_id

# gets list of trainer pairings for the fair
def trainersForFair(fair):
    pairings = db.trainings.find({"fair":fair})
    lst = []
    for pairing in pairings:
        lst.append({"_id":pairing["_id"], "mentor":db.users.find_one({"_id":pairing["mentor"]}), "trainer":db.users.find_one({"_id":pairing["trainer"]})})
    return lst

def mentorsNeedingTrainers(fair, repeats):
    repeats = (repeats == 'true')
    regs = db.registration.find({"fair":fair, "approved":True})
    lst = []
    for reg in regs:
        user = db.users.find_one({"_id":reg['user']})
        if user['acct_type'] == "Mentor":
            if repeats or (db.trainings.find({"fair":fair, "mentor":reg['user']}).count() == 0):
                lst.append(user)
    return sorted(lst, key=lambda k: k['last'])

# gets a list of of administrators for fair
def administrators(fair):
    regs = db.registration.find({"fair":fair, "approved":True})
    lst = []
    for reg in regs:
        user = db.users.find_one({"_id":reg["user"]})
        if user['acct_type'] == "Administrator":
            lst.append(user)
    return sorted(lst, key=lambda k:k['last'])

def trainingExists(fair, mentor, trainer):
    return (db.pairings.find({"fair":fair, "mentor":mentor, "trainer":trainer}).count() > 0)

def deleteTrainingByID(id):
    return db.trainings.delete_one({"_id":id})

def addAnnouncement(fair, author, datetime, title, contents):
    announcement = {
        "fair": fair,
        "author": author,
        "datetime": datetime,
        "title": title,
        "contents": contents
    }
    return db.announcements.insert_one(announcement).inserted_id

def deleteAnnouncementByID(id):
    return db.announcements.delete_one({"_id":id})

# gets time zone for user
def tzForUser(id):
    return db.users.find_one({"_id":id})['timezone']

# gets announcements for fair, user is only for timezone purposes
def announcements(user, fair):
    announces = db.announcements.find({"fair":fair})
    result = []
    for announce in announces:
        announce["_id"] = str(announce["_id"])
        announce["datetime"] = datetime.fromtimestamp(announce['datetime'], timezone(tzForUser(user['_id']))).strftime("%m/%d/%Y %I:%M:%S %p")
        result.append(announce)
    return result

# gets a comma-separated list of partners
def partners(user_id, fair_id):
    partner_names = []
    user = db.users.find_one({"_id":user_id})
    if user["acct_type"] == "Student":
        partnerships = db.pairings.find({"fair":fair_id, "student":user["_id"]})
        for partnership in partnerships:
            partner = db.users.find_one({"_id":partnership["mentor"]})
            partner_names.append(partner["first"] + " " + partner["last"])
    elif user["acct_type"] == "Mentor":
        partnerships = db.pairings.find({"fair":fair_id, "mentor":user["_id"]})
        for partnership in partnerships:
            partner = db.users.find_one({"_id":partnership["student"]})
            partner_names.append(partner["first"] + " " + partner["last"])
    return ", ".join(partner_names) if len(partner_names) > 0 else "None"

# gets a comma-separated list of trainers
def trainers(user_id, fair_id):
    trainer_names = []
    user = db.users.find_one({"_id":user_id})
    if user["acct_type"] == "Mentor":
        trainings = db.trainings.find({"fair":fair_id, "mentor":user_id})
        for training in trainings:
            trainer = db.users.find_one({"_id":training["trainer"]})
            trainer_names.append(trainer["first"] + " " + trainer["last"])
    return ", ".join(trainer_names) if len(trainer_names) > 0 else "None"
