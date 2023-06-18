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
app.secret_key="HungryHogOinkOink"
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

geolocator = Nominatim(user_agent="HungryHog")
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


def GetCart():
    if conn:
        mycursor = conn.cursor()
        mycursor.execute("Select ORDER_SUMMARY.PRODUCT_ID, ORDER_SUMMARY.PRODUCT_NAME, ORDER_SUMMARY.QUANTITY, ORDER_SUMMARY.PRODUCT_PRICE, ORDER_SUMMARY.PRODUCT_LOGO, ORDER_SUMMARY.Kitchen_ID, ORDER_SUMMARY.SCHEDULE_TIME, ORDER_SUMMARY.TOTAL_AMOUNT, ORDER_SUMMARY.Meal_ID, ORDER_SUMMARY.USER_EMAIL, ORDER_SUMMARY.IS_COMPLETE, Meals.Meal_Timings, Meals.Meal_Type, Kitchen.Kitchen_Name FROM ORDER_SUMMARY LEFT JOIN Kitchen ON ORDER_SUMMARY.Kitchen_ID = Kitchen.Kitchen_ID LEFT JOIN Meals ON ORDER_SUMMARY.Meal_ID = Meals.Meal_ID WHERE ORDER_SUMMARY.USER_EMAIL=%s AND ORDER_SUMMARY.IS_COMPLETE=0;", (session['USER_EMAIL'], ))
        myresult = mycursor.fetchall()
        #print(myresult)
        mycursor.close()
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


def GetOrderNowData():
    if conn:
        mycursor = conn.cursor()
        mycursor.execute("Select ORDER_SUMMARY.PRODUCT_ID, ORDER_SUMMARY.PRODUCT_NAME, ORDER_SUMMARY.QUANTITY, ORDER_SUMMARY.PRODUCT_PRICE, ORDER_SUMMARY.PRODUCT_LOGO, ORDER_SUMMARY.Kitchen_ID, ORDER_SUMMARY.SCHEDULE_TIME, ORDER_SUMMARY.TOTAL_AMOUNT, ORDER_SUMMARY.Meal_ID, ORDER_SUMMARY.USER_EMAIL, ORDER_SUMMARY.IS_COMPLETE, Meals.Meal_Timings, Meals.Meal_Type, Kitchen.Kitchen_Name FROM ORDER_SUMMARY LEFT JOIN Kitchen ON ORDER_SUMMARY.Kitchen_ID = Kitchen.Kitchen_ID LEFT JOIN Meals ON ORDER_SUMMARY.Meal_ID = Meals.Meal_ID WHERE ORDER_SUMMARY.USER_EMAIL='"+session['USER_EMAIL']+"' AND ORDER_SUMMARY.IS_COMPLETE=1;")
        myresult = mycursor.fetchall()
        mycursor.close()
        #print(myresult)
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
    session['USER_EMAIL'] = token['userinfo']['email']
    session['USER_NAME'] = token['userinfo']['name']
    session['USER_PASSWORD'] = hashlib.sha512((session['USER_EMAIL']+session['USER_NAME']).encode()).hexdigest()

    mycursor = conn.cursor()
    sql = "INSERT IGNORE INTO USERS VALUES (%s, %s, %s, '', '', '', '', '', '', %s, 200, 200);"
    val = (session['USER_NAME'], session['USER_PASSWORD'], session['USER_EMAIL'], w3.eth.accounts[random.randint(0,9)])
    mycursor.execute(sql, val)
    conn.commit()
    mycursor.close()
    
    mycursor = conn.cursor()
    mycursor.execute('SELECT * FROM USERS WHERE USER_EMAIL="'+session["USER_EMAIL"]+'"')
    myresult = mycursor.fetchall()
    mycursor.close()
    #print(myresult)
    session['USER_STREET'] = myresult[0][3]
    session['USER_STATE'] = myresult[0][4]
    session['USER_CITY'] = myresult[0][5]
    session['USER_COUNTRY'] = myresult[0][6]
    session['USER_PINCODE'] = myresult[0][7]
    session['USER_MOBILE'] = myresult[0][8]
    session['USER_PRIVATE_KEY'] = myresult[0][9]
    session['USER_LATITUDE'] = myresult[0][10]
    session['USER_LONGITUDE'] = myresult[0][11]

    mycursor = conn.cursor()
    mycursor.execute('SELECT COUNT(*) FROM ORDER_SUMMARY WHERE USER_EMAIL="'+session["USER_EMAIL"]+'" AND IS_COMPLETE=0')
    myresult = mycursor.fetchall()
    mycursor.close()
    session['CART_COUNT'] = myresult[0][0]

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
# RECIPE GENERATION 
##############################################################################################################################################################



