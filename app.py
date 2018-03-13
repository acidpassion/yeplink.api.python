#!flask/bin/python
from flask import Flask, jsonify
from pymongo import MongoClient
from flask_cors import CORS
import json
import datetime
from bson.json_util import dumps, CANONICAL_JSON_OPTIONS
from bson.json_util import loads

application = Flask(__name__)
CORS(application)
client=MongoClient("112.74.57.41", 27017,  connect=False)
db=client.lotapp



@application.route('/test', methods=['GET','POST'])
def test():
    return 'api is running'


@application.route('/games/<string:filterID>', methods=['GET','POST'])
def get_games(filterID):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    result = db.Result.find({"date"
                             "" : today, "filterID":filterID},{"_id": 0})
    print(result)
    return json.dumps(list(result), indent=4, ensure_ascii=False)

if __name__ == '__main__':
    application.run()