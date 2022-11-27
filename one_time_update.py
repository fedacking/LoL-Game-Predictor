from plug_mongo import players

players.update({}, {"$set": {"hits": 1, "total": 1}})
