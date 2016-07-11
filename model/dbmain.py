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
        "approved" : approved,
        "permissions" : ["is_owner"]
    }
    reg_id = registration.insert_one(reg).inserted_id
    return reg_id

def fairsForUser(user):
    registration = db.registration
    fairs = db.fairs
    regs = registration.find({"user" : user})
    fair_list = []
    for reg in regs:
        fair_list.append(fairs.find_one({"_id" : reg["fair"]}))
    return fair_list