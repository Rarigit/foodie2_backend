from app import app
from flask import request, make_response, jsonify
from dbhelpers import run_statement
from validhelpers import check_data
import json


@app.get('/api/order-client')
def get_order_client():
    # Also included items to keys to see it in my postman response code
    keys = ['orderId', 'clientId', 'restaurantId', 'isConfirmed', 'isComplete', 'isCancelled', 'createdAt', 'items']
    # token_input = request.headers.get("clientToken")
    token_input = request.headers.get("Token")
    print(request.headers)
    client_id_input = request.args.get("client")
    print(request.args)
    result_verify = run_statement("CALL get_order_tkid_verify(?,?)", [client_id_input, token_input])
    print("result_verify:", result_verify)
    if result_verify[0][0] == 1:
        id_input = request.args.get("orderId")
        result = run_statement("CALL get_order_client_argoid(?,?)", [token_input, id_input])
        order_alpha = []
        # Using this if I parse the items string into a python lists via split to make a list for item ids, as i was just getting a bunch of dictionaries which was redundant  
        if (type(result) == list):
            for order in result:
                order_dict = dict(zip(keys, order))
                if order_dict['items'] is not None:
                    order_dict['items'] = [int(item_id) for item_id in order_dict['items'].split(',')]
                order_alpha.append(order_dict)
            return make_response(jsonify(order_alpha), 200)
        else:
            return make_response(jsonify(result), 500)
    else:
        return "Error. Authentication verification failed. Please input credentials again."

# Restaurant-order
@app.get('/api/order-restaurant')
def get_order_restaurant():
    keys = ['orderId', 'clientId', 'restaurantId', 'isConfirmed', 'isComplete', 'isCancelled', 'createdAt', 'items']
    token_input = request.headers.get("Token")
    print(token_input)
    restaurant_id_input = request.headers.get("restaurantID")
    print(request.headers)
    result_verify = run_statement("CALL get_order_tkid_verify_restaurant(?,?)", [restaurant_id_input, token_input])
    if result_verify[0][0] == 1:
        id_input = request.args.get("orderId")
        result = run_statement("CALL get_order_rest_argoid(?,?)", [token_input, id_input])
        order_alpha = []
        if (type(result) == list):
            for order in result:
                order_dict = dict(zip(keys, order))
                if order_dict['items'] is not None:
                    order_dict['items'] = [int(item_id) for item_id in order_dict['items'].split(',')]
                order_alpha.append(order_dict)
            return make_response(jsonify(order_alpha), 200)
        else:
            return make_response(jsonify(result), 500)
    else:
        return "Error. Authentication verification failed. Please input credentials again."


