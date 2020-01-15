#pip3 install Flask
#pip3 install psycopg2
#pip3 install flask-cors

import psycopg2
import psycopg2.extras

import http.server
import socketserver
from threading import Thread
import time
import sys
import json
import time

from flask import Flask
from flask import request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

PORT = 8999

scripts = {} # '1': "print(\"It works\")"

con = psycopg2.connect(host='localhost', port=5432, user='postgres',  
    password='password', dbname='smarthouse')
con.autocommit = True


@app.route('/')
def home():
    return {'status': 'working'}

def setScript(id, code):
    global scripts
    scripts[str(id)] = code
    
@app.route('/script/add', methods=['POST'])
def addScriptToDB():    
    inputs = request.get_json()
    
    if ('name' not in inputs):
        return ({'status': 'data_error', 'message': 'name expected'}, 400)
    
    if ('xmlCode' not in inputs):
        return ({'status': 'data_error', 'message': 'XML code expected'}, 400)

    if ('pyCode' not in inputs):
        return ({'status': 'data_error', 'message': 'Python code expected'}, 400)
    
    if ('is_enabled' not in inputs):
        return ({'status': 'data_error', 'message': 'is_enabled status expected'}, 400)
        
    name = inputs['name']
    xmlCode = inputs['xmlCode']
    pyCode = inputs['pyCode']
    is_enabled = inputs['is_enabled']
    return insertOrUpdate(name, xmlCode, pyCode,is_enabled)
        
@app.route('/script/addToRun', methods=['POST'])
def addScriptToRun():
	inputs = request.get_json()
	if ('name' not in inputs):
		return ({'status': 'data_error', 'message': 'name expected'}, 400)
	name = inputs['name']
	with con:
		cur = con.cursor()
		query = f"SELECT script_id, py_script FROM scripts WHERE script_title = \'{name}\'"
		cur.execute(query)
		script = cur.fetchone()
		if(script == None):
			return {'Error': 'ScriptNotFound'}
		else:
			syncEnabledScripts()
			return {'status': 'Added to Run'}

@app.route('/script/all')
def allScripts():
    return json.dumps(getScriptsByEnabled())

@app.route('/script/change_status/<id>/<status>')
def changeScriptStatus(id, status):
	with con:
		cur = con.cursor()
		query = f"UPDATE scripts SET is_enabled = {status} where script_id = {id}"
		cur.execute(query)
		#cur.flush()
		#query = f"SELECT script_title, is_enabled FROM scripts WHERE script_title = \'{name}\'"
		#cur.execute(query)
		#result = cur.fetchone()
		#if(script == None):
		#	return {'Error': 'ScriptNotFound'}
		#else:
			#return {'status': status, 'name': name }
	syncEnabledScripts()
	return {'status': status, 'id': id }
    
def runner():
    global scripts
    while True:
        time.sleep(0.1)
        if len(scripts) > 0:
            for script in scripts.values():
                exec(script)

def insertOrUpdate(name, xmlCode, pyCode,isEnabled):
    with con:
        cur = con.cursor()
        query = f"SELECT * FROM scripts WHERE script_title = \'{name}\'"
        cur.execute(query)
        script = cur.fetchone()
        pyCode = pyCode.replace("'", "\\'")
        if(script == None):
            query = f"INSERT INTO scripts(script_title, py_script, xml_script, is_enabled) VALUES ( \'{name}\', \'{pyCode}\', \'{xmlCode}\', {isEnabled});"
            cur.execute(query)
            syncEnabledScripts()
            return("inserted")
        else:
            query = f"UPDATE scripts SET py_script=\'{pyCode}\', xml_script=\'{xmlCode}\',is_enabled= {isEnabled} where script_title =\'{name}\'"
            cur.execute(query)
            syncEnabledScripts()
            return("updated")

    
def getScriptsByEnabled(is_enabled=None):
    whereClause = ""
    if (is_enabled == True):
        whereClause = "WHERE is_enabled = True"
    elif (is_enabled == False):
        whereClause = "WHERE is_enabled = False"
    with con:
        cur = con.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        query = f"SELECT script_id, script_title, py_script, is_enabled FROM scripts {whereClause}"
        cur.execute(query)
        rows = cur.fetchall()
    return rows

def syncEnabledScripts():
    global scripts
    rows=getScriptsByEnabled(True)
    scripts = {}
    for row in rows:
        setScript(row['script_id'], row['py_script'])   

def server():
    global PORT
    global scripts
    
    #load all enabled scripts to dictionary
    rows=getScriptsByEnabled(True)
    for row in rows:
        setScript(row['script_id'], row['py_script'])   
    app.run(host="0.0.0.0", port=PORT)

thread1 = Thread( target=runner )
thread1.daemon = True
thread1.start()

server()

sys.exit()
