import mysql.connector
from flask import Flask, jsonify, request, render_template, redirect, url_for, session, Response
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt
import time
from datetime import datetime

import base64
from io import StringIO
import PIL.Image
import razorpay
from flask_cors import CORS

from authlib.integrations.flask_client import OAuth
import os

from itertools import groupby

import json
#from compile_solidity_utils import w3, deploy_n_transact
from marshmallow import Schema, fields, ValidationError
import json
from web3 import Web3
from solcx import compile_standard, install_solc, compile_files, compile_source, link_code
import sys
from functools import lru_cache
from web3 import Web3
from web3.auto import w3
from web3.contract import Contract
from web3._utils.events import get_event_data
from web3._utils.abi import exclude_indexed_event_inputs, get_abi_input_names, get_indexed_event_inputs, normalize_event_input_types
from web3.exceptions import MismatchedABI, LogTopicError
from web3.types import ABIEvent
from eth_utils import event_abi_to_log_topic, to_hex
from hexbytes import HexBytes
import random


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

oauth = OAuth(app)
app.secret_key="HungryHogOinkOink"

# Creating connection object
conn = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "pass@123",
    database = "tiffin_service"
)

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
account_key = w3.eth.accounts[1]

##############################################################################################################################################################
####### OAUTH ########
##############################################################################################################################################################

