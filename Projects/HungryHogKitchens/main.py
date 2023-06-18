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

#os.environ['CURL_CA_BUNDLE'] = ''

from transformers import FlaxAutoModelForSeq2SeqLM
from transformers import AutoTokenizer
from diffusers import StableDiffusionPipeline
import torch

from geopy.geocoders import Nominatim
from geopy.distance import great_circle
 
import hashlib



##############################################################################################################################################################
####### DECLARATIONS ########
##############################################################################################################################################################



app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

oauth = OAuth(app)
app.secret_key="HungryHogKitchensOinkOink"
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



# Creating connection object
conn = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "pass@123",
    database = "tiffin_service"
)

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
account_key = w3.eth.accounts[1]

geolocator = Nominatim(user_agent="HungryHogKitchens")
proximity_km = 15
minimum_proximity = 5



##############################################################################################################################################################
####### Utility ########
##############################################################################################################################################################



def convertToBinaryData(filename):
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

def getSnacks(image_name, image_data):
    try:
        with open('./static/images/'+image_name+'.jpg', 'wb') as file:
            file.write(image_data)
        # image = Image.open(BytesIO(image_data))
        # plt.savefig('./static/images/' + image_name+'.jpg')
    except Exception as e:
        print('Error: '+ str(e))

def getMealData():
    mycursor = conn.cursor()
    mycursor.execute("SELECT * FROM Meals")
    myresult = mycursor.fetchall()
    #print(myresult)
    mycursor.close()
    result = []
    for i in range(len(myresult)):
        meal = {
            "Meal_ID": myresult[i][0],
            "Meal_Type": myresult[i][1],
            "Meal_Timings": myresult[i][2],
        }
        result.append(meal)
    return result

def getSnackData():
    mycursor = conn.cursor()
    sql = "SELECT SNACK.SNACK_ID, SNACK.SNACK_NAME, SNACK.SNACK_PRICE, SNACK.Kitchen_ID, SNACK.Meal_ID, Meals.Meal_Type, Meals.Meal_Timings, SNACK.SNACK_LOGO, SNACK.SNACK_REVIEW_COUNT, SNACK.SNACK_REVIEW_TOTAL, SNACK.SNACK_RATING FROM SNACK LEFT JOIN Meals ON SNACK.Meal_ID = Meals.Meal_ID WHERE SNACK.Kitchen_ID=%s"
    val = (session['Kitchen_ID'], )
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    #print(myresult)
    mycursor.close()
    result = []
    for i in range(len(myresult)):
        snack = {
            "SNACK_ID": myresult[i][0],
            "SNACK_NAME": myresult[i][1],
            "SNACK_PRICE": myresult[i][2],
            "Kitchen_ID": myresult[i][3],
            "Meal_ID": myresult[i][4],
            "Meal_Type": myresult[i][5],
            "Meal_Timings": myresult[i][6],
            "SNACK_LOGO": myresult[i][7],
            "SNACK_REVIEW_COUNT": myresult[i][8],
            "SNACK_REVIEW_TOTAL": myresult[i][9],
            "SNACK_RATING": myresult[i][10],
        }

        getSnacks(snack["SNACK_ID"], snack["SNACK_LOGO"])
        snack["SNACK_LOGO"] = snack["SNACK_ID"]+".jpg"
        result.append(snack)
    return result



##############################################################################################################################################################
####### GeoPy ########
##############################################################################################################################################################



def getCoordinates(address):
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    else:
        return (200, 200)

def getLocationDetails(latitiude, longitutde):
    Latitude = str(latitiude)
    Longitude = str(longitutde)
    
    location = geolocator.reverse(Latitude+","+Longitude)
    
    address = location.raw['address']
    
    street = address.get('suburb', '')
    city = address.get('city', '')
    state = address.get('state', '')
    country = address.get('country', '')
    code = address.get('country_code')
    zipcode = address.get('postcode', '')
    return (street, city, state, country, zipcode)

def getPointDistance(l1, l2):
    #print(l1,l2)
    return great_circle(l1, l2).km



##############################################################################################################################################################
####### OAUTH ########
##############################################################################################################################################################



