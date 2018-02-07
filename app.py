#!flask/bin/python
from flask import Flask, request, render_template
from pymongo import MongoClient
from flask_cors import CORS
import json
import datetime
from bson import json_util, ObjectId
import bson
from bson.codec_options import CodecOptions
import collections

application = Flask(__name__)
CORS(application)
client=MongoClient("localhost", 27017)
db=client.lotapp



@application.route('/test', methods=['GET','POST'])
def test():
    return 'api is running'


@application.route('/games', methods=['GET','POST'])
def get_games():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    filter = request.json
    pinelines = [
        {
            "$lookup": {
                "from": "GameDetail",
                "localField": "gameId",
                "foreignField": "gameId",
                "as": "details"
            }
         },

        {
            "$match": {
                "$and": [{

                    "date": "2018-02-02",
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
    result = list(db.Game.aggregate(pinelines))

    return json.dumps(result, indent =4)

if __name__ == '__main__':
    application.run()