#GOOGLE
@app.route('/google/')
def google():
   
    # Google Oauth Config
    # Get client_id and client_secret from environment variables
    # For developement purpose you can directly put it
    # here inside double quotes
    GOOGLE_CLIENT_ID = "334805346698-8oq76gdpbl9cud4q48b2ah5t492k94sg.apps.googleusercontent.com"
    GOOGLE_CLIENT_SECRET = "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"
     
    CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url=CONF_URL,
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
     
    # Redirect to google_auth function
    redirect_uri = url_for('google_auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)
 
@app.route('/google/auth/')
def google_auth():
    token = oauth.google.authorize_access_token()
    #user = oauth.google.parse_id_token(token)
    session['USER_EMAIL'] = token['userinfo']['email']
    session['USER_NAME'] = token['userinfo']['name']

    mycursor = conn.cursor()
    sql = "INSERT IGNORE INTO USERS VALUES (%s, '', %s, '', '', '', '', '', %s);"
    val = (session['USER_NAME'], session['USER_EMAIL'], w3.eth.accounts[random.randint(0,9)])
    mycursor.execute(sql, val)
    conn.commit()
    
    mycursor = conn.cursor()
    mycursor.execute('SELECT * FROM USERS WHERE USER_EMAIL="'+session["USER_EMAIL"]+'"')
    myresult = mycursor.fetchall()
    print(myresult)
    session['USER_PASSWORD'] = myresult[0][1]
    session['USER_STREET'] = myresult[0][3]
    session['USER_STATE'] = myresult[0][4]
    session['USER_CITY'] = myresult[0][5]
    session['USER_PINCODE'] = myresult[0][6]
    session['USER_MOBILE'] = myresult[0][7]
    session['USER_PRIVATE_KEY'] = myresult[0][8]

    mycursor = conn.cursor()
    mycursor.execute('SELECT COUNT(*) FROM ORDER_SUMMARY WHERE USER_EMAIL="'+session["USER_EMAIL"]+'" AND IS_COMPLETE=0')
    myresult = mycursor.fetchall()
    session['CART_COUNT'] = myresult[0][0]

    print(" Google User ", token['userinfo']['email'])
    return redirect('/')



#FACEBOOK
@app.route('/facebook/')
def facebook():
   
    # Facebook Oauth Config
    FACEBOOK_CLIENT_ID = os.environ.get('FACEBOOK_CLIENT_ID')
    FACEBOOK_CLIENT_SECRET = os.environ.get('FACEBOOK_CLIENT_SECRET')
    oauth.register(
        name='facebook',
        client_id=FACEBOOK_CLIENT_ID,
        client_secret=FACEBOOK_CLIENT_SECRET,
        access_token_url='https://graph.facebook.com/oauth/access_token',
        access_token_params=None,
        authorize_url='https://www.facebook.com/dialog/oauth',
        authorize_params=None,
        api_base_url='https://graph.facebook.com/',
        client_kwargs={'scope': 'email'},
    )
    redirect_uri = url_for('facebook_auth', _external=True)
    return oauth.facebook.authorize_redirect(redirect_uri)
 
@app.route('/facebook/auth/')
def facebook_auth():
    token = oauth.facebook.authorize_access_token()
    resp = oauth.facebook.get(
        'https://graph.facebook.com/me?fields=id,name,email,picture{url}')
    profile = resp.json()
    print("Facebook User ", profile)
    return redirect('/')



#TWITTER
@app.route('/twitter/')
def twitter():
   
    # Twitter Oauth Config
    TWITTER_CLIENT_ID = os.environ.get('TWITTER_CLIENT_ID')
    TWITTER_CLIENT_SECRET = os.environ.get('TWITTER_CLIENT_SECRET')
    oauth.register(
        name='twitter',
        client_id=TWITTER_CLIENT_ID,
        client_secret=TWITTER_CLIENT_SECRET,
        request_token_url='https://api.twitter.com/oauth/request_token',
        request_token_params=None,
        access_token_url='https://api.twitter.com/oauth/access_token',
        access_token_params=None,
        authorize_url='https://api.twitter.com/oauth/authenticate',
        authorize_params=None,
        api_base_url='https://api.twitter.com/1.1/',
        client_kwargs=None,
    )
    redirect_uri = url_for('twitter_auth', _external=True)
    return oauth.twitter.authorize_redirect(redirect_uri)
 
@app.route('/twitter/auth/')
def twitter_auth():
    token = oauth.twitter.authorize_access_token()
    resp = oauth.twitter.get('account/verify_credentials.json')
    profile = resp.json()
    print(" Twitter User", profile)
    return redirect('/')


##############################################################################################################################################################
# client = razorpay.Client(auth=("rzp_test_JGsIexMIOVh3bW", "kpvTVMIBppTJGlKtMmnzwcVd"))

# DATA = {
#     "amount": 100,
#     "currency": "INR",
#     "receipt": "receipt#1",
#     "notes": {
#         "key1": "value3",
#         "key2": "value2"
#     }
# }
# print(client.order.create(data=DATA))



##############################################################################################################################################################
####### Ethereum ########
##############################################################################################################################################################




def getSnackReviews(snack_id):
    snack_reviews = []
    with open("data.json", 'r') as f:
        datastore = json.load(f)
    abi = datastore["abi"]
    contract_address = datastore["contract_address"]

    # Create the contract instance with the newly-deployed address
    contract = w3.eth.contract(
        address=contract_address, abi=abi,
    )

    for i in range(contract.functions.get_array_length(snack_id).call()):
        temp = contract.functions.getReview(snack_id, i).call()
        snack_review = {
            "USER_EMAIL": temp[0],
            "USER_NAME": temp[1],
            "SNACK_ID": temp[2],
            "SNACK_REVIEW": temp[3],
            "SCHEDULE_DATE": temp[4],
            "SNACK_RATING": temp[5]
        }
        snack_reviews.append(snack_review)

    return (snack_reviews)

def getSnackUserReviews(snack_id, user_email, schedule_date):
    with open("data.json", 'r') as f:
        datastore = json.load(f)
    abi = datastore["abi"]
    contract_address = datastore["contract_address"]

    # Create the contract instance with the newly-deployed address
    contract = w3.eth.contract(
        address=contract_address, abi=abi,
    )

    return (contract.functions.getUserReview(snack_id, user_email, schedule_date).call())



def deploy_contract(contract_interface):
    # Instantiate and deploy contract
    account = account_key
    # print(account)
    contract = w3.eth.contract(
    abi=contract_interface['abi'],
    bytecode=contract_interface['bin']
    )
# Get transaction hash from deployed contract
    ''''
    tx_hash = contract.deploy(
    transaction={'from': w3.eth.accounts[1]}
    )
# Get tx receipt to get contract address
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    '''
    
    construct_txn = contract.constructor().build_transaction(
        {
            "gasPrice": 0, 
            'from': account,
            'nonce': w3.eth.get_transaction_count(account),
        }
    )

    # 6. Sign tx with PK
    # tx_create = w3.eth.account.sign_transaction(construct_txn, account.private_key)

    # 7. Send tx and wait for receipt
    # tx_hash = w3.eth.send_raw_transaction(tx_create.rawTransaction)
    tx_hash = w3.eth.send_transaction(construct_txn)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)


    return tx_receipt['contractAddress']

# compile all contract files
#contracts = compile_files(['review.sol', 'stringUtils.sol'])
def compile_contract():
    _solc_version = "0.4.24"
    install_solc(_solc_version)
    review = open("review.sol","r").read()
    stringUtils = open("stringUtils.sol","r").read()
    '''
    contracts = compile_standard(
        {
            "language": "Solidity",
            import_remappings=['=./pathDirectory', '-'])
            "sources": {"./review.sol": {"content": review}},
            "settings": {
                "outputSelection": {
                    "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
                }
            },
        },
        solc_version=_solc_version,
    )
    '''
    contracts = compile_source(
        review,
        output_values=["abi", "bin", "metadata"],
        solc_version=_solc_version
    )
    #print(contracts)


    # separate main file and link file
    # main_contract = contracts.pop("review.sol:reviewRecords")
    # library_link = contracts.pop("stringUtils.sol:StringUtils")
    main_contract = contracts.pop("<stdin>:reviewRecords")

    contracts = compile_source(
        stringUtils,
        output_values=["abi", "bin", "metadata"],
        solc_version=_solc_version
    )
    library_link = contracts.pop("<stdin>:StringUtils")



    library_address = {
        "stringUtils.sol:StringUtils": deploy_contract(library_link)
    }

    main_contract['bin'] = link_code(
        main_contract['bin'], library_address
    )

    # add abi(application binary interface) and transaction reciept in json file
    with open('data.json', 'w') as outfile:
        data = {
        "abi": main_contract['abi'],
        "contract_address": deploy_contract(main_contract)
        }
        json.dump(data, outfile, indent=4, sort_keys=True)


    with open("data.json", 'r') as f:
        datastore = json.load(f)
        abi = datastore["abi"]
        contract_address = datastore["contract_address"]