# Text to recipe
MODEL_NAME_OR_PATH = "flax-community/t5-recipe-generation"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME_OR_PATH, use_fast=True)
model = FlaxAutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME_OR_PATH)

# Text to image
model_id = "runwayml/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
pipe = pipe.to("cuda")


prefix = "items: "
# generation_kwargs = {
#     "max_length": 512,
#     "min_length": 64,
#     "no_repeat_ngram_size": 3,
#     "early_stopping": True,
#     "num_beams": 5,
#     "length_penalty": 1.5,
# }
generation_kwargs = {
    "max_length": 512,
    "min_length": 64,
    "no_repeat_ngram_size": 3,
    "do_sample": True,
    "top_k": 60,
    "top_p": 0.95
}

special_tokens = tokenizer.all_special_tokens
tokens_map = {
    "<sep>": "--",
    "<section>": "\n"
}
def skip_special_tokens(text, special_tokens):
    for token in special_tokens:
        text = text.replace(token, "")

    return text

def target_postprocessing(texts, special_tokens):
    if not isinstance(texts, list):
        texts = [texts]
    
    new_texts = []
    for text in texts:
        text = skip_special_tokens(text, special_tokens)

        for k, v in tokens_map.items():
            text = text.replace(k, v)

        new_texts.append(text)

    return new_texts

def generation_function(texts):
    _inputs = texts if isinstance(texts, list) else [texts]
    inputs = [prefix + inp for inp in _inputs]
    inputs = tokenizer(
        inputs, 
        max_length=256, 
        padding="max_length", 
        truncation=True, 
        return_tensors="jax"
    )

    input_ids = inputs.input_ids
    attention_mask = inputs.attention_mask

    output_ids = model.generate(
        input_ids=input_ids, 
        attention_mask=attention_mask,
        **generation_kwargs
    )
    generated = output_ids.sequences
    generated_recipe = target_postprocessing(
        tokenizer.batch_decode(generated, skip_special_tokens=False),
        special_tokens
    )
    return generated_recipe

def generate_image(prompt):
    image = pipe(prompt).images[0]
    image.save("./static/images/"+"_".join(prompt.split())+".jpg", "JPEG")
    return image



##############################################################################################################################################################
# PAGE ROUTES 
##############################################################################################################################################################



@app.route('/')
def indexPage():
    if conn:
        mycursor = conn.cursor()
        mycursor.execute("select * from Kitchen order by Kitchen_Ratings desc")
        myresult = mycursor.fetchall()
        mycursor.close()
        l=[]
        for i in range(min(5, len(myresult))):
            kitchen = {
                "Kitchen_ID" : myresult[i][0],
                "Kitchen_Email" : myresult[i][1],
                "Kitchen_Name" : myresult[i][2],
                "Kitchen_Password": myresult[i][3],
                "Kitchen_Type": myresult[i][4],
                "Kitchen_open_time": myresult[i][5],
                "Kitchen_Close_time": myresult[i][6],
                "Kitchen_Address": myresult[i][7],
                "Kitchen_City": myresult[i][8],
                "Kitchen_State": myresult[i][9],
                "Kitchen_Country": myresult[i][10],
                "Kitchen_Pincode": myresult[i][11],
                "Kitchen_Ratings" : myresult[i][12],
                "Kitchen_Number": myresult[i][13],
                "Popularity": myresult[i][14],
                "Kitchen_Latitude": myresult[i][15],
                "Kitchen_Longitude": myresult[i][16],            }
            if 'USER_LATITUDE' in session and session['USER_LATITUDE'] !=200:
                if getPointDistance((session['USER_LATITUDE'], session['USER_LONGITUDE']), (kitchen['Kitchen_Latitude'], kitchen['Kitchen_Longitude'])) < proximity_km:
                    l.append(kitchen)
            else:
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


