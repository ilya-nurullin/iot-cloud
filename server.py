#pip3 install Flask

import http.server
import socketserver
from threading import Thread
import time
import sys
import json
import pymysql

from flask import Flask
from flask import request

app = Flask(__name__)

PORT = 8000

scripts = {} # '1': "print(\"It works\")"

con = pymysql.connect('localhost', 'root',  
    'password', 'SmartHouse', 
    autocommit=True)      


@app.route('/')
def home():
    return {'status': 'working'}

def setScript(name, code):
    global scripts
    scripts[name] = code
    
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
        query = f"SELECT  pyScript FROM Scripts WHERE scriptTitle = \'{name}\'"
        cur.execute(query)
        script = cur.fetchone()
        if(script == None):
            return {'Error': 'ScriptNotFound'}
        else:
            print(script)
            setScript(name, script[0])
            return {'status': 'Added to Run'}

@app.route('/script/all')
def allScripts():
    global scripts
    return scripts

@app.route('/script/change_status/<name>/<status>')
def changeScriptStatus(name, status):
	with con:
		cur = con.cursor()
		query = f"UPDATE Scripts SET isEnabled = \'{status}\' where scriptTitle = \'{name}\'"
		cur.execute(query)
		#cur.flush()
		#query = f"SELECT scriptTitle, isEnabled FROM Scripts WHERE scriptTitle = \'{name}\'"
		#cur.execute(query)
		#result = cur.fetchone()
		#if(script == None):
		#	return {'Error': 'ScriptNotFound'}
		#else:
			#return {'status': status, 'name': name }
	return {'status': status, 'name': name }
    
def runner():
    global scripts
    while True:
        time.sleep(0.1)
        for script in scripts.values():
            exec(script)

def insertOrUpdate(name, xmlCode, pyCode,isEnabled):
    with con:
        cur = con.cursor()
        query = f"SELECT * FROM Scripts WHERE scriptTitle = \"{name}\""
        cur.execute(query)
        script = cur.fetchone()
        if(script == None):
            query = f"INSERT INTO Scripts VALUES ( 0,\'{name}\', \'{pyCode}\', \'{xmlCode}\', {isEnabled});"
            cur.execute(query)
            return("inserted")
        else:
            query = f"UPDATE Scripts SET pyScript=\'{pyCode}\', xmlScript=\'{xmlCode}\',isEnabled= {isEnabled} where scriptTitle =\'{name}\'"
            cur.execute(query)
            return("updated")

    
def getScriptsByEnabled(is_enabled=None):
    whereClause = "";
    if (is_enabled == True):
        whereClause = "WHERE isEnabled = True";
    elif (is_enabled == False):
        whereClause = "WHERE isEnabled = False";
    with con:
        cur = con.cursor()
        query = "SELECT scriptTitle, pyScript FROM Scripts "+whereClause
        cur.execute(query)
        rows = cur.fetchall()
    return rows
    
def server():
    global PORT
    global scripts
    
    #load all enabled scripts to dictionary
    rows=getScriptsByEnabled(True)
    for row in rows:
        print(row[0], row[1])    
    app.run(host="0.0.0.0", port=PORT)

thread1 = Thread( target=runner )
thread1.daemon = True
thread1.start()

server()

sys.exit()
