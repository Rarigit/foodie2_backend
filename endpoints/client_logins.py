from app import app
from flask import request, make_response, jsonify
from dbhelpers import run_statement
from validhelpers import check_data
import json



@app.post('/api/client-login')
def insert_client_login():
    required_data = ['email', 'password',]
    check_result = check_data(request.json, required_data)
    if check_result != None:
        return check_result
    email = request.json.get('email')
    password = request.json.get('password')
    result = run_statement("CALL insert_client_login(?,?)", [email, password])
    if (type(result) == list):
        response = {
                        'clientId' : result[0][0],
                        'token' : result[0][1],
        }
        print("New Client-login session recorded in DB!")
        return json.dumps(response, default=str)
    else:
        return "Sorry, something went wrong"
    

@app.delete('/api/client-login')
def delete_client_login():
    check_result = check_data(request.headers, ['token'])
    if check_result != None:
        return check_result
    token = request.headers.get('token')
    result = run_statement("CALL delete_clog_tkarg(?)", [token])
    if result == None:
        return make_response(jsonify("Successfully deleted Client login-session"), 200)
    else:
        return make_response(jsonify("Failed to delete Client login-session. Something went wrong"), 500)