from app import app
from flask import request, make_response, jsonify
from dbhelpers import run_statement
from validhelpers import check_data
import json



@app.get('/api/client')
def get_client():
    keys = ['username', 'first_name', 'last_name', 'email', 'created_at', 'picture_url', 'client_id']
    token_input = request.headers.get("token")
    result = run_statement("CALL get_client_tokenarg(?)", [token_input])
    client_alpha = []
    if (type(result) == list):
        for client in result:
            client_alpha.append(dict(zip(keys, client)))
        return make_response(jsonify(client_alpha), 200)
    else:
        return make_response(jsonify(result), 500)
    

@app.post('/api/client')
def insert_client():
    # Make sure the required data is camelCase and the same format as the json arguments in the request.json.get 
    required_data = ['userName', 'firstName', 'lastName', 'email', 'password']
    check_result = check_data(request.json, required_data)
    if check_result != None:
        return check_result
    # keys = ['username', 'first_name', 'last_name', 'email', 'password', 'created_at', 'picture_url']
    # No need for keys i guess on post request
    username = request.json.get('userName')
    first_name = request.json.get('firstName')
    last_name = request.json.get('lastName')
    email = request.json.get('email')
    password = request.json.get('password')
    created_at = request.json.get('createdAt')
    picture_url = request.json.get('pictureUrl')
    result = run_statement("CALL insert_client(?,?,?,?,?,?,?)", [username, first_name, last_name, email, password, created_at, picture_url])
    if (type(result) == list):
        response = {
                        'clientId' : result[0][0],
                        'token' : result[0][1],
        }
        print("New client recorded in DB!")
        return json.dumps(response, default=str)
    else:
        return "Sorry, something went wrong"

@app.patch('/api/client')
def patch_client():
    required_data = ['token']
    check_result = check_data(request.headers, required_data)
    if check_result != None:
        return check_result
    token_input = request.headers.get("token")
    password = request.json.get('password')
    username = request.json.get('userName')
    first_name = request.json.get('firstName')
    last_name = request.json.get('lastName')
    picture_url = request.json.get('pictureUrl')
    result = run_statement("CALL edit_client_tokenarg(?,?,?,?,?,?)", [token_input, password, username, first_name, last_name, picture_url])
    if result == None:
        return make_response(jsonify("Client info updated successfully"), 200)
    else:
        return make_response(jsonify("Update failed. Something went wrong"), 500)


# Tried format(id) method by using debugger, Couldn't find any data for it as result is truly none so gonna use another method to print better responses to Postman
@app.delete('/api/client')
def delete_client():
    check_result = check_data(request.headers, ['token'])
    if check_result != None:
        return check_result
    token = request.headers.get('token')
    result = run_statement("CALL delete_client_tkarg(?)", [token])
    if result == None:
        return make_response(jsonify("Successfully deleted client"), 200)
    # Need to format this correctly deletion action works tho. Done!
    else:
        return make_response(jsonify("Failed to delete client. Something went wrong"), 500)
        # return "Client {} does not exist".format(id)
    
    
