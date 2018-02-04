import pymongo
import json
import datetime

client = pymongo.MongoClient("localhost", 27017)
db = client.lotapp

for document in db.Filter.find():
    filter = document

today = datetime.datetime.now().strftime("%Y-%m-%d")

query = [{
    "$lookup": {
        "from": "asias",
        "localField": "id",
        "foreignField": "gameId",
        "as": "details"
    }
}, {
    "$unwind": "$details"
}, {
    "$match": {
        "$and": [{

            "date": today,
            "details.startHost": {
                "$gte": filter["startHostFrom"],
                "$lte": filter["startHostTo"]
            },
            "details.startPanko": filter["startPanko"],
            "details.startGuest": {
                "$gte": filter["startGuestFrom"],
                "$lte": filter["startGuestTo"]
            },
            "details.endHost": {
                "$gte": filter["endHostFrom"],
                "$lte": filter["endHostTo"]
            },
            "details.endPanko": filter["endPanko"],
            "details.endGuest": {
                "$gte": filter["endGuestFrom"],
                "$lte": filter["endGuestTo"]
            },
            "details.nowHost": {
                "$gte": filter["nowHostFrom"],
                "$lte": filter["nowHostTo"]
            },
            "details.nowPanko": filter["nowPanko"],
            "details.nowGuest": {
                "$gte": filter["nowGuestFrom"],
                "$lte": filter["nowGuestTo"]
            },
            "details.euroAsiaHost": {
                "$gte": filter["euroAsiaHostFrom"],
                "$lte": filter["euroAsiaHostTo"]
            },
            "details.euroAsiaPanko": filter["euroAsiaPanko"],
            "details.euroAsiaGuest": {
                "$gte": filter["euroAsiaGuestFrom"],
                "$lte": filter["euroAsiaGuestTo"]
            }

        }]
    }
},
    {
        "$group": {
            "_id": {
                "game": {
                    "$concat": ["$type", " ", "$date", " ", "$time", " ", "$host", " VS ", "$guest"]
                },
                "company": "$details.company"
            },
            "details": {
                "$push": "$$ROOT"
            }
        }
    },
    {
        "$group": {
            "_id": "$_id.game",
            "data": {
                "$push": {
                    "company":"$_id.company",
                    "details": "$details"
                }
            }
        }
    },
    {
        "$project": {
            "_id": 0,
            "game": "$_id",
            "data": 1
        }
    }
]
print(query)
result = db.games.aggregate(query)
for document in result:
    print(document)
    # db.result.insert(document)
