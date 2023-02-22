from app import app
from flask import request, make_response, jsonify
from dbhelpers import run_statement
from validhelpers import check_data
import json


# Make sure keys are put in the same order as they are in the DB tables. That way it matches with the postman response output
@app.get('/api/restaurant')
def get_restaurant():
    keys = ['id', 'name', 'address', 'city', 'email', 'phoneNum', 'password', 'profileUrl', 'bannerUrl', 'bio']
    restaurant_id = request.args.get("restaurantId")
    result = run_statement("CALL get_restaurant_argid(?)", [restaurant_id])
    restaurant_alpha = []
    if (type(result) == list):
        for restaurant in result:
            restaurant_alpha.append(dict(zip(keys, restaurant)))
        return make_response(jsonify(restaurant_alpha), 200)
    else:
        return make_response(jsonify(result), 500)
    
# Make sure the required data is camelCase and the same format as the json arguments in the request.json.get 
@app.post('/api/restaurant')
def post_restaurant():
    required_data = ['name', 'address', 'city', 'email', 'phoneNum', 'password', 'bio']
    check_result = check_data(request.json, required_data)
    if check_result != None:
        return check_result
    name = request.json.get('name')
    address = request.json.get('address')
    city = request.json.get('city')
    email = request.json.get('email')
    phone_num = request.json.get('phoneNum')
    password = request.json.get('password')
    profile_url = request.json.get('profileUrl')
    banner_url = request.json.get('bannerUrl')
    bio = request.json.get('bio')
    result = run_statement("CALL insert_restaurant(?,?,?,?,?,?,?,?,?)", [name, address, city, email, phone_num, password, profile_url, banner_url, bio])
    if (type(result) == list):
        response = {
                        'restaurantId' : result[0][0],
                        'token' : result[0][1],
        }
        print("New Restaurant recorded in DB!")
        return json.dumps(response, default=str)
    else:
        return "Sorry, something went wrong"

@app.patch('/api/restaurant')
def patch_restaurant():
    required_data = ['token']
    check_result = check_data(request.headers, required_data)
    if check_result != None:
        return check_result
    token_input = request.headers.get("token")
    name = request.json.get('name')
    address = request.json.get('address')
    city = request.json.get('city')
    email = request.json.get('email')
    phone = request.json.get('phone')
    password = request.json.get('password')
    profile_url = request.json.get('profileUrl')
    banner_url = request.json.get('bannerUrl')
    bio = request.json.get('bio')
    result = run_statement("CALL edit_restaurant_tokenarg(?,?,?,?,?,?,?,?,?,?)", [token_input, name, address, city, email, phone, password, profile_url, banner_url, bio])
    if result == None:
        return make_response(jsonify("Client info updated successfully"), 200)
    else:
        return make_response(jsonify("Update failed. Something went wrong"), 500)
