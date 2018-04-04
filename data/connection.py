from pymongo import MongoClient

MONGO_IP    = 'localhost'
MONGO_PORT  = '27017'

def connect_mongo(ip=None, port=None):

    if ip == None:
        ip = MONGO_IP
        port = MONGO_PORT

    client = MongoClient(host=ip, port=port)

    return client