@app.route('/ordernow')
def ordernowPage():
    if conn and "USER_EMAIL" in session:
        data = GetOrderNowData()
        #print(data)
        grouped_data = []
        for key, group in groupby(data, lambda x: x['SCHEDULE_TIME']):
            grouped_data.append(list(group))
        #print(len(grouped_data))
        #print('grouped_data:'+ str(grouped_data))
        return render_template('ordernow.html', session=session, data=grouped_data)
        
    elif conn:
        return redirect('/sign_in')
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")


@app.route('/recipe')
def recipePage():
    if conn and "USER_EMAIL" in session:
        return render_template('recipe.html', session=session)
    elif conn:
        return redirect('/sign_in')
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")


@app.route('/shopping_cart')
def shopping_cartPage():
    if conn and "USER_EMAIL" in session:
        data = GetCart()
        return render_template('shopping-cart.html', session=session, data=data)
    elif conn:
        return redirect('/sign_in')
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/profile')
def profilePage():
    if conn and "USER_EMAIL" in session:
        return render_template('profile.html', session=session)
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
        mycursor.close()
        l=[]
        for i in range(len(myresult)):
            kitchen = {
                "Kitchen_ID" : myresult[i][0],
                "Kitchen_Email" : myresult[i][1],
                "Kitchen_Name" : myresult[i][2],
                "Kitchen_Password": myresult[i][3],
                "Kitchen_Type": myresult[i][4],
                "Kitchen_open_time": myresult[i][5],
                "Kitchen_Close_time": myresult[i][6],
                "Kitchen_Address": myresult[i][7],
                "Kitchen_City": myresult[i][8],
                "Kitchen_State": myresult[i][9],
                "Kitchen_Country": myresult[i][10],
                "Kitchen_Pincode": myresult[i][11],
                "Kitchen_Ratings" : myresult[i][12],
                "Kitchen_Number": myresult[i][13],
                "Popularity": myresult[i][14],
                "Kitchen_Latitude": myresult[i][15],
                "Kitchen_Longitude": myresult[i][16],
            }

            if 'USER_LATITUDE' in session and session['USER_LATITUDE'] !=200:
                if getPointDistance((session['USER_LATITUDE'], session['USER_LONGITUDE']), (kitchen['Kitchen_Latitude'], kitchen['Kitchen_Longitude'])) < proximity_km:
                    l.append(kitchen)
            else:
                l.append(kitchen)
            
        return render_template('snacks.html', kitchens=l, kitchen_name="Kitchens", snack=[], session=session)
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")


@app.route('/snacks/<string:Kitchen_ID>')
def snacksPageDynamic(Kitchen_ID):
    if conn and "USER_EMAIL" in session:
        mycursor = conn.cursor(buffered=True)
        mycursor.execute("select SNACK.SNACK_ID, SNACK.SNACK_NAME, SNACK.SNACK_PRICE, SNACK.Kitchen_ID, Kitchen.Kitchen_Name, SNACK.Meal_ID, SNACK.SNACK_LOGO, Meals.Meal_Type, Meals.Meal_Timings, Kitchen.Kitchen_Latitude, Kitchen.Kitchen_Longitude, SNACK.SNACK_RATING FROM SNACK LEFT JOIN Kitchen ON SNACK.Kitchen_ID = Kitchen.Kitchen_ID LEFT JOIN Meals ON SNACK.Meal_ID = Meals.Meal_ID WHERE Kitchen.Kitchen_ID=%s", (Kitchen_ID,))
        myresult = mycursor.fetchall()
        mycursor.close()
        l = []
        kitchen_name=""
        for i in range(len(myresult)):
            #print(myresult[i][8])
            snack = {
                "SNACK_ID" : myresult[i][0],
                "SNACK_NAME" : myresult[i][1],
                "SNACK_PRICE": myresult[i][2],
                "Kitchen_ID": myresult[i][3],
                "Kitchen_Name": myresult[i][4],
                "Meal_ID": myresult[i][5],
                "Meal_Type" : myresult[i][7],
                "Meal_Timings": myresult[i][8],
                "Kitchen_Latitude": myresult[i][9],
                "Kitchen_Longitude": myresult[i][10],
                "SNACK_RATING": myresult[i][11]
            }
            if 'USER_LATITUDE' in session and session['USER_LATITUDE'] !=200:
                if getPointDistance((session['USER_LATITUDE'], session['USER_LONGITUDE']), (snack['Kitchen_Latitude'], snack['Kitchen_Longitude'])) >= proximity_km:
                    return redirect('/snacks')

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



