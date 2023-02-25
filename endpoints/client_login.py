from app import app
from flask import request, make_response, jsonify
from dbhelpers import run_statement
from validhelpers import check_data
import json
import bcrypt
import time

@app.post('/api/client-login')
def insert_client_login():
    required_data = ['email', 'password',]
    check_result = check_data(request.json, required_data)
    if check_result != None:
        return check_result
    email = request.json.get('email')
    password = request.json.get('password')
    # I definitely need to make 2 separate procedures for this one. One that selects the id, password
    # Then decrypts it in PYTHON
    # Once verifies it logs in the user
    result = run_statement("CALL inser_client_login_step1(?)", [email])
    if isinstance(result, list) and len(result) > 0 and len(result[0]) > 0:
        client_id_value = result[0][0]
        hashed_password = result[0][1]
        if (bcrypt.checkpw(password.encode(), hashed_password.encode())):
            result2 = run_statement("CALL insert_client_login_step2(?)", [client_id_value])
            if isinstance(result2, list):
                response = {
                            'clientId' : result2[0][0],
                            'token' : result2[0][1],
                }
                print("New Client-login session recorded in DB!")
                return json.dumps(response, default=str)
            else:
                return "Sorry, something went wrong"
        else:
            return "Invalid email or password"
    else:
        return "Invalid email or password"
    

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