class ReviewSchema(Schema):
    USER_EMAIL = fields.String(required=True)
    USER_NAME = fields.String(required=True)
    SNACK_ID = fields.String(required=True)
    SNACK_REVIEW = fields.String(required=True)
    SCHEDULE_DATE = fields.String(required=True)
    SNACK_RATING = fields.Int(required=True)
    


def transaction(account_key, USER_EMAIL, USER_NAME, SNACK_ID, SNACK_REVIEW, SCHEDULE_DATE, SNACK_RATING):
    body = {"USER_EMAIL":USER_EMAIL, 'USER_NAME':USER_NAME, 'SNACK_ID':SNACK_ID, 'SNACK_REVIEW':SNACK_REVIEW, 'SCHEDULE_DATE':SCHEDULE_DATE, 'SNACK_RATING':SNACK_RATING}
    w3.eth.defaultAccount = account_key
    with open("data.json", 'r') as f:
        datastore = json.load(f)
    abi = datastore["abi"]
    contract_address = datastore["contract_address"]

    # Create the contract instance with the newly-deployed address
    user = w3.eth.contract(
        address=contract_address, abi=abi,
    )
    #body = request.get_json()
    #result, error = ReviewSchema().load(body)
    result = ReviewSchema().load(body)
    '''
    if error:        
        return jsonify(error), 422
    '''
    tx_hash = user.functions.setReview(
        result['USER_EMAIL'], result['USER_NAME'], result['SNACK_ID'], result['SNACK_REVIEW'], result['SCHEDULE_DATE'], result['SNACK_RATING']
    )
    tx_hash = tx_hash.transact({'from': w3.eth.defaultAccount})
    # Wait for transaction to be mined...
    w3.eth.wait_for_transaction_receipt(tx_hash)
    #user_data = user.functions.getReview().call()
    #print(user_data)

#compile_contract()
#body = {"USER_EMAIL":c, 'USER_NAME':'Angad Singh', 'SNACK_ID':'SNK00010', 'SNACK_REVIEW':'Tasted Amazing!'+str(random.randint(0,100)), 'SNACK_RATING':3}
#transaction("0x92dBF31392EE24731C140098d63f49E2855918d7", 'angadsinghkataria.chd@gmail.com', 'Angad Singh', 'SNK00010', 'Tasted Amazing!'+str(random.randint(0,100)), "2023-06-10", 3)
#tx_dictionary = getSnackReviews("SNK00010")
#print(tx_dictionary)

##############################################################################################################################################################


# Page routes 
# *********************************************#


@app.route('/')
def indexPage():
    if conn:
        mycursor = conn.cursor()
        mycursor.execute("select * from Kitchen order by Kitchen_Ratings desc")
        myresult = mycursor.fetchall()
        l=[]
        for i in range(min(5, len(myresult))):
            kitchen = {
                "Kitchen_ID" : myresult[i][0],
                "Kitchen_Name" : myresult[i][1],
                "Kitchen_Type": myresult[i][2],
                "Kitchen_open_time": myresult[i][3],
                "Kitchen_Close_time": myresult[i][4],
                "Kitchen_Address": myresult[i][5],
                "Kitchen_Ratings" : myresult[i][6],
                "Kitchen_Number": myresult[i][7],
                "Popularity": myresult[i][8],
                "Meal_ID": myresult[i][9],
            }
            l.append(kitchen)
        return render_template('index.html', kitchens=l, session=session)
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/about')
def aboutPage():
    if conn:
        return render_template('about.html', session=session)
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/checkout')
def checkoutPage():
    if conn and "USER_EMAIL" in session:
        return render_template('checkout.html', session=session)
    elif conn:
        return redirect('/sign_in')
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/contact')
def contactPage():
    if conn:
        return render_template('contact.html', session=session)
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")


@app.route('/gallery')
def galleryPage():
    if conn:
        return render_template('gallery.html', session=session)
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")