##############################################################################################################################################################
# API ROUTES 
##############################################################################################################################################################



@app.route('/CheckServer')
def CheckServer():
    if conn:
        return jsonify(StatusCode = '1', Message="Connected!")
    else:
        return jsonify(StatusCode = '0', Message="Connection Failed!")

@app.route('/getUsers',methods = ['GET'])
def getUsers():
  if request.method == 'GET':
    try:
        if conn:
            mycursor = conn.cursor()
            mycursor.execute("SELECT * FROM USERS")
            myresult = mycursor.fetchall()
            mycursor.close()
            #print(myresult)
            Users = myresult
            return jsonify(Users = Users)
    except Exception as e:
        print(str(e))
        return jsonify(StatusCode = '0', Message="Error")

     

@app.route('/updatecartcount', methods = ['GET'])
def update_cart_count():
    try:
        if "USER_EMAIL" in session:
            mycursor = conn.cursor()
            mycursor.execute('SELECT COUNT(*) FROM ORDER_SUMMARY WHERE USER_EMAIL=%s AND IS_COMPLETE=0', (session["USER_EMAIL"], ))
            myresult = mycursor.fetchall()
            mycursor.close()
            session['CART_COUNT'] = myresult[0][0]
            return jsonify(StatusCode = '0', success = True, CART_COUNT = myresult[0][0])
    except Exception as e:
        print(str(e))
        return jsonify(StatusCode = '0', Message="Error")


@app.route('/getrecipe', methods = ['POST'])
def get_recipe():
    try:
        if "USER_EMAIL" in session:
            req = request.get_json()
            generated = generation_function([i.strip() for i in req['INGREDIENTS'].split(",")])
            #print(generated)
            result = []
            cur = ""

            for text in generated:
                recipe = {}
                sections = text.split("\n")
                for section in sections:
                    section = section.strip()
                    if section.startswith("title:"):
                        section = section.replace("title:", "")
                        cur = "Title"
                        if cur not in recipe:
                            recipe["Title"] = ""
                    elif section.startswith("ingredients:"):
                        section = section.replace("ingredients:", "")
                        cur = "Ingredients"
                        if cur not in recipe:
                            recipe["Ingredients"] = ""
                    elif section.startswith("directions:"):
                        section = section.replace("directions:", "")
                        cur = "Directions"
                        if cur not in recipe:
                            recipe["Directions"] = ""
                    if cur=="Title":
                        recipe[cur] += section.strip().capitalize()
                    else:
                        recipe[cur] += "\n".join([f"  - {info.strip().capitalize()}" for i, info in enumerate(section.split("--"))])
                result.append(recipe)
                    
            for i in range(len(result)):
                img = generate_image(result[i]["Title"])
                with open("./static/images/"+"_".join(result[i]["Title"].split())+".jpg", "rb") as img_file:
                    img = base64.b64encode(img_file.read()).decode("utf-8")
                result[i]["Image"] = img
            
            return jsonify(StatusCode = '1', RECIPE=result)
    except Exception as e:
        print(str(e))
        return jsonify(StatusCode = '0', Message="Error")




