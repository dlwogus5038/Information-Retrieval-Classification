import pymongo

client = pymongo.MongoClient(host='localhost', port=27017)
db = client.test
collection1 = db.term
collection2 = db.doc

for elem in collection1.find():
    collection1.delete_one(elem)

for elem in collection2.find():
    collection2.delete_one(elem)