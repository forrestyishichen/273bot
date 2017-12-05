#!/usr/bin/env python

import urllib
import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeWebhookResult(req):
    if req.get("result").get("action") == "check.price":
        result = req.get("result")
        parameters = result.get("parameters")
        branch = parameters.get("branch")
        bed = parameters.get("bed")

        branch_price = {'San Francisco':60.00, 'San Mateo':50.00, 'Palo Alto':100.00, 'Cupertino':80.00, 'San Jose':0.00}
        room_price = {'single':150.00, 'queen':200.00, 'king':200.00, 'twin':200.00, 'double-double':300.00, 'studio':500.00}

        speech = "The cost of a " + bed + " room in " + branch + " is " + str(float(branch_price[branch])+float(room_price[bed])) + " dollars."

        print("Response:")
        print(speech)

        return {
            "speech": speech,
            "displayText": speech,
            #"data": {},
            # "contextOut": [],
            "source": "apiai-onlinestore-shipping"
            }
    else:
        return {}


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(port)

    print ("Starting app on port %d" % port)

    app.run(debug=True, port=port, host='0.0.0.0')
