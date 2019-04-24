from pymongo import MongoClient

def get_db(dbname, port=27017):
    client = MongoClient("localhost", port)
    db = client[dbname]
    return db, client