#GOOGLE
@app.route('/google/')
def google():
        
    redirect_uri = url_for('google_auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)
 
@app.route('/google/auth/')
def google_auth():
    token = oauth.google.authorize_access_token()
    #user = oauth.google.parse_id_token(token)
    session['Kitchen_Email'] = token['userinfo']['email']
    session['Kitchen_Name'] = token['userinfo']['name']
    session['Kitchen_Password'] = hashlib.sha512((session['Kitchen_Email']+session['Kitchen_Name']).encode()).hexdigest()
    session['Kitchen_ID'] = hashlib.sha512((session['Kitchen_Email']+session['Kitchen_Password']).encode()).hexdigest()

    mycursor = conn.cursor()
    sql = "INSERT IGNORE INTO Kitchen VALUES (%s, %s, %s, %s, '', '', '', '', '', '', '', '', 0, '' 0, 200, 200, 0, 0, %s);"
    val = (session['Kitchen_Name'], session['Kitchen_Email'], session['Kitchen_ID'], session['Kitchen_Password'], w3.eth.accounts[random.randint(0,9)])
    mycursor.execute(sql, val)
    conn.commit()
    mycursor.close()
    
    mycursor = conn.cursor()
    mycursor.execute('SELECT * FROM Kitchen WHERE Kitchen_ID="'+session["Kitchen_ID"]+'"')
    myresult = mycursor.fetchall()
    mycursor.close()
    #print(myresult)
    session['Kitchen_Type'] = myresult[0][4]
    session['Kitchen_Open_Time'] = myresult[0][5]
    session['Kitchen_Close_Time'] = myresult[0][6]
    session['Kitchen_Address'] = myresult[0][7]
    session['Kitchen_City'] = myresult[0][8]
    session['Kitchen_State'] = myresult[0][9]
    session['Kitchen_Country'] = myresult[0][10]
    session['Kitchen_Pincode'] = myresult[0][11]
    session['Kitchen_Ratings'] = myresult[0][12]
    session['Kitchen_Number'] = myresult[0][13]
    session['Popularity'] = myresult[0][14]
    session['Kitchen_Latitude'] = myresult[0][15]
    session['Kitchen_Longitude'] = myresult[0][16]
    session['Kitchen_Review_Count'] = myresult[0][17]
    session['Kitchen_Review_Total'] = myresult[0][18]
    session['Kitchen_Private_Key'] = myresult[0][19]

    #print(" Google User ", token)
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
    #print("Facebook User ", profile)
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
####### ETHEREUM ########
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
# PAGE ROUTES 
##############################################################################################################################################################



@app.route('/')
def indexPage():
    try:
        return render_template('index.html', session=session)
    except Exception as e:
        print(str(e))
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/sign_in', methods=['GET', 'POST'])
def sign_inPage():
    try:
        if "Kitchen_ID" in session:
            return redirect('/')
        else:
            return render_template('sign_in.html')
    except Exception as e:
        print(str(e))
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/about')
def aboutPage():
    try:
        return render_template('about.html', session=session)
    except Exception as e:
        print(str(e))
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/profile')
def profilePage():
    try:
        if "Kitchen_ID" in session:
            return render_template('profile.html', session=session)
        else:
            return redirect('/sign_in')
    except Exception as e:
        print(str(e))
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/menu')
def menuPage():
    try:
        if "Kitchen_ID" in session:
            return render_template('menu.html', session=session, data=getSnackData(), meals=getMealData())
        else:
            return redirect('/sign_in')
    except Exception as e:
        print(str(e))
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/gallery')
def galleryPage():
    try:
        return render_template('gallery.html', session=session)
    except Exception as e:
        print(str(e))
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/contact')
def contactPage():
    try:
        return render_template('contact.html', session=session)
    except Exception as e:
        print(str(e))
        return jsonify(StatusCode = '0', Message="Connection Failed!")



##############################################################################################################################################################
# API ROUTES 
##############################################################################################################################################################



@app.route('/UsersAuthentication',methods = ['POST'])
def UsersAuthentication():
    if request.method == 'POST':
        req = request.get_json()
    try:
        if conn:
            mycursor = conn.cursor()

            Kitchen_ID = hashlib.sha512((req['Kitchen_Email']+req['Kitchen_Email'].split("@")[0]).encode()).hexdigest()
            session["Kitchen_ID"] = Kitchen_ID
            session["Kitchen_Password"] = req["Kitchen_Password"]
            street,city,state,country,zipcode=getLocationDetails(req['Kitchen_Latitude'], req['Kitchen_Longitude'])
            sql = "INSERT IGNORE INTO Kitchen VALUES (%s, %s, %s, %s, '', '', '', %s, %s, %s, %s, %s, 0, '', 0, %s, %s, 0, 0, %s);"
            val = (Kitchen_ID, req['Kitchen_Email'], req['Kitchen_Email'].split("@")[0], req["Kitchen_Password"], street, city, state, country, zipcode, req['Kitchen_Latitude'], req['Kitchen_Longitude'], w3.eth.accounts[random.randint(0,9)])
            mycursor.execute(sql, val)
            conn.commit()
            mycursor.close()
            
            session['Kitchen_Email'] = req['Kitchen_Email']
            session['Kitchen_Name'] = req['Kitchen_Email'].split("@")[0]

            mycursor = conn.cursor()
            mycursor.execute('SELECT * FROM Kitchen WHERE Kitchen_ID="'+session["Kitchen_ID"]+'"')
            myresult = mycursor.fetchall()
            mycursor.close()

            if len(myresult) == 0:
                return jsonify(StatusCode = '0',ErrorMessage='Invalid User email')

            session['Kitchen_Name'] = myresult[0][2]
            session['Kitchen_Type'] = myresult[0][4]
            session['Kitchen_Open_Time'] = myresult[0][5]
            session['Kitchen_Close_Time'] = myresult[0][6]
            session['Kitchen_Address'] = myresult[0][7]
            session['Kitchen_City'] = myresult[0][8]
            session['Kitchen_State'] = myresult[0][9]
            session['Kitchen_Country'] = myresult[0][10]
            session['Kitchen_Pincode'] = myresult[0][11]
            session['Kitchen_Ratings'] = myresult[0][12]
            session['Kitchen_Number'] = myresult[0][13]
            session['Popularity'] = myresult[0][14]
            session['Kitchen_Latitude'] = myresult[0][15]
            session['Kitchen_Longitude'] = myresult[0][16]
            session['Kitchen_Review_Count'] = myresult[0][17]
            session['Kitchen_Review_Total'] = myresult[0][18]
            session['Kitchen_Private_Key'] = myresult[0][19]

            return jsonify(StatusCode = '1', Message="Success")
    except Exception as e:
        print(str(e))
        return jsonify(StatusCode = '0', Message="Error")


@app.route('/updateUserCoordinates',methods = ['POST'])
def updateUserCoordinates():
    if request.method == "POST":
        try:
            if conn and "Kitchen_ID" in session:
                request_json = request.get_json()
                if session['Kitchen_Latitude'] != 200:
                    if getPointDistance((session['Kitchen_Latitude'], session['Kitchen_Longitude']), (request_json['Kitchen_Latitude'], request_json['Kitchen_Longitude'])) < minimum_proximity:
                        return jsonify(StatusCode = '0', Message="Within proximity") 
                mycursor = conn.cursor()
                street,city,state,country,zipcode=getLocationDetails(request_json['Kitchen_Latitude'], request_json['Kitchen_Longitude'])
                #print(request_json,street,city,state,country,zipcode)
                if request_json['Kitchen_Request'] == 1:
                    sql = "UPDATE USERS SET Kitchen_Latitude=%s, Kitchen_Longitude=%s, Kitchen_Address=%s, Kitchen_City=%s, Kitchen_State=%s, Kitchen_Country=%s, Kitchen_Pincode=%s WHERE Kitchen_ID=%s AND Kitchen_Latitude=200"
                    if session['Kitchen_Latitude'] == 200:
                        session['Kitchen_Latitude'] = request_json['Kitchen_Latitude']
                        session['Kitchen_Longitude'] = request_json['Kitchen_Longitude']
                        session['Kitchen_Address'] = street
                        session['Kitchen_City'] = city
                        session['Kitchen_State'] = state
                        session['Kitchen_Country'] = country
                        session['Kitchen_Pincode'] = zipcode
                else:
                    sql = "UPDATE USERS SET Kitchen_Latitude=%s, Kitchen_Longitude=%s, Kitchen_Address=%s, Kitchen_City=%s, Kitchen_State=%s, Kitchen_Country=%s, Kitchen_Pincode=%s WHERE Kitchen_ID=%s"
                    session['Kitchen_Latitude'] = request_json['Kitchen_Latitude']
                    session['Kitchen_Longitude'] = request_json['Kitchen_Longitude']
                    session['Kitchen_Address'] = street
                    session['Kitchen_City'] = city
                    session['Kitchen_State'] = state
                    session['Kitchen_Country'] = country
                    session['Kitchen_Pincode'] = zipcode
                val = (request_json['Kitchen_Latitude'], request_json['Kitchen_Longitude'], street, city, state, country, zipcode, session['Kitchen_ID'])
                mycursor.execute(sql, val)
                conn.commit()
                mycursor.close()
                return jsonify(StatusCode = '1', Message="Location Updated!") 
            return jsonify(StatusCode = '0', Message="Error") 
        except Exception as e:
            print(str(e))
            return jsonify(StatusCode = '0', Message="Error")  

@app.route('/updateProfile',methods = ['POST'])
def updateProfile():
    if request.method == "POST":
        try:
            if conn and "Kitchen_ID" in session:
                request_json = request.get_json()
                latitude, longitude = getCoordinates(request_json['Kitchen_Address']+", "+request_json['Kitchen_City']+", "+request_json['Kitchen_State']+", "+request_json['Kitchen_Country']+", "+request_json['Kitchen_Pincode'])
                #print(latitude, longitude, request_json)

                mycursor = conn.cursor()
                sql = "UPDATE Kitchen SET Kitchen_Latitude=%s, Kitchen_Longitude=%s, Kitchen_Address=%s, Kitchen_City=%s, Kitchen_State=%s, Kitchen_Country=%s, Kitchen_Pincode=%s, Kitchen_Number=%s, Kitchen_Type=%s, Kitchen_Open_Time=%s, Kitchen_Close_Time=%s WHERE Kitchen_ID=%s"
                if latitude != 200:
                    val = (latitude, longitude, request_json['Kitchen_Address'], request_json['Kitchen_City'], request_json['Kitchen_State'], request_json['Kitchen_Country'], request_json['Kitchen_Pincode'], request_json['Kitchen_Number'], request_json['Kitchen_Type'], request_json['Kitchen_Open_Time'], request_json['Kitchen_Close_Time'], session['Kitchen_ID'])
                    session['Kitchen_Latitude'] = latitude
                    session['Kitchen_Longitude'] = longitude
                else:
                    val = (session['Kitchen_Latitude'], session['Kitchen_Longitude'], request_json['Kitchen_Address'], request_json['Kitchen_City'], request_json['Kitchen_State'], request_json['Kitchen_Country'], request_json['Kitchen_Pincode'], request_json['Kitchen_Number'], request_json['Kitchen_Type'], request_json['Kitchen_Open_Time'], request_json['Kitchen_Close_Time'], session['Kitchen_ID'])
                    session['Kitchen_Latitude'] = session['Kitchen_Latitude']
                    session['Kitchen_Longitude'] = session['Kitchen_Longitude']
                session['Kitchen_Address'] = request_json['Kitchen_Address']
                session['Kitchen_City'] = request_json['Kitchen_City']
                session['Kitchen_State'] = request_json['Kitchen_State']
                session['Kitchen_Country'] = request_json['Kitchen_Country']
                session['Kitchen_Pincode'] = request_json['Kitchen_Pincode']
                session['Kitchen_Number'] = request_json['Kitchen_Number']
                session['Kitchen_Type'] = request_json['Kitchen_Type']
                session['Kitchen_Open_Time'] = request_json['Kitchen_Open_Time']
                session['Kitchen_Close_Time'] = request_json['Kitchen_Close_Time']
                mycursor.execute(sql, val)
                conn.commit()
                mycursor.close()
                return jsonify(StatusCode = '1', Message="Success")
        except Exception as e:
            print(str(e))
            return jsonify(StatusCode = '0', Message="Error")


@app.route('/logout',methods = ['GET']) 
def logout():
    session.pop("Kitchen_ID")
    session.pop("Kitchen_Email")
    session.pop("Kitchen_Name")
    session.pop("Kitchen_Password")
    session.pop("Kitchen_Type")
    session.pop("Kitchen_Open_Time")
    session.pop("Kitchen_Close_Time")
    session.pop("Kitchen_Address")
    session.pop("Kitchen_City")
    session.pop("Kitchen_State")
    session.pop("Kitchen_Country")
    session.pop("Kitchen_Pincode")
    session.pop("Kitchen_Ratings")
    session.pop("Kitchen_Number")
    session.pop("Popularity")
    session.pop("Kitchen_Latitude")
    session.pop("Kitchen_Longitude")
    session.pop("Kitchen_Review_Count")
    session.pop("Kitchen_Review_Total")
    session.pop("Kitchen_Private_Key")

    return redirect('/')


if __name__ == '__main__':
    app.run(debug = False, port=5001)