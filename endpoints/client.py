from app import app
from flask import request, make_response, jsonify
from dbhelpers import run_statement
# from dbcreds import production_mode
from validhelpers import check_data



@app.get('/api/client')
def get_client():
    keys = ['username', 'first_name', 'last_name', 'email', 'password', 'created_at', 'picture_url', 'client_id']
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
    required_data = ['username', 'first_name', 'last_name', 'email', 'password',]
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
    if result == None:
        return "New client recorded in DB!"
    else:
        return "Sorry, something went wrong"

@app.patch('/api/client')
def patch_client():
    required_data = ['token']
    check_result = check_data(request.json, required_data)
    if check_result != None:
        return check_result
    password = request.json.get('password')
    username = request.json.get('userName')
    first_name = request.json.get('firstName')
    last_name = request.json.get('lastName')
    picture_url = request.json.get('pictureUrl')
    result = run_statement("CALL edit_client_tokenarg(?,?,?,?,?,?)", [password, username, first_name, last_name, picture_url])
    if result == None:
        return "Client info updated successfully"
    else:
        return "Sorry, something went wrong"


@app.delete('/api/client')
def delete_candies():
    check_result = check_data(request.json, ['token'])
    if check_result != None:
        return check_result
    token = request.json.get('token')
    result = run_statement("CALL delete_client_tkarg(?)", [token])
    if result == None:
        return "Successfully deleted Client {}".format(id)
    else:
        return "Client {} does not exist".format(id)