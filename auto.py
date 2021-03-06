import pymongo
import json
import datetime
import sys

print(sys.getdefaultencoding())

client = pymongo.MongoClient("112.74.57.41", 27017)
db = client.lotapp

for document in db.Filter.find():
    filter = document
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    query = [{
        "$lookup": {
            "from": "Game",
            "localField": "gameId",
            "foreignField": "gameId",
            "as": "game"
        }
    },{
        "$match": {
            "$and": [{

                "game.date": today,
                "startHost": {
                    "$gte": filter["StartHostFrom"],
                    "$lte": filter["StartHostTo"]
                },
                "startPanko": filter["StartPanko"],
                "startGuest": {
                    "$gte": filter["StartGuestFrom"],
                    "$lte": filter["StartGuestTo"]
                },
                "nowHost": {
                    "$gte": filter["NowHostFrom"],
                    "$lte": filter["NowHostTo"]
                },
                "nowPanko": filter["NowPanko"],
                "nowGuest": {
                    "$gte": filter["NowGuestFrom"],
                    "$lte": filter["NowGuestTo"]
                },
                "euroAsiaHost": {
                    "$gte": filter["EuroAsiaHostFrom"],
                    "$lte": filter["EuroAsiaHostTo"]
                },
                "euroAsiaPanko": filter["EuroAsiaPanko"],
                "euroAsiaGuest": {
                    "$gte": filter["EuroAsiaGuestFrom"],
                    "$lte": filter["EuroAsiaGuestTo"]
                }

            }]
        }
    },
        {
            "$unwind": "$game"
        },
        {
        "$project": {
            "fullname": {
                "$concat": ["$game.type", " ", "$game.date", " ", "$game.time", " ", "$game.host", " VS ", "$game.guest"]
            },
            "_id": 0,
            "company": "$company",
            "startHost": "$startHost",
            "startPanko": "$startPanko",
            "startGuest": "$startGuest",
            "nowHost": "$nowHost",
            "nowPanko": "$nowPanko",
            "nowGuest": "$nowGuest",
            "euroAsiaHost": "$euroAsiaHost",
            "euroAsiaPanko": "$euroAsiaPanko",
            "euroAsiaGuest": "$euroAsiaGuest"
        }
    },
        {
            "$group": {
                "_id": "$fullname",
                "details": {
                    "$push": "$$ROOT"
                }
            }
        }
    ]

    result = db.GameDetail.aggregate(query)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.Result.delete_many({"filterID": filter['_id'], "date": today})
    data = []
    print(filter)
    for item in result:
        print(item)
        data.append(item)
    if(len(data) >0):
        db.Result.insert({"filterID": filter['_id'], "data": data, "date":today, "timestamp": timestamp})

    # print(json.dumps(list(result), indent=4,  ensure_ascii=False))
    # db.Result.insert(result)



