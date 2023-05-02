from app import app
from flask import request, make_response, jsonify
from dbhelpers import run_statement
from validhelpers import check_data
import json
import bcrypt
import time

# Make 2 separate procedures for this one. One that selects the id, password
# Then decrypts it in PYTHON
# Once verifies it logs in the user

@app.post('/api/client-login')
def insert_client_login():
    required_data = ['email', 'password',]
    check_result = check_data(request.json, required_data)
    if check_result != None:
        return check_result
    email = request.json.get('email')
    password = request.json.get('password')
    result = run_statement("CALL inser_client_login_step1(?)", [email])
    if(type(result) == list):
        if result == []:
            return make_response(jsonify('Incorrect email address, please re-enter email.'), 400)
        # client_id_value = result[0][0]
        hashed_password = result[0][1]
        if (bcrypt.checkpw(password.encode(), hashed_password.encode())):
            result2 = run_statement("CALL insert_client_login_step2(?)", [result[0][0]])
            if (type(result) == list):
                response = {
                            'clientId' : result2[0][0],
                            'token' : result2[0][1],
                }
                print("New Client-login session recorded in DB!")
                return json.dumps(response, default=str)
        else:
            return make_response(jsonify("Error, please try again."), 400)
    

@app.delete('/api/client-login')
def delete_client_login():
    check_result = check_data(request.headers, ['token'])
    if check_result != None:
        return check_result
    token = request.headers.get('token')
    client_id_input = request.json.get("clientId")
    result_verify = run_statement("CALL verify_delete_clientlogin(?,?)", [client_id_input, token])
    print(result_verify)
    if result_verify[0][0] == 1:
        result = run_statement("CALL delete_clog_tkarg(?)", [token])
        if result == None:
            return make_response(jsonify("Successfully deleted Client login-session"), 200)
        else:
            return make_response(jsonify("Failed to delete Client login-session. Something went wrong"), 500)
    else:
        return "Invalid credentials. Denied access!"