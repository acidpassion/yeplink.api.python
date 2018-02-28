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
            "from": "GameDetail",
            "localField": "gameId",
            "foreignField": "gameId",
            "as": "details"
        }
    },{
        "$match": {
            "$and": [{

                "date": today,
                "details.startHost": {
                    "$gte": filter["StartHostFrom"],
                    "$lte": filter["StartHostTo"]
                },
                "details.startPanko": filter["StartPanko"],
                "details.startGuest": {
                    "$gte": filter["StartGuestFrom"],
                    "$lte": filter["StartGuestTo"]
                },
                "details.endHost": {
                    "$gte": filter["EndHostFrom"],
                    "$lte": filter["EndHostTo"]
                },
                "details.endPanko": filter["EndPanko"],
                "details.endGuest": {
                    "$gte": filter["EndGuestFrom"],
                    "$lte": filter["EndGuestTo"]
                },
                "details.nowHost": {
                    "$gte": filter["NowHostFrom"],
                    "$lte": filter["NowHostTo"]
                },
                "details.nowPanko": filter["NowPanko"],
                "details.nowGuest": {
                    "$gte": filter["NowGuestFrom"],
                    "$lte": filter["NowGuestTo"]
                },
                "details.euroAsiaHost": {
                    "$gte": filter["EuroAsiaHostFrom"],
                    "$lte": filter["EuroAsiaHostTo"]
                },
                "details.euroAsiaPanko": filter["EuroAsiaPanko"],
                "details.euroAsiaGuest": {
                    "$gte": filter["EuroAsiaGuestFrom"],
                    "$lte": filter["EuroAsiaGuestTo"]
                }

            }]
        }
    },
        {
            "$unwind": "$details"
        },
        {
        "$project": {
            "fullname": {
                "$concat": ["$type", " ", "$date", " ", "$time", " ", "$host", " VS ", "$guest"]
            },
            "_id": 0,
            "company": "$details.company",
            "startHost": "$details.startHost",
            "startPanko": "$details.startPanko",
            "startGuest": "$details.startGuest",
            "nowHost": "$details.nowHost",
            "nowPanko": "$details.nowPanko",
            "nowGuest": "$details.nowGuest",
            "endHost": "$details.endHost",
            "endPanko": "$details.endPanko",
            "endGuest": "$details.endGuest",
            "euroAsiaHost": "$details.euroAsiaHost",
            "euroAsiaPanko": "$details.euroAsiaPanko",
            "euroAsiaGuest": "$details.euroAsiaGuest"
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

    result = db.Game.aggregate(query)
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



