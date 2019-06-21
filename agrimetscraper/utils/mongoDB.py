from pymongo import MongoClient

def get_db(dbname, connect_string, port=27017):

    if connect_string != r"localhost":
        client = MongoClient(connect_string)
    else:
        client = MongoClient(connect_string, port)

    db = client[dbname]
    return db, client


