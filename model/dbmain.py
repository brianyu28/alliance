import pymongo
from pymongo import MongoClient
from bson import ObjectId
from flask import session
from helpers import *
client = MongoClient('mongodb://allianceweb:crbysj2016!!@ds011765.mlab.com:11765/alliance')
db = client.alliance

# Interactions with the Users collection
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
