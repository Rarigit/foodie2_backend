from app import app
from flask import request, make_response, jsonify
from dbhelpers import run_statement
from validhelpers import check_data
import json
import bcrypt
import time


# Make sure keys are put in the same order as they are in the DB tables. That way it matches with the postman response output
# Completed Bonus Restaurant Categories and Bonus Search capabilities by name and Bonus Regional filtering
#Edited sql procedure after presentation. Made all parameters truly optional instead of mandatory
@app.get('/api/restaurant')
def get_restaurant():
    keys = ['id', 'name', 'address', 'city', 'email', 'phoneNum', 'password', 'profileUrl', 'bannerUrl', 'bio']
    restaurant_id = request.args.get("restaurantId")
    city_input = request.args.get("searchCity")
    search_keyword = request.args.get('searchKeyword')
    categories_input = request.args.get('searchCategory')
    result = run_statement("CALL get_restaurant_argid(?,?,?,?)", [restaurant_id, city_input, search_keyword, categories_input])
    restaurant_alpha = []
    if (type(result) == list):
        for restaurant in result:
            restaurant_alpha.append(dict(zip(keys, restaurant)))
        return make_response(jsonify(restaurant_alpha), 200)
    else:
        return make_response(jsonify(result), 500)
    
#Edited post endpoint to include more specific error messages that are human readable and takes into account common user error.
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
    start = time.time_ns()
    salt = bcrypt.gensalt(rounds=12)
    hash_result = bcrypt.hashpw(password.encode(), salt)
    finish = time.time_ns()
    print(f"This encryption took {(finish-start)/1000000000} seconds")
    profile_url = request.json.get('profileUrl')
    banner_url = request.json.get('bannerUrl')
    bio = request.json.get('bio')
    result = run_statement("CALL insert_restaurant(?,?,?,?,?,?,?,?,?)", [name, address, city, email, phone_num, hash_result, profile_url, banner_url, bio])
    if "restaurant_UN_email" in result:
        return make_response(jsonify("Error: This email is already in use. Use another email."), 422)
    elif "chk_city" in result:
        return make_response(jsonify("Error: Chosen city unavailable, choose from approved city list."), 422)
    elif "restaurant_CHECK_email" in result:
        return make_response(jsonify("Error: Email must be in valid email format."), 422)
    elif "restaurant_CHECK" in result:
        return make_response(jsonify("Error: Phone Number must be in valid format: xxx-xxx-xxxx"), 422)
    else:
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
    # email = request.json.get('email')
    phone = request.json.get('phone')
    password = request.json.get('password')
    start = time.time_ns()
    salt = bcrypt.gensalt(rounds=12)
    hash_result = bcrypt.hashpw(password.encode(), salt)
    finish = time.time_ns()
    print(f"This encryption took {(finish-start)/1000000000} seconds")
    profile_url = request.json.get('profileUrl')
    banner_url = request.json.get('bannerUrl')
    bio = request.json.get('bio')
    result = run_statement("CALL edit_restaurant_tokenarg(?,?,?,?,?,?,?,?,?)", [token_input, name, address, city, phone, hash_result, profile_url, banner_url, bio])
    if result == None:
        return make_response(jsonify("Restaurant info updated successfully"), 200)
    else:
        return make_response(jsonify("Update failed. Something went wrong"), 500)

