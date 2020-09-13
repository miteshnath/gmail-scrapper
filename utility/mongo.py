from pymongo import MongoClient, errors
from bson.objectid import ObjectId
import os
import sys
import time
import argparse

sys.path.append(os.getcwd())

from config.configurations import MONGO_URI, MONGO_DB
from utility.exceptions import DuplicateDocError


class MongoDb:
    def __init__(self, collection_name):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.collection_name = collection_name
        self.total = self.db.emails.count_documents({})
    
    def insert_one(self, doc):
        try:
            return self.db.emails.insert(doc)
        except errors.DuplicateKeyError as e:
            raise DuplicateDocError(err_msg="duplicate id", logger=self.logger)
        
    def insert_bulk(self, doc_list):
        return self.db.emails.insert_many(doc_list)
    
    def find_one(self, options):
        _options = {}
        for key in options.keys():
            _options[key] = ObjectId(options[key])
        return self.db.emails.find_one(_options)

    def get_last_n(self, count):
        res = []
        mails = self.db.emails.find().skip(self.db.emails.count() - int(count))
        for mail in mails:
            mail['_id'] = str(mail['_id'])
            mail["attachment_data"] = "contains data not showing in this view"
            res.append(mail)
        return res