def GetOrderNowData():
    if conn:
        mycursor = conn.cursor()
        mycursor.execute("Select ORDER_SUMMARY.PRODUCT_ID, ORDER_SUMMARY.PRODUCT_NAME, ORDER_SUMMARY.QUANTITY, ORDER_SUMMARY.PRODUCT_PRICE, ORDER_SUMMARY.PRODUCT_LOGO, ORDER_SUMMARY.Kitchen_ID, ORDER_SUMMARY.SCHEDULE_TIME, ORDER_SUMMARY.TOTAL_AMOUNT, ORDER_SUMMARY.Meal_ID, ORDER_SUMMARY.USER_EMAIL, ORDER_SUMMARY.IS_COMPLETE, Meals.Meal_Timings, Meals.Meal_Type, Kitchen.Kitchen_Name FROM ORDER_SUMMARY LEFT JOIN Kitchen ON ORDER_SUMMARY.Kitchen_ID = Kitchen.Kitchen_ID LEFT JOIN Meals ON ORDER_SUMMARY.Meal_ID = Meals.Meal_ID WHERE ORDER_SUMMARY.USER_EMAIL='"+session['USER_EMAIL']+"' AND ORDER_SUMMARY.IS_COMPLETE=1;")
        myresult = mycursor.fetchall()
        print(myresult)
        GetOrderNowList = []
        RecordCount = len(myresult)
        for i in range(len(myresult)):
            product_review, product_rating = getSnackUserReviews(myresult[i][0], myresult[i][9], myresult[i][6])
            GetOrderNowRecord = {
                    "PRODUCT_ID" : myresult[i][0],
                    "PRODUCT_REVIEW": product_review,
                    "PRODUCT_RATING": product_rating,
                    "PRODUCT_NAME" : myresult[i][1],
                    "QUANTITY": myresult[i][2],
                    "PRODUCT_PRICE": myresult[i][3],
                    "PRODUCT_LOGO": myresult[i][4],
                    "Kitchen_ID": myresult[i][5],
                    "SCHEDULE_TIME": myresult[i][6],
                    "TOTAL_AMOUNT": myresult[i][7],
                    "Meal_ID": myresult[i][8],
                    "USER_EMAIL": myresult[i][9],
                    "IS_COMPLETE": myresult[i][10],
                    "Meal_Timings": myresult[i][11],
                    "Meal_Type": myresult[i][12],
                    "Kitchen_Name" : myresult[i][13]
                }
            getSnacks(GetOrderNowRecord["PRODUCT_ID"], GetOrderNowRecord["PRODUCT_LOGO"])
            GetOrderNowRecord["PRODUCT_LOGO"] = GetOrderNowRecord["PRODUCT_ID"]+".jpg"
            GetOrderNowList.append(GetOrderNowRecord)
        return GetOrderNowList



@app.route('/ordernow')
def ordernowPage():
    if conn and "USER_EMAIL" in session:
        data = GetOrderNowData()
        print(data)
        grouped_data = []
        for key, group in groupby(data, lambda x: x['SCHEDULE_TIME']):
            grouped_data.append(list(group))
        print(len(grouped_data))
        print('grouped_data:'+ str(grouped_data))
        return render_template('ordernow.html', session=session, data=grouped_data)
        
    elif conn:
        return redirect('/sign_in')
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")


@app.route('/reservation')
def reservationPage():
    if conn and "USER_EMAIL" in session:
        return render_template('reservation.html', session=session)
    elif conn:
        return redirect('/sign_in')
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")
    

def GetCart():
    if conn:
        mycursor = conn.cursor()
        mycursor.execute("Select ORDER_SUMMARY.PRODUCT_ID, ORDER_SUMMARY.PRODUCT_NAME, ORDER_SUMMARY.QUANTITY, ORDER_SUMMARY.PRODUCT_PRICE, ORDER_SUMMARY.PRODUCT_LOGO, ORDER_SUMMARY.Kitchen_ID, ORDER_SUMMARY.SCHEDULE_TIME, ORDER_SUMMARY.TOTAL_AMOUNT, ORDER_SUMMARY.Meal_ID, ORDER_SUMMARY.USER_EMAIL, ORDER_SUMMARY.IS_COMPLETE, Meals.Meal_Timings, Meals.Meal_Type, Kitchen.Kitchen_Name FROM ORDER_SUMMARY LEFT JOIN Kitchen ON ORDER_SUMMARY.Kitchen_ID = Kitchen.Kitchen_ID LEFT JOIN Meals ON ORDER_SUMMARY.Meal_ID = Meals.Meal_ID WHERE ORDER_SUMMARY.USER_EMAIL='"+session['USER_EMAIL']+"' AND ORDER_SUMMARY.IS_COMPLETE=0;")
        myresult = mycursor.fetchall()
        #print(myresult)
        ShoppingCartList = []
        RecordCount = len(myresult)
        for i in range(len(myresult)):
            ShoppingCartRecord = {
                    "PRODUCT_ID" : myresult[i][0],
                    "PRODUCT_NAME" : myresult[i][1],
                    "QUANTITY": myresult[i][2],
                    "PRODUCT_PRICE": myresult[i][3],
                    "PRODUCT_LOGO": myresult[i][4],
                    "Kitchen_ID": myresult[i][5],
                    "SCHEDULE_TIME": myresult[i][6],
                    "TOTAL_AMOUNT": myresult[i][7],
                    "Meal_ID": myresult[i][8],
                    "USER_EMAIL": myresult[i][9],
                    "IS_COMPLETE": myresult[i][10],
                    "Meal_Timings": myresult[i][11],
                    "Meal_Type": myresult[i][12],
                    "Kitchen_Name" : myresult[i][13]
                }
            getSnacks(ShoppingCartRecord["PRODUCT_ID"], ShoppingCartRecord["PRODUCT_LOGO"])
            ShoppingCartRecord["PRODUCT_LOGO"] = ShoppingCartRecord["PRODUCT_ID"]+".jpg"
            ShoppingCartList.append(ShoppingCartRecord)
        return ShoppingCartList


