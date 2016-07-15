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

