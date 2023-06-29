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
import base64



##############################################################################################################################################################
####### DECLARATIONS ########
##############################################################################################################################################################



app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

oauth = OAuth(app)
app.secret_key="HungryHogDeliveryOinkOink"
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

geolocator = Nominatim(user_agent="HungryHogDelivery")
proximity_km = 15
minimum_proximity = 5



##############################################################################################################################################################
####### Utility ########
##############################################################################################################################################################



def convertToBinaryData(filename):
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData



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
    session['Delivery_Partner_Email'] = token['userinfo']['email']
    session['Delivery_Partner_Name'] = token['userinfo']['name']
    session['Delivery_Partner_Password'] = hashlib.sha512((session['Delivery_Partner_Email']+session['Delivery_Partner_Name']).encode()).hexdigest()
    session['Delivery_Partner_ID'] = hashlib.sha512((session['Delivery_Partner_Email']+session['Delivery_Partner_Password']).encode()).hexdigest()

    mycursor = conn.cursor(buffered=True)
    sql = "INSERT IGNORE INTO Delivery_Partner VALUES (%s, %s, %s, %s, '', 200, 200, 0, %s)"
    val = (session['Delivery_Partner_ID'], session['Delivery_Partner_Name'], session['Delivery_Partner_Email'], session['Delivery_Partner_Password'], w3.eth.accounts[random.randint(0,9)])
    mycursor.execute(sql, val)
    conn.commit()
    mycursor.close()
    
    mycursor = conn.cursor(buffered=True)
    mycursor.execute('SELECT * FROM Kitchen WHERE Delivery_Partner_ID="'+session["Delivery_Partner_ID"]+'"')
    myresult = mycursor.fetchall()
    mycursor.close()
    #print(myresult)
    session['Delivery_Partner_Number'] = myresult[0][4]
    session['Delivery_Partner_Latitude'] = myresult[0][5]
    session['Delivery_Partner_Longitude'] = myresult[0][6]
    session['Delivery_Partner_Ratings'] = myresult[0][7]
    session['Delivery_Partner_Private_Key'] = myresult[0][8]

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
        if "Delivery_Partner_ID" in session:
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
        if "Delivery_Partner_ID" in session:
            return render_template('profile.html', session=session)
        else:
            return redirect('/sign_in')
    except Exception as e:
        print(str(e))
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/delivery')
def deliveryPage():
    try:
        if "Delivery_Partner_ID" in session:
            return render_template('index.html', session=session)
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
            mycursor = conn.cursor(buffered=True)

            Delivery_Partner_ID = hashlib.sha512((req['Delivery_Partner_Email']+req['Delivery_Partner_Email'].split("@")[0]).encode()).hexdigest()
            session["Delivery_Partner_ID"] = Delivery_Partner_ID
            session["Delivery_Partner_Password"] = req["Delivery_Partner_Password"]
            sql = "INSERT IGNORE INTO Delivery_Partner VALUES (%s, %s, %s, %s, '', %s, %s, 0, %s)"
            val = (Delivery_Partner_ID, req['Delivery_Partner_Email'].split("@")[0], req['Delivery_Partner_Email'], req["Delivery_Partner_Password"], req['Delivery_Partner_Latitude'], req['Delivery_Partner_Longitude'], w3.eth.accounts[random.randint(0,9)])
            mycursor.execute(sql, val)
            conn.commit()
            mycursor.close()
            
            session['Delivery_Partner_Email'] = req['Delivery_Partner_Email']
            session['Delivery_Partner_Name'] = req['Delivery_Partner_Email'].split("@")[0]

            mycursor = conn.cursor(buffered=True)
            mycursor.execute('SELECT * FROM Delivery_Partner WHERE Delivery_Partner_ID="'+session["Delivery_Partner_ID"]+'"')
            myresult = mycursor.fetchall()
            mycursor.close()

            if len(myresult) == 0:
                return jsonify(StatusCode = '0',ErrorMessage='Invalid User email')

            session['Delivery_Partner_Name'] = myresult[0][1]
            session['Delivery_Partner_Number'] = myresult[0][4]
            session['Delivery_Partner_Latitude'] = myresult[0][5]
            session['Delivery_Partner_Longitude'] = myresult[0][6]
            session['Delivery_Partner_Ratings'] = myresult[0][7]
            session['Delivery_Partner_Private_Key'] = myresult[0][8]

            return jsonify(StatusCode = '1', Message="Success")
    except Exception as e:
        print(str(e))
        return jsonify(StatusCode = '0', Message="Error")

@app.route('/updateProfile',methods = ['POST'])
def updateProfile():
    if request.method == "POST":
        try:
            if conn and "Delivery_Partner_ID" in session:
                request_json = request.get_json()
                mycursor = conn.cursor(buffered=True)
                sql = "UPDATE Delivery_Partner SET Delivery_Partner_Number=%s WHERE Delivery_Partner_ID=%s"
                val = (request_json['Delivery_Partner_Number'],)
                session['Delivery_Partner_Number'] = request_json['Delivery_Partner_Number']
                mycursor.execute(sql, val)
                conn.commit()
                mycursor.close()
                return jsonify(StatusCode = '1', Message="Success")
        except Exception as e:
            print(str(e))
            return jsonify(StatusCode = '0', Message="Error")

@app.route('/updateCoordinates',methods = ['POST'])
def updateCoordinates():
    if request.method == "POST":
        try:
            if conn and "Delivery_Partner_ID" in session:
                request_json = request.get_json()
                if session['Delivery_Partner_Latitude'] != 200:
                    if getPointDistance((session['Delivery_Partner_Latitude'], session['Delivery_Partner_Longitude']), (request_json['Delivery_Partner_Latitude'], request_json['Delivery_Partner_Longitude'])) < minimum_proximity:
                        return jsonify(StatusCode = '0', Message="Within proximity") 
                mycursor = conn.cursor(buffered=True)
                sql = "UPDATE Delivery_Partner SET Delivery_Partner_Latitude=%s, Delivery_Partner_Longitude=%s WHERE Delivery_Partner_ID=%s"
                val = (request_json['Delivery_Partner_Latitude'], request_json['Delivery_Partner_Longitude'], session['Delivery_Partner_ID'])
                mycursor.execute(sql, val)
                conn.commit()
                mycursor.close()
                session['Delivery_Partner_Latitude'] = request_json['Delivery_Partner_Latitude']
                session['Delivery_Partner_Longitude'] = request_json['Delivery_Partner_Longitude']
                return jsonify(StatusCode = '1', Message="Location Updated!") 
            return jsonify(StatusCode = '0', Message="Error") 
        except Exception as e:
            print(str(e))
            return jsonify(StatusCode = '0', Message="Error")  


@app.route('/logout',methods = ['GET']) 
def logout():
    session.pop("Delivery_Partner_ID")
    session.pop("Delivery_Partner_Name")
    session.pop("Delivery_Partner_Email")
    session.pop("Delivery_Partner_Password")
    session.pop("Delivery_Partner_Number")
    session.pop("Delivery_Partner_Latitude")
    session.pop("Delivery_Partner_Longitude")
    session.pop("Delivery_Partner_Ratings")
    session.pop("Delivery_Partner_Private_Key")
    return redirect('/')

if __name__ == '__main__':
    app.run(debug = False, port=5002)