@app.route('/UsersAuthentication',methods = ['POST'])
def UsersAuthentication():
    if request.method == 'POST':
        req = request.get_json()
    try:
        if conn:
            mycursor = conn.cursor()
            street,city,state,country,zipcode=getLocationDetails(req['USER_LATITUDE'], req['USER_LONGITUDE'])
            sql = "INSERT IGNORE INTO USERS VALUES (%s, %s, %s, %s, %s, %s, %s, %s, '', %s, %s, %s);"
            val = (req['USER_EMAIL'].split("@")[0], req["USER_PASSWORD"], req['USER_EMAIL'], street, state, city, country, zipcode, w3.eth.accounts[random.randint(0,9)], req['USER_LATITUDE'], req['USER_LONGITUDE'])
            mycursor.execute(sql, val)
            conn.commit()
            mycursor.close()
            
            session['USER_EMAIL'] = req['USER_EMAIL']
            session['USER_NAME'] = req['USER_EMAIL'].split("@")[0]


            mycursor = conn.cursor()
            mycursor.execute('SELECT * FROM USERS WHERE USER_EMAIL="'+req["USER_EMAIL"]+'"')
            myresult = mycursor.fetchall()
            mycursor.close()
            if len(myresult) == 0:
                return jsonify(StatusCode = '0',ErrorMessage='Invalid User email')
            user_record = {
                "USER_NAME" : myresult[0][0],
                "USER_PASSWORD" : myresult[0][1],
                "USER_EMAIL" : myresult[0][2],
                "USER_STREET" : myresult[0][3],
                "USER_STATE" : myresult[0][4],
                "USER_CITY" : myresult[0][5],
                "USER_COUNTRY" : myresult[0][6],
                "USER_PINCODE" : myresult[0][7],
                "USER_MOBILE" : myresult[0][8],
                "USER_PRIVATE_KEY" : myresult[0][9],
                "USER_LATITUDE" : myresult[0][10],
                "USER_LONGITUDE" : myresult[0][11]
            }
            session['USER_NAME'] = myresult[0][0]
            session['USER_PASSWORD'] = myresult[0][1]
            session['USER_STREET'] = myresult[0][3]
            session['USER_STATE'] = myresult[0][4]
            session['USER_CITY'] = myresult[0][5]
            session['USER_COUNTRY'] = myresult[0][6]
            session['USER_PINCODE'] = myresult[0][7]
            session['USER_MOBILE'] = myresult[0][8]
            session['USER_PRIVATE_KEY'] = myresult[0][9]
            session['USER_LATITUDE'] = myresult[0][10]
            session['USER_LONGITUDE'] = myresult[0][11]

            mycursor = conn.cursor()
            mycursor.execute('SELECT COUNT(*) FROM ORDER_SUMMARY WHERE USER_EMAIL="'+session["USER_EMAIL"]+'" AND IS_COMPLETE=0')
            myresult = mycursor.fetchall()
            mycursor.close()
            session['CART_COUNT'] = myresult[0][0]

            return jsonify(StatusCode = '1', UserRecord=user_record)
    except Exception as e:
        print(str(e))
        return jsonify(StatusCode = '0', Message="Error")


@app.route('/ReviewSubmit',methods = ['POST'])
def ReviewSubmit():
    if request.method == 'POST':
        try:
            req = request.get_json()
            #print(req)
            transaction(session['USER_PRIVATE_KEY'], session['USER_EMAIL'], session['USER_NAME'], req['SNACK_ID'], req['SNACK_REVIEW'], req['SCHEDULE_TIME'], int(req['SNACK_RATING']))
            
            mycursor = conn.cursor()
            sql = "UPDATE SNACK SET SNACK_REVIEW_COUNT=SNACK_REVIEW_COUNT+1, SNACK_REVIEW_TOTAL=SNACK_REVIEW_TOTAL+%s, SNACK_RATING=ROUND((SNACK_REVIEW_TOTAL+%s)/(SNACK_REVIEW_COUNT+1), 2) WHERE SNACK_ID=%s"
            val = (int(req['SNACK_RATING']), int(req['SNACK_RATING']), req['SNACK_ID'])
            mycursor.execute(sql, val)
            conn.commit()
            mycursor.close()

            mycursor = conn.cursor()
            sql = "UPDATE Kitchen SET Kitchen_Review_Count=Kitchen_Review_Count+1, Kitchen_Review_Total=Kitchen_Review_Total+%s, Kitchen_Ratings=ROUND((Kitchen_Review_Total+%s)/(Kitchen_Review_Count+1), 2) WHERE Kitchen_ID=%s"
            val = (int(req['SNACK_RATING']), int(req['SNACK_RATING']), req['Kitchen_ID'])
            mycursor.execute(sql, val)
            conn.commit()
            mycursor.close()

            return jsonify(StatusCode = '1', Message="Review Saved!")
        except Exception as e:
            print(str(e))
            return jsonify(StatusCode = '0', Message="Error")



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
                mycursor.close()
                #print(myresult)
                KitchensList = []
                RecordCount = len(myresult)
                for i in range(len(myresult)):
                    KitchenRecord = {
                        "Kitchen_ID" : myresult[i][0],
                        "Kitchen_Email" : myresult[i][1],
                        "Kitchen_Name" : myresult[i][2],
                        "Kitchen_Password": myresult[i][3],
                        "Kitchen_Type": myresult[i][4],
                        "Kitchen_open_time": myresult[i][5],
                        "Kitchen_Close_time": myresult[i][6],
                        "Kitchen_Address": myresult[i][7],
                        "Kitchen_City": myresult[i][8],
                        "Kitchen_State": myresult[i][9],
                        "Kitchen_Country": myresult[i][10],
                        "Kitchen_Pincode": myresult[i][11],
                        "Kitchen_Ratings" : myresult[i][12],
                        "Kitchen_Number": myresult[i][13],
                        "Popularity": myresult[i][14],
                        "Kitchen_Latitude": myresult[i][15],
                        "Kitchen_Longitude": myresult[i][16],
                    }
                    KitchensList.append(KitchenRecord)
                
                return jsonify(StatusCode = '1', Total = RecordCount,  get_kitchens=KitchensList)
        except Exception as e:
            print(str(e))
            return jsonify(StatusCode = '0', Message="Error")


