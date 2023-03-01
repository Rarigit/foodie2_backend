from app import app
from flask import request, make_response, jsonify
from dbhelpers import run_statement
from validhelpers import check_data
# import json


# Completed bonus menu category and Bonus search capability for menu items
@app.get('/api/menu')
def get_menu():
    keys = ['id', 'name', 'description', 'price', 'imageUrl', 'restaurantId', 'searchCategory']
    restaurant_id = request.args.get("restaurantId")
    menu_id = request.args.get("menuId")
    search_name = request.args.get('searchKeyword')
    categories_input = request.args.get('searchCategory')
    result = run_statement("CALL get_menu_arg_ridmid(?,?,?,?)", [restaurant_id, menu_id, search_name, categories_input])
    menu_alpha = []
    if (type(result) == list):
        for menu in result:
            menu_alpha.append(dict(zip(keys, menu)))
        return make_response(jsonify(menu_alpha), 200)
    else:
        return make_response(jsonify(result), 500)
    

@app.post('/api/menu')
def insert_menu():
    required_data = ['name', 'description', 'price']
    check_result = check_data(request.json, required_data)
    if check_result != None:
        return check_result
    token_input = request.headers.get("restToken")
    restaurant_id_input = request.json.get('restaurantId')
    result_verify = run_statement("CALL verify_post_menu(?,?)", [restaurant_id_input, token_input])
    print(result_verify)
    if result_verify[0][0] == 1:
        name = request.json.get('name')
        description = request.json.get('description')
        price = request.json.get('price')
        image_url = request.json.get('imageUrl')
        result = run_statement("CALL insert_menu_argtk(?,?,?,?,?,?)", [token_input ,name, description, price, image_url, restaurant_id_input])
        if result == None:
            return make_response(jsonify("Menu inserted successfully"), 200)
        else:
            return make_response(jsonify("Failed to insert menu. Something went wrong"), 500)
    else:
        return "Credential Authentication failed. Error!"



@app.patch('/api/menu')
def patch_menu():
    required_data = ['restToken']
    check_result = check_data(request.headers, required_data)
    if check_result != None:
        return check_result
    token_input = request.headers.get("restToken")
    restaurant_id_input = request.json.get('restaurantId')
    result_verify = run_statement("CALL verify_patch_menu(?,?)", [restaurant_id_input, token_input])
    print(result_verify)
    if result_verify[0][0] == 1:
        id = request.json.get('menuId')
        name = request.json.get('name')
        description = request.json.get('description')
        price = request.json.get('price')
        image_url = request.json.get('imageUrl')
        result = run_statement("CALL edit_menu_argmid(?,?,?,?,?,?,?)", [token_input, id, name, description, price, image_url, restaurant_id_input])
        if result == None:
            return make_response(jsonify("Menu info updated successfully"), 200)
        else:
            return make_response(jsonify("Menu info update failed. Something went wrong"), 500)
    else:
        return "Credential Authentication Failed. Error!"


@app.delete('/api/menu')
def delete_menu():
    check_result = check_data(request.headers, ['restToken'])
    if check_result != None:
        return check_result
    token_input = request.headers.get('restToken')
    restaurant_id_input = request.json.get('restaurantId')
    result_verify = run_statement("CALL verify_delete_menu(?,?)", [restaurant_id_input, token_input])
    print(result_verify)
    if result_verify[0][0] == 1:
        id = request.json.get('menuId')
        result = run_statement("CALL del_menu_argid(?,?)", [token_input, id])
        if result == None:
            return make_response(jsonify("Successfully deleted Menu item"), 200)
        else:
            return make_response(jsonify("Failed to delete Menu item. Something went wrong"), 500)
    else:
        return "Credential Authentication Failed. Error!"
    
    