@app.route('/shopping_cart')
def shopping_cartPage():
    if conn and "USER_EMAIL" in session:
        data = GetCart()
        return render_template('shopping-cart.html', session=session, data=data)
    elif conn:
        return redirect('/sign_in')
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/sign_in', methods=['GET', 'POST'])
def sign_inPage():
    if conn and "USER_EMAIL" in session:
        redirect('/')
    elif conn:
        return render_template('sign_in.html')
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/snacks')
def snacksPage():
    if conn:
        mycursor = conn.cursor()
        mycursor.execute("select * from Kitchen order by Kitchen_Ratings desc")
        myresult = mycursor.fetchall()
        l=[]
        for i in range(len(myresult)):
            kitchen = {
                "Kitchen_ID" : myresult[i][0],
                "Kitchen_Name" : myresult[i][1],
                "Kitchen_Type": myresult[i][2],
                "Kitchen_open_time": myresult[i][3],
                "Kitchen_Close_time": myresult[i][4],
                "Kitchen_Address": myresult[i][5],
                "Kitchen_Ratings" : myresult[i][6],
                "Kitchen_Number": myresult[i][7],
                "Popularity": myresult[i][8],
                "Meal_ID": myresult[i][9],
            }
            l.append(kitchen)
        return render_template('snacks.html', kitchens=l, kitchen_name="Snacks", snack=[], session=session)
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/snacks/<string:Kitchen_ID>')
def snacksPageDynamic(Kitchen_ID):
    if conn and "USER_EMAIL" in session:
        mycursor = conn.cursor()
        mycursor.execute("select SNACK.SNACK_ID, SNACK.SNACK_NAME, SNACK.SNACK_PRICE, SNACK.Kitchen_ID, Kitchen.Kitchen_Name, SNACK.Meal_ID, SNACK.SNACK_LOGO, Meals.Meal_Type, Meals.Meal_Timings FROM SNACK  LEFT JOIN Kitchen ON SNACK.Kitchen_ID = Kitchen.Kitchen_ID LEFT JOIN Meals ON SNACK.Meal_ID = Meals.Meal_ID WHERE Kitchen.Kitchen_ID='"+Kitchen_ID+"'")
        myresult = mycursor.fetchall()
        l = []
        kitchen_name=""
        for i in range(len(myresult)):
            print(myresult[i][8])
            snack = {
                "SNACK_ID" : myresult[i][0],
                "SNACK_NAME" : myresult[i][1],
                "SNACK_PRICE": myresult[i][2],
                "Kitchen_ID": myresult[i][3],
                "Kitchen_Name": myresult[i][4],
                "Meal_ID": myresult[i][5],
                "Meal_Type" : myresult[i][7],
                "Meal_Timings": myresult[i][8]
            }

            snack_reviews = getSnackReviews(myresult[i][0])

            snack["SNACK_REVIEWS"] = snack_reviews 
            #start_time,end_time = snack["Meal_Timings"].split("-")
            #start_time=time.strptime(start_time, "%H:%M")
            #end_time=time.strptime(end_time, "%H:%M")
            #current_time=time.strptime(time.strftime("%H:%M",time.localtime()), "%H:%M")
            
            #if start_time<=current_time and current_time<=end_time:
            getSnacks(snack["SNACK_ID"], myresult[i][6])
            snack["SNACK_LOGO_FILE"] = snack["SNACK_ID"]+".jpg"
            #print(snack["SNACK_ID"])
            l.append(snack)
            kitchen_name=myresult[i][4]
        #print(l)
        return render_template('snacks.html', snack=l, kitchen_name=kitchen_name, kitchens=[], session=session)
    elif conn:
        return redirect('/sign_in')
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")


@app.route('/admin_home')
def admin_homePage():
    if conn:
        return render_template('admin_home.html', session=session)
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/admin_users')
def admin_usersPage():
    if conn:
        return render_template('admin_users.html', session=session)
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/admin_kitchens')
def admin_kitchensPage():
    if conn:
        return render_template('admin_kitchens.html', session=session)
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/admin_delivery_partners')
def admin_delivery_partnersPage():
    if conn:
        return render_template('admin_delivery_partner.html', session=session)
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")

