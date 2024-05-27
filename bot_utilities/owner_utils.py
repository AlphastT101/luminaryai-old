async def insertdb(dbname, id ,mongodb):

    if dbname == 'blist-servers':
        db = mongodb["blacklisted"]
        collection = db['servers']

        doc = {
            "server_id": id
        }
        result = collection.find_one({"server_id": int(id)})

        if result:
            return "already blacklisted"
        else:
            collection.insert_one(doc)
            return "blacklisted"
        
    if dbname == 'blist-users':
        db = mongodb["blacklisted"]
        collection = db['users']

        doc ={
            "user_id": id
        }
        result = collection.find_one({"userid_id": int(id)})

        if result:
            return "already blacklisted"
        else:
            collection.insert_one(doc)
            return "blacklisted"


async def getdb(dbname, id, mongodb):

    if dbname == 'blist-servers':
        db = mongodb["blacklisted"]
        collection = db['servers']
        result = collection.find_one({"server_id": int(id)})
        if result:
            return "blacklisted"
        else:
            return "not blacklisted"
        
    if dbname == 'blist-users':
        db = mongodb["blacklisted"]
        collection = db['users']

        result = collection.find_one({"user_id": int(id)})
        if result:
            return "blacklisted"
        else:
            return "not blacklisted"

async def deletedb(dbname, id, mongodb):

    if dbname == 'blist-servers':
        db = mongodb['blacklisted']
        collection = db['servers']

        result = collection.find_one({"server_id": int(id)})
        if result:
            collection.delete_one({"server_id": int(id)})
            return "unblacklisted"
        else:
            return "not blacklisted"
        
    if dbname == 'blist-users':
        db = mongodb['blacklisted']
        collection = db['users']

        result = collection.find_one({"user_id": int(id)})
        if result:
            collection.delete_one({"user_id": int(id)})
            return "unblacklisted"
        else:
            return "not blacklisted"