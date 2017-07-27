import os
import redis
from flask import Flask, render_template, redirect, request, url_for, make_response
import json

if 'VCAP_SERVICES' in os.environ:
    VCAP_SERVICES = json.loads(os.environ['VCAP_SERVICES'])
    CREDENTIALS = VCAP_SERVICES["rediscloud"][0]["credentials"] 
    r = redis.Redis(host=CREDENTIALS["hostname"], port=CREDENTIALS["port"], password=CREDENTIALS["password"]) 
else: 
    r = redis.Redis(host='127.0.0.1', port='6379') 

#r = redis.Redis(host='redis-10439.c14.us-east-1-2.ec2.cloud.redislabs.com', port='10439', password='JWmXAZRFhTuM3aXG')

app = Flask(__name__)

@app.route('/')
def survey():
    resp = make_response(render_template('survey.html'))
    return resp

@app.route('/suthankyou.html', methods=['POST'])
def suthankyou():

    ## This is how you grab the contents from the form
    f = request.form['feedback']
    d = request.form['Division']
    s = request.form['state']

    r.incr("counter", 1)
    counter = r.get("counter")
    
    response = d + "," + s + "," + f

    r.hset("responses",counter,response)
    
    print r.hgetall("responses")
    resp = """
    <h3> - THANKS FOR TAKING THE SURVEY - </h3>
    <a href="/"><h3>Back to main menu</h3></a>
    """

    return resp

@app.route('/results')
def results():
    start_page = """<html><body>"""
    mid_page = ""

    for resp in r.hvals("responses"):
        mid_page += resp + "<br>"
            
    end_page = """</body></html>"""

  
    return start_page + mid_page + end_page

if __name__ == "__main__":
	app.run(debug=False, host='0.0.0.0', \
                port=int(os.getenv('PORT', '5000')), threaded=True)
