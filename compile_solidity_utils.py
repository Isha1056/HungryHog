import pickle
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
from marshmallow import Schema, fields, ValidationError
import json
import mysql.connector




# web3.py instance
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
account_key = w3.eth.accounts[1]
#contracts = compile_files(['user.sol', 'stringUtils.sol'])
"""
def separate_main_n_link(file_path, contracts):
    # separate out main file and link files
    # assuming first file is main file.
    main = {}
    link = {}

    all_keys = list(contracts.keys())
    for key in all_keys:
        if file_path[0] in key:
            main = contracts[key]
        else:
            link[key] = contracts[key]
    return main, link
"""    

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


"""
def deploy_n_transact(file_path, mappings=[]):
    # compile all files
    contracts = compile_files(file_path, import_remappings=mappings)
    link_add = {}
    contract_interface, links = separate_main_n_link(file_path, contracts)
    # first deploy all link libraries
    for link in links:
        link_add[link] = deploy_contract(links[link])    
    # now link dependent library code to main contract binary 
    # https://solidity.readthedocs.io/en/v0.4.24/using-the-compiler.html?highlight=library
    if link_add:
        contract_interface['bin'] = link_code(contract_interface['bin'], link_add)    
    # return contract receipt and abi(application binary interface)
    return deploy_contract(contract_interface), contract_interface['abi']
"""

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

def convertToBinaryData(filename):
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

def enter_snacks():
    conn = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "pass@123",
        database = "tiffin_service"
    )

    vals = (
        ('SNK0002', 'Fried Chicken Momos', '60', 'dg', 2010, convertToBinaryData("/mnt/c/Users/angad/OneDrive/Documents/GitHub/HungryHog/static/images/snacks_frynonvegmomo.jpg"), 0, 0, 0),
        ('SNK0003', 'Veg Chowmein', '65', 'hrhk', 2012, convertToBinaryData("/mnt/c/Users/angad/OneDrive/Documents/GitHub/HungryHog/static/images/snacks_chommeen.jpg"), 0, 0, 0),
        ('SNK0004', 'Chicken Momos', '55', 'sf', 2010, convertToBinaryData("/mnt/c/Users/angad/OneDrive/Documents/GitHub/HungryHog/static/images/snacks_nonvegmomo.jpg"), 0, 0, 0),
        ('SNK0005', 'Fried Veg Momos', '50', 'akd', 2010, convertToBinaryData("/mnt/c/Users/angad/OneDrive/Documents/GitHub/HungryHog/static/images/snacks_vegmomo.jpg"), 0, 0, 0),
        ('SNK0006', 'Veg Spring Rolls', '60', 'bbk', 2011, convertToBinaryData("/mnt/c/Users/angad/OneDrive/Documents/GitHub/HungryHog/static/images/snacks_vegroll.jpg"), 0, 0, 0),
        ('SNK0007', 'Golgappa', '50','lb', 2010, convertToBinaryData("/mnt/c/Users/angad/OneDrive/Documents/GitHub/HungryHog/static/images/snacks_gol.jpg"), 0, 0, 0),
        ('SNK0008', 'Noodles', '100','lb', 2015, convertToBinaryData("/mnt/c/Users/angad/OneDrive/Documents/GitHub/HungryHog/static/images/snacks_chommeen.jpg"), 0, 0, 0),
        ('SNK0009', 'Kimchi', '140','lb', 2015, convertToBinaryData("/mnt/c/Users/angad/OneDrive/Documents/GitHub/HungryHog/static/images/snacks_chommeen.jpg"), 0, 0, 0),
        ('SNK00010', 'Boba Tea', '100','lb', 2015, convertToBinaryData("/mnt/c/Users/angad/OneDrive/Documents/GitHub/HungryHog/static/images/snacks_chommeen.jpg"), 0, 0, 0),
        ('SNK00011', 'Pizza', '400','lb', 2015, convertToBinaryData("/mnt/c/Users/angad/OneDrive/Documents/GitHub/HungryHog/static/images/snacks_chommeen.jpg"), 0, 0, 0)
    )
    for i in vals:
        mycursor = conn.cursor()
        sql = """INSERT INTO SNACK VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);"""
        val = (i)
        mycursor.execute(sql, val)
        conn.commit()


compile_contract()
enter_snacks()