# *********************************************#
# APIs routes
# *********************************************#
@app.route('/CheckServer')
def CheckServer():
    if conn:
        return jsonify(StatusCode = '1', Message="Connected!")
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/getUsers',methods = ['GET'])
def getUsers():
  if request.method == 'GET':
     if conn:
        mycursor = conn.cursor()
        mycursor.execute("SELECT * FROM USERS")
        myresult = mycursor.fetchall()
        print(myresult)
        Users = myresult
        return jsonify(Users = Users)
     
'''
@app.route('/getSnacks',methods = ['GET'])
def getSnacks():
  if request.method == 'GET':
     if conn:
        mycursor = conn.cursor()
        mycursor.execute("SELECT * FROM SNACK")
        myresult = mycursor.fetchall()
        image_data = myresult[0][3]
        # Convert image data to image object
        image = Image.open(BytesIO(image_data))

        # Display image using matplotlib
        plt.imshow(image)
        plt.show()
        return jsonify(myresult=myresult)
'''

@app.route('/updatecartcount', methods = ['GET'])
def update_cart_count():
    if "USER_EMAIL" in session:
        mycursor = conn.cursor()
        mycursor.execute('SELECT COUNT(*) FROM ORDER_SUMMARY WHERE USER_EMAIL="'+session["USER_EMAIL"]+'" AND IS_COMPLETE=0')
        myresult = mycursor.fetchall()
        session['CART_COUNT'] = myresult[0][0]


# @app.route('/getSnacks',methods = ['GET'])
def getSnacks(image_name, image_data):
    try:
        with open('./static/images/'+image_name+'.jpg', 'wb') as file:
            file.write(image_data)
        # image = Image.open(BytesIO(image_data))
        # plt.savefig('./static/images/' + image_name+'.jpg')
    except Exception as e:
        print('Error: '+ str(e))

@app.route('/UsersAuthentication',methods = ['POST'])
def UsersAuthentication():
    if request.method == 'POST':
        req = request.get_json()
        print(req)
    try:
        if conn:
            mycursor = conn.cursor()
            sql = "INSERT IGNORE INTO USERS VALUES (%s, %s, %s, '', '', '', '', '', %s);"
            val = (req['USER_EMAIL'].split("@")[0], req["USER_PASSWORD"], req['USER_EMAIL'], w3.eth.accounts[random.randint(0,9)])
            mycursor.execute(sql, val)
            conn.commit()
            
            session['USER_EMAIL'] = req['USER_EMAIL']
            session['USER_NAME'] = req['USER_EMAIL'].split("@")[0]


            mycursor = conn.cursor()
            mycursor.execute('SELECT * FROM USERS WHERE USER_EMAIL="'+req["USER_EMAIL"]+'"')
            myresult = mycursor.fetchall()
            print(myresult)
            if len(myresult) == 0:
                return jsonify(StatusCode = '0',ErrorMessage='Invalid User email')
            user_record = {
                "USER_NAME" : myresult[0][0],
                "USER_PASSWORD" : myresult[0][1],
                "USER_EMAIL" : myresult[0][2],
                "USER_STREET" : myresult[0][3],
                "USER_STATE" : myresult[0][4],
                "USER_CITY" : myresult[0][5],
                "USER_PINCODE" : myresult[0][6],
                "USER_MOBILE" : myresult[0][7],
            }
            session['USER_PASSWORD'] = myresult[0][1]
            session['USER_STREET'] = myresult[0][3]
            session['USER_STATE'] = myresult[0][4]
            session['USER_CITY'] = myresult[0][5]
            session['USER_PINCODE'] = myresult[0][6]
            session['USER_MOBILE'] = myresult[0][7]
            session['USER_PRIVATE_KEY'] = myresult[0][8]

            mycursor = conn.cursor()
            mycursor.execute('SELECT COUNT(*) FROM ORDER_SUMMARY WHERE USER_EMAIL="'+session["USER_EMAIL"]+'" AND IS_COMPLETE=0')
            myresult = mycursor.fetchall()
            session['CART_COUNT'] = myresult[0][0]

            return jsonify(StatusCode = '1', UserRecord=user_record)
    except Exception as e:
        return str(e)

@app.route('/ReviewSubmit',methods = ['POST'])
def ReviewSubmit():
    if request.method == 'POST':
        req = request.get_json()
        print(req)
        transaction(session['USER_PRIVATE_KEY'], session['USER_EMAIL'], session['USER_NAME'], req['SNACK_ID'], req['SNACK_REVIEW'], req['SCHEDULE_TIME'], int(req['SNACK_RATING']))
        return jsonify(StatusCode = '1', Message="Review Saved!")


