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
            "from": "GameDetail",
            "localField": "gameId",
            "foreignField": "gameId",
            "as": "details"
        }
    },{
        "$match": {
            "$and": [{

                "date": '2018-02-02',
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
    print(query)
    result = db.Game.aggregate(query)
    print(list(result))
    # db.Result.insert_many(list(result))