# No need for keys i guess on post request
# Make sure the required data is camelCase and the same format as the json arguments in the request.json.get 
# The POST for this endpoint allows creating orders. Orders can only contain items from a single restaurant and can only be placed by signed-in clients
# The items in an order are a mandatory field and must be in list form. The list of items corresponds to the menu item IDs
# Since its only signed in clients i think it might be a clientToken that is required. Need to confirm 
# Only did is-cancelled input because it was a client side insert and clients can only cancel an order. Looks like data truncation issue affects all columns too 
# Convert the True/False str boolean to an int as my "isCancelled" column is of TinyInt(1) which is an integer 0/1 representing True or False in my stored procedure
#Final changes to the post order endpoint utilizing Mark's advice from the presentation
@app.post('/api/order')
def insert_order():
    keys = ['orderId', 'clientId', 'restaurantId', 'isConfirmed', 'isComplete', 'isCancelled', 'createdAt', 'items']
    # cut out items for now in required data
    # required_data = ['clientToken','restaurantId']
    # check_result = check_data(request.json, required_data)
    # if check_result != None:
    #     return check_result
    token_input = request.headers.get("Token")
    # token_input = request.headers.get("clientToken")
    print("Received token:", token_input) 
    print(request.headers)
    client_id_input = request.json.get("clientId")
    restaurant_id_input= request.json.get('restaurantId')
    # menu_item_id_input = request.json.get('menuItemId')
    # # Made an extra request.json for menu_item_id as I need to verify that both menu item and restaurant originate from the same row 
    # verify_item_store = run_statement("CALL get_itemid_restaurantid_verified(?,?)", [menu_item_id_input, restaurant_id_input])
    # print(verify_item_store)
    # if 1 == 1:
    # item_input = request.json.get('items')
    result = run_statement("CALL create_order(?,?,?)", [token_input, client_id_input, restaurant_id_input])
        # This basically will extract the result generated which is a list of lists of order id Ex. [[23,]]
    # order_id = result[0][0] 
    if (type(result) == list):
        order_id = result[0][0] 
        item_id_input = request.json.get('items')
    # if result is not None and len(result) > 0:
    # if (type(result) == None):
        for item in item_id_input:
            #Here I'm adding another check to confirm each item in the list of items within the loop belongs to the correct restaurant
            # verify_item_store = run_statement("CALL get_itemid_restaurantid_verified(?,?)", [menu_item_id_input, restaurant_id_input])
            # # verify_item_store[0][0] == 1
            result_two = run_statement("CALL insert_order(?,?)", [item, order_id])
            if (type(result_two) == list):
                if result_two[0][0] == 1:
                    return make_response(jsonify(f"Successfully Sent Order {order_id} to Restaurant"), 200)
                elif result_two[0][0] == 0:
                    return make_response(jsonify("Error: Order was not sent, please try again."), 500)
            # return make_response(jsonify("Order-id selected and items list inserted successfully"), 200)
    # else:
    #     return "The menu items do not originate from that restaurant. Error!"
    else:
        return make_response(jsonify(result), 500)


# Client Order Edit
@app.patch('/api/order-client')
def patch_order_client():
    # required_data = ['clientToken']
    required_data = ['Token']
    check_result = check_data(request.headers, required_data)
    if check_result != None:
        return check_result
    # token_input = request.headers.get('clientToken') 
    token_input = request.headers.get("Token")
    print("Received token:", token_input) 
    print(request.headers)
    client_id_input = request.json.get("clientId")
    print(request.json)
    # client_id_input = request.json.get("clientId")
    # print(client_id_input)
    # is_cancelled_input = request.json.get('cancelOrder')
    # print(is_cancelled_input)
    is_cancelled_input = request.json.get('cancelOrder')
    print(is_cancelled_input)
    result_verify = run_statement("CALL get_cliord_patch_verify(?,?)", [client_id_input, token_input])
    # Follow the same parameter order as in the stored procedure or else truncation errors occur
    print(result_verify)
    if result_verify[0][0] == 1:
        id_input = request.json.get('orderId')
        result = run_statement("CALL edit_client_oder(?,?,?)", [token_input, is_cancelled_input, id_input])
        if result == None:
            return make_response(jsonify("Client Order info updated successfully"), 200)
        else:
            return make_response(jsonify("Failed to update client info. Something went wrong"), 500)
    else:
        return "Credential Authentication failed. Please try again!"




# Restaurant Order Edit
@app.patch('/api/order-restaurant')
def patch_order_restaurant():
    required_data = ['Token']
    check_result = check_data(request.headers, required_data)
    if check_result != None:
        return check_result
    token_input = request.headers.get("Token")
    restaurant_id_input = request.headers.get('restaurantID')
    is_confirmed_input = request.json.get('confirmOrder')
    is_complete_input = request.json.get('completeOrder')
    print(is_complete_input)
    result_verify = run_statement("CALL verify_patch_order_store(?,?)", [restaurant_id_input, token_input])
    print(result_verify)
    if result_verify[0][0] == 1:
        id_input = request.json.get('orderId')
        result = run_statement("CALL edit_restaurant_order(?,?,?,?)", [token_input, is_confirmed_input, is_complete_input, id_input])
        if result == None:
            return make_response(jsonify("Restaurant Order info updated successfully"), 200)
        else:
            return make_response(jsonify("Failed to update restaurant order info. Error"), 500)
    else:
        return "Credential Authentication failed. Please try again!"
