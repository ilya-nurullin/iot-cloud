# pip3 install Flask

import http.server
import socketserver
from threading import Thread
import time
import sys
import json

from flask import Flask
from flask import request

app = Flask(__name__)

PORT = 8000

scripts = {} # '1': "print(\"It works\")"

@app.route('/')
def home():
    return {'status': 'working'}

def setScript(name, code):
    global scripts
    scripts[name] = code
    
@app.route('/script/add', methods=['POST'])
def addScript():    
    inputs = request.get_json()
    
    if ('name' not in inputs):
        return ({'status': 'data_error', 'message': 'name expected'}, 400)
    
    if ('code' not in inputs):
        return ({'status': 'data_error', 'message': 'code expected'}, 400)
        
    name = inputs['name']
    code = inputs['code']
    if (name in scripts):
        setScript(name, code)
        return {'status': 'updated'}
    else:
        setScript(name, code)
        return {'status': 'created'}

@app.route('/script/all')
def allScripts():
    global scripts
    return scripts

@app.route('/script/change_status/<name>/<status>')
def changeScriptStatus(name, status):
    global scripts
    return {'status': status, 'name': name}
    
def runner():
    global scripts
    while True:
        time.sleep(0.1)
        for script in scripts.values():
          exec(script)

def server():
    global PORT
    app.run(host="0.0.0.0", port=PORT)


thread1 = Thread( target=runner )
thread1.daemon = True
thread1.start()

server()

sys.exit()