@app.route('/showMyLunchBoxOrders',methods = ['POST'])
def showMyLunchBoxOrders():
    if request.method == 'POST':
        req = request.get_json()
        try:
            if conn:
                mycursor = conn.cursor()
                mycursor.execute("select Lunch_Box_Order.Lunch_Box_Order_ID, Lunch_Box_Order.Lunch_Box_Type, Lunch_Box_Order.Lunch_Box_Size, Lunch_Box_Order.Lunch_Box_color_pref, Payment.Payment_type, Payment.Payment_Amt, Payment.Payment_Status, Kitchen.Kitchen_ID, Kitchen.Kitchen_Name, Delivery_Management.Delivery_Timings, Delivery_Management.Door_Step_Delivery FROM Lunch_Box_Order LEFT JOIN Kitchen ON Lunch_Box_Order.Kitchen_ID = Kitchen.Kitchen_ID LEFT JOIN Payment ON Lunch_Box_Order.Payment_ID = Payment.Payment_ID LEFT JOIN Delivery_Management ON Lunch_Box_Order.Delivery_ID = Delivery_Management.Delivery_ID Where Lunch_Box_Order.User_EMAIL='"+session('USER_EMAIL')+"'")
                myresult = mycursor.fetchall()
                #print(myresult)
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
            print(str(e))
            return jsonify(StatusCode = '0', Message="Error")


