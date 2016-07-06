import pymongo
from pymongo import MongoClient
client = MongoClient('mongodb://allianceweb:crbysj2016!!@ds011765.mlab.com:11765/alliance')
db = client.alliance

# Interactions with the database
def addUser(username, hashed_pass, first, last, email, acct_type, school):
    users = db.users
    user = {
        "username": username,
        "password": hashed_pass,
        "first": first,
        "last": last,
        "email": email,
        "acct_type": acct_type,
        "school": school
    }
    user_id = users.insert_one(user).inserted_id
    return user_id