@app.route('/logout',methods = ['GET']) 
def logout():
    session.pop("USER_NAME")
    session.pop("USER_PASSWORD")
    session.pop("USER_EMAIL")
    session.pop("USER_STREET")
    session.pop("USER_STATE")
    session.pop("USER_CITY")
    session.pop("USER_PINCODE")
    session.pop("USER_MOBILE")
    session.pop("USER_PRIVATE_KEY")
    return redirect('/')


@app.route('/getKitchens',methods = ['GET'])
def getKitchens():
    if request.method == 'GET':
        try:
            if conn:
                mycursor = conn.cursor()
                mycursor.execute('select * from Kitchen;')
                myresult = mycursor.fetchall()
                print(myresult)
                KitchensList = []
                RecordCount = len(myresult)
                for i in range(len(myresult)):
                    KitchenRecord = {
                        "Kitchen_ID" : myresult[i][0],
                        "Kitchen_Name" : myresult[i][1],
                        "Kitchen_Type" : myresult[i][2],
                        "Kitchen_open_time" : myresult[i][3],
                        "Kitchen_Close_time": myresult[i][4],
                        "Kitchen_Address" : myresult[i][5],
                        "Kitchen_Ratings" : myresult[i][6],
                        "Kitchen_Number" : myresult[i][7],
                        "Popularity" : myresult[i][8],
                        "Meal_ID" : myresult[i][9],
                    }
                    KitchensList.append(KitchenRecord)
                
                return jsonify(StatusCode = '1', Total = RecordCount,  get_kitchens=KitchensList)
        except Exception as e:
            return str(e)

@app.route('/showMyLunchBoxOrders',methods = ['POST'])
def showMyLunchBoxOrders():
    if request.method == 'POST':
        req = request.get_json()
        print(req)
        try:
            if conn:
                mycursor = conn.cursor()
                mycursor.execute("select Lunch_Box_Order.Lunch_Box_Order_ID, Lunch_Box_Order.Lunch_Box_Type, Lunch_Box_Order.Lunch_Box_Size, Lunch_Box_Order.Lunch_Box_color_pref, Payment.Payment_type, Payment.Payment_Amt, Payment.Payment_Status, Kitchen.Kitchen_ID, Kitchen.Kitchen_Name, Delivery_Management.Delivery_Timings, Delivery_Management.Door_Step_Delivery FROM Lunch_Box_Order LEFT JOIN Kitchen ON Lunch_Box_Order.Kitchen_ID = Kitchen.Kitchen_ID LEFT JOIN Payment ON Lunch_Box_Order.Payment_ID = Payment.Payment_ID LEFT JOIN Delivery_Management ON Lunch_Box_Order.Delivery_ID = Delivery_Management.Delivery_ID Where Lunch_Box_Order.User_EMAIL='"+session('USER_EMAIL')+"'")
                myresult = mycursor.fetchall()
                print(myresult)
                LunchBoxOrdersList = []
                RecordCount = len(myresult)
                for i in range(len(myresult)):
                    LunchBoxOrdersRecord = {
                        "Lunch_Box_Order_ID" : myresult[i][0],
                        "Lunch_Box_Type" : myresult[i][1],
                        "Lunch_Box_Size": myresult[i][2],
                        "Lunch_Box_color_pref": myresult[i][3],
                        "Payment_type": myresult[i][4],
                        "Payment_Amt": myresult[i][5],
                        "Payment_Status": myresult[i][6],
                        "Kitchen_ID": myresult[i][7],
                        "Kitchen_Name": myresult[i][8],
                        "Delivery_Timings": myresult[i][9],
                        "Door_Step_Delivery" : myresult[i][10]
                    }
                    LunchBoxOrdersList.append(LunchBoxOrdersRecord)
                return jsonify(StatusCode = '1', Total = RecordCount, LunchBoxOrdersList=LunchBoxOrdersList)
        except Exception as e:
            return str(e)