@app.route('/Shoping_cart',methods = ['GET', 'POST'])
def Shoping_cart():
    if request.method == 'GET':
        try:
            if conn:
                mycursor = conn.cursor()
                mycursor.execute("Select ORDER_SUMMARY.PRODUCT_ID, ORDER_SUMMARY.PRODUCT_NAME, ORDER_SUMMARY.QUANTITY, ORDER_SUMMARY.PRODUCT_PRICE, ORDER_SUMMARY.PRODUCT_LOGO, ORDER_SUMMARY.Kitchen_ID, ORDER_SUMMARY.SCHEDULE_TIME, ORDER_SUMMARY.TOTAL_AMOUNT, ORDER_SUMMARY.Meal_ID, ORDER_SUMMARY.USER_EMAIL, ORDER_SUMMARY.IS_COMPLETE, Meals.Meal_Timings, Meals.Meal_Type, Kitchen.Kitchen_Name FROM ORDER_SUMMARY LEFT JOIN Kitchen ON ORDER_SUMMARY.Kitchen_ID = Kitchen.Kitchen_ID LEFT JOIN Meals ON ORDER_SUMMARY.Meal_ID = Meals.Meal_ID WHERE ORDER_SUMMARY.USER_EMAIL='"+session['USER_EMAIL']+"' AND ORDER_SUMMARY.IS_COMPLETE=0;")
                myresult = mycursor.fetchall()
                mycursor.close()
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
                        "Kitchen_Name" : myresult[i][13],
                        "PAYMENT_ID": myresult[i][14]
                    }
                    getSnacks(ShoppingCartRecord["PRODUCT_ID"], ShoppingCartRecord["PRODUCT_LOGO"])
                    ShoppingCartRecord["PRODUCT_LOGO"] = ShoppingCartRecord["PRODUCT_ID"]+".jpg"
                    ShoppingCartList.append(ShoppingCartRecord)
                return jsonify(StatusCode = '1', Total = RecordCount, ShoppingCartList=ShoppingCartList)
        except Exception as e:
            print(str(e))
            return jsonify(StatusCode = '0', Message="Error")
    
    
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
                mycursor.close()
                session["CART_COUNT"]+=1
                return jsonify(StatusCode = '1', Total = mycursor.rowcount)
        except Exception as e:
            print(str(e))
            return jsonify(StatusCode = '0', Message="Error")
            

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
                #print(PRODUCT_LIST)
                for i in PRODUCT_LIST:
                    sql = "UPDATE ORDER_SUMMARY SET QUANTITY = %s, TOTAL_AMOUNT = %s, SCHEDULE_TIME = %s, PAYMENT_ID = %s, IS_COMPLETE = %s WHERE PRODUCT_ID = %s AND USER_EMAIL=%s AND PAYMENT_ID=%s"
                    val = (i['QUANTITY'], i['TOTAL_AMOUNT'], i['SCHEDULE_TIME'], PAYMENT_ID, IS_COMPLETE,  i['PRODUCT_ID'], session['USER_EMAIL'], '')
                    mycursor.execute(sql, val)
                    conn.commit()
                mycursor.close()
                latitude, longitude = getCoordinates(request_json['USER_STREET']+", "+request_json['USER_CITY']+", "+request_json['USER_STATE']+", "+request_json['USER_COUNTRY']+", "+request_json['USER_PINCODE'])
                #print(latitude, longitude, request_json)

                mycursor = conn.cursor()
                sql = "UPDATE USERS SET USER_LATITUDE=%s, USER_LONGITUDE=%s, USER_STREET=%s, USER_CITY=%s, USER_STATE=%s, USER_COUNTRY=%s, USER_PINCODE=%s, USER_MOBILE=%s WHERE USER_EMAIL=%s"
                if latitude != 200:
                    val = (latitude, longitude, request_json['USER_STREET'], request_json['USER_CITY'], request_json['USER_STATE'], request_json['USER_COUNTRY'], request_json['USER_PINCODE'], request_json['USER_MOBILE'], session['USER_EMAIL'])
                    session['USER_LATITUDE'] = latitude
                    session['USER_LONGITUDE'] = longitude
                else:
                    val = (session['USER_LATITUDE'], session['USER_LONGITUDE'], request_json['USER_STREET'], request_json['USER_CITY'], request_json['USER_STATE'], request_json['USER_COUNTRY'], request_json['USER_PINCODE'], request_json['USER_MOBILE'], session['USER_EMAIL'])
                session['USER_LATITUDE'] = request_json['USER_LATITUDE']
                session['USER_LONGITUDE'] = request_json['USER_LONGITUDE']
                session['USER_STREET'] = request_json['USER_STREET']
                session['USER_CITY'] = request_json['USER_CITY']
                session['USER_STATE'] = request_json['USER_STATE']
                session['USER_COUNTRY'] = request_json['USER_COUNTRY']
                session['USER_PINCODE'] = request_json['USER_PINCODE']
                session['USER_MOBILE'] = request_json['USER_MOBILE']
                mycursor.execute(sql, val)
                conn.commit()
                mycursor.close()

                update_cart_count()

                return jsonify(StatusCode = '1', Message="Success")
        except Exception as e:
            print(str(e))
            return jsonify(StatusCode = '0', Message="Error")


@app.route('/updateUserCoordinates',methods = ['POST'])
def updateUserCoordinates():
    if request.method == "POST":
        try:
            if conn and "USER_EMAIL" in session:
                request_json = request.get_json()
                if session['USER_LATITUDE'] != 200:
                    if getPointDistance((session['USER_LATITUDE'], session['USER_LONGITUDE']), (request_json['USER_LATITUDE'], request_json['USER_LONGITUDE'])) < minimum_proximity:
                        return jsonify(StatusCode = '0', Message="Within proximity") 
                mycursor = conn.cursor()
                street,city,state,country,zipcode=getLocationDetails(request_json['USER_LATITUDE'], request_json['USER_LONGITUDE'])
                #print(request_json,street,city,state,country,zipcode)
                if request_json['USER_REQUEST'] == 1:
                    sql = "UPDATE USERS SET USER_LATITUDE=%s, USER_LONGITUDE=%s, USER_STREET=%s, USER_CITY=%s, USER_STATE=%s, USER_COUNTRY=%s, USER_PINCODE=%s WHERE USER_EMAIL=%s AND USER_LATITUDE=200"
                    if session['USER_LATITUDE'] == 200:
                        session['USER_LATITUDE'] = request_json['USER_LATITUDE']
                        session['USER_LONGITUDE'] = request_json['USER_LONGITUDE']
                        session['USER_STREET'] = street
                        session['USER_CITY'] = city
                        session['USER_STATE'] = state
                        session['USER_COUNTRY'] = country
                        session['USER_PINCODE'] = zipcode
                else:
                    sql = "UPDATE USERS SET USER_LATITUDE=%s, USER_LONGITUDE=%s, USER_STREET=%s, USER_CITY=%s, USER_STATE=%s, USER_COUNTRY=%s, USER_PINCODE=%s WHERE USER_EMAIL=%s"
                    session['USER_LATITUDE'] = request_json['USER_LATITUDE']
                    session['USER_LONGITUDE'] = request_json['USER_LONGITUDE']
                    session['USER_STREET'] = street
                    session['USER_CITY'] = city
                    session['USER_STATE'] = state
                    session['USER_COUNTRY'] = country
                    session['USER_PINCODE'] = zipcode
                val = (request_json['USER_LATITUDE'], request_json['USER_LONGITUDE'], street, city, state, country, zipcode, session['USER_EMAIL'])
                mycursor.execute(sql, val)
                conn.commit()
                mycursor.close()

                
                return jsonify(StatusCode = '1', Message="Location Updated!") 
            return jsonify(StatusCode = '0', Message="Error") 
        except Exception as e:
            print(str(e))
            return jsonify(StatusCode = '0', Message="Error")  


@app.route('/deleteCartRow',methods = ['POST'])
def deleteCartRow():
    if request.method == 'POST':
        try:
            if conn:
                request_json = request.get_json()
                PRODUCT_ID = request_json.get("PRODUCT_ID")
                #print("PRODUCT_ID: ", PRODUCT_ID)
                mycursor = conn.cursor()
                mycursor.execute("DELETE FROM ORDER_SUMMARY WHERE PRODUCT_ID='"+PRODUCT_ID+"' AND USER_EMAIL='"+session['USER_EMAIL']+"'")
                conn.commit()
                mycursor.close()
                return jsonify(StatusCode = '1', Message="Row Deleted!")
        except Exception as e:
            print(str(e))
            return jsonify(StatusCode = '0', Message="Error")


@app.route('/updateProfile',methods = ['POST'])
def updateProfile():
    if request.method == "POST":
        try:
            if conn and "USER_EMAIL" in session:
                request_json = request.get_json()
                latitude, longitude = getCoordinates(request_json['USER_STREET']+", "+request_json['USER_CITY']+", "+request_json['USER_STATE']+", "+request_json['USER_COUNTRY']+", "+request_json['USER_PINCODE'])
                #print(latitude, longitude, request_json)

                mycursor = conn.cursor()
                sql = "UPDATE USERS SET USER_LATITUDE=%s, USER_LONGITUDE=%s, USER_STREET=%s, USER_CITY=%s, USER_STATE=%s, USER_COUNTRY=%s, USER_PINCODE=%s, USER_MOBILE=%s WHERE USER_EMAIL=%s"
                if latitude != 200:
                    val = (latitude, longitude, request_json['USER_STREET'], request_json['USER_CITY'], request_json['USER_STATE'], request_json['USER_COUNTRY'], request_json['USER_PINCODE'], request_json['USER_MOBILE'], session['USER_EMAIL'])
                    session['USER_LATITUDE'] = latitude
                    session['USER_LONGITUDE'] = longitude
                else:
                    val = (session['USER_LATITUDE'], session['USER_LONGITUDE'], request_json['USER_STREET'], request_json['USER_CITY'], request_json['USER_STATE'], request_json['USER_COUNTRY'], request_json['USER_PINCODE'], request_json['USER_MOBILE'], session['USER_EMAIL'])
                    session['USER_LATITUDE'] = session['USER_LATITUDE']
                    session['USER_LONGITUDE'] = session['USER_LONGITUDE']
                session['USER_STREET'] = request_json['USER_STREET']
                session['USER_CITY'] = request_json['USER_CITY']
                session['USER_STATE'] = request_json['USER_STATE']
                session['USER_COUNTRY'] = request_json['USER_COUNTRY']
                session['USER_PINCODE'] = request_json['USER_PINCODE']
                session['USER_MOBILE'] = request_json['USER_MOBILE']
                mycursor.execute(sql, val)
                conn.commit()
                mycursor.close()

                return jsonify(StatusCode = '1', Message="Success")
        except Exception as e:
            print(str(e))
            return jsonify(StatusCode = '0', Message="Error")




if __name__ == '__main__':
    app.run(debug = False)