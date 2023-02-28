from app import app
from flask import request, make_response, jsonify
from dbhelpers import run_statement
from validhelpers import check_data
import json
import bcrypt
import time


@app.post('/api/restaurant-login')
def insert_restaurant_login():
    required_data = ['email', 'password',]
    check_result = check_data(request.json, required_data)
    if check_result != None:
        return check_result
    email = request.json.get('email')
    password = request.json.get('password')
    result = run_statement("CALL restaurant_login_step1(?)", [email])
    if isinstance(result, list) and len(result) > 0 and len(result[0]) > 0:
        restaurant_id_value = result[0][0]
        hashed_password = result[0][1]
        if (bcrypt.checkpw(password.encode(), hashed_password.encode())):
            result2 = run_statement("CALL insert_restlogin_step2(?)", [restaurant_id_value])
            if isinstance(result2, list):
                response = {
                            'restaurantId' : result2[0][0],
                            'token' : result2[0][1],
                }
                print("New Restaurant-login session recorded in DB!")
                return json.dumps(response, default=str)
            else:
                return "Sorry, something went wrong"
        else:
            return "Invalid email or password"
    else:
        return "Invalid email or password"


@app.delete('/api/restaurant-login')
def delete_restaurant_login():
    check_result = check_data(request.headers, ['token'])
    if check_result != None:
        return check_result
    token = request.headers.get('token')
    restaurant_id_input = request.json.get("restaurantId")
    result_verify = run_statement("CALL verify_store_login(?,?)", [restaurant_id_input, token])
    print(result_verify)
    if result_verify[0][0] == 1:
        result = run_statement("CALL del_restaurant_login(?)", [token])
        if result == None:
            return make_response(jsonify("Successfully deleted Restaurant login-session"), 200)
        else:
            return make_response(jsonify("Failed to delete Restaurant login-session. Something went wrong"), 500)
    else:
        return "Invalid credentials. Denied access!"