@app.route('/Shoping_cart',methods = ['GET', 'POST'])
def Shoping_cart():
        if request.method == 'GET':
            try:
                if conn:
                    mycursor = conn.cursor()
                    mycursor.execute("Select ORDER_SUMMARY.PRODUCT_ID, ORDER_SUMMARY.PRODUCT_NAME, ORDER_SUMMARY.QUANTITY, ORDER_SUMMARY.PRODUCT_PRICE, ORDER_SUMMARY.PRODUCT_LOGO, ORDER_SUMMARY.Kitchen_ID, ORDER_SUMMARY.SCHEDULE_TIME, ORDER_SUMMARY.TOTAL_AMOUNT, ORDER_SUMMARY.Meal_ID, ORDER_SUMMARY.USER_EMAIL, ORDER_SUMMARY.IS_COMPLETE, Meals.Meal_Timings, Meals.Meal_Type, Kitchen.Kitchen_Name FROM ORDER_SUMMARY LEFT JOIN Kitchen ON ORDER_SUMMARY.Kitchen_ID = Kitchen.Kitchen_ID LEFT JOIN Meals ON ORDER_SUMMARY.Meal_ID = Meals.Meal_ID WHERE ORDER_SUMMARY.USER_EMAIL='"+session['USER_EMAIL']+"' AND ORDER_SUMMARY.IS_COMPLETE=0;")
                    myresult = mycursor.fetchall()
                    print(myresult)
                    ShoppingCartList = []
                    RecordCount = len(myresult)
                    for i in range(len(myresult)):
                        ShoppingCartRecord = {
                            "PRODUCT_ID" : myresult[i][0],
                            "PRODUCT_NAME" : myresult[i][1],
                            "QUANTITY": myresult[i][2],
                            "PRODUCT_PRICE": myresult[i][3],
                            "PRODUCT_LOGO": myresult[i][4],
                            "Kitchen_ID": myresult[i][5],
                            "SCHEDULE_TIME": myresult[i][6],
                            "TOTAL_AMOUNT": myresult[i][7],
                            "Meal_ID": myresult[i][8],
                            "USER_EMAIL": myresult[i][9],
                            "IS_COMPLETE": myresult[i][10],
                            "Meal_Timings": myresult[i][11],
                            "Meal_Type": myresult[i][12],
                            "Kitchen_Name" : myresult[i][13],
                            "PAYMENT_ID": myresult[i][14]
                        }
                        getSnacks(ShoppingCartRecord["PRODUCT_ID"], ShoppingCartRecord["PRODUCT_LOGO"])
                        ShoppingCartRecord["PRODUCT_LOGO"] = ShoppingCartRecord["PRODUCT_ID"]+".jpg"
                        ShoppingCartList.append(ShoppingCartRecord)
                    return jsonify(StatusCode = '1', Total = RecordCount, ShoppingCartList=ShoppingCartList)
            except Exception as e:
                return str(e)
        
        
        if request.method == 'POST':
            try:
                if conn:
                    request_json = request.get_json()
                    snack_id = request_json.get("SNACK_ID")
                    #print(snack_id)
                    mycursor = conn.cursor()
                    sql = "INSERT INTO ORDER_SUMMARY SELECT SNACK_ID, SNACK_NAME, SNACK_PRICE, SNACK_LOGO, Kitchen_ID, %s, SNACK_PRICE, 1, Meal_ID,%s, %s, %s FROM SNACK WHERE SNACK_ID=%s AND NOT EXISTS(SELECT NULL FROM ORDER_SUMMARY WHERE PRODUCT_ID=%s AND USER_EMAIL=%s AND IS_COMPLETE=0)"
                    val = (datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), session['USER_EMAIL'],'', 0, snack_id, snack_id, session['USER_EMAIL'])
                    mycursor.execute(sql, val)
                    conn.commit()
                    session["CART_COUNT"]+=1
                    return jsonify(StatusCode = '1', Total = mycursor.rowcount)
            except Exception as e:
                return str(e)
            

@app.route('/UpdateOrderHistory',methods = ['GET', 'POST'])
def UpdateOrderHistory(): 
    if request.method == 'POST':
        try:
            if conn:
                mycursor = conn.cursor()
                request_json = request.get_json()
                PAYMENT_ID = request_json['PAYMENT_ID']
                IS_COMPLETE = request_json['IS_COMPLETE']
                PRODUCT_LIST = request_json['PRODUCT_LIST']
                print(PRODUCT_LIST)
                for i in PRODUCT_LIST:
                    sql = "UPDATE ORDER_SUMMARY SET QUANTITY = %s, TOTAL_AMOUNT = %s, SCHEDULE_TIME = %s, PAYMENT_ID = %s, IS_COMPLETE = %s WHERE PRODUCT_ID = %s AND USER_EMAIL=%s AND PAYMENT_ID=%s"
                    val = (i['QUANTITY'], i['TOTAL_AMOUNT'], i['SCHEDULE_TIME'], PAYMENT_ID, IS_COMPLETE,  i['PRODUCT_ID'], session['USER_EMAIL'], '')
                    mycursor.execute(sql, val)
                    conn.commit()
                update_cart_count()
                return jsonify({'success': True})
        except Exception as e:
            print(str(e))
            return jsonify({'success': False})
        
            


@app.route('/deleteCartRow',methods = ['POST'])
def deleteCartRow():
    if request.method == 'POST':
        try:
            if conn:
                request_json = request.get_json()
                PRODUCT_ID = request_json.get("PRODUCT_ID")
                print("PRODUCT_ID: ", PRODUCT_ID)
                mycursor = conn.cursor()
                mycursor.execute("DELETE FROM ORDER_SUMMARY WHERE PRODUCT_ID='"+PRODUCT_ID+"' AND USER_EMAIL='"+session['USER_EMAIL']+"'")
                conn.commit()
                return 'Row Deleted!'
        except Exception as e:
                return str(e)

if __name__ == '__main__':
  
    app.run(debug = True)