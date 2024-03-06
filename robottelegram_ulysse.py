import sys  # Importing sys module for program interruption
sys.path.append("C:\\Users\\admin\\Desktop\\robottelegram\\v3-bitget-api-sdk\\bitget-python-sdk-api")

import bitget.v2.mix.order_api   as maxOrderApi
import bitget.v2.mix.account_api as maxAccountApi
import bitget.v2.mix.market_api  as maxMarketApi
import bitget.bitget_api         as baseApi
from bitget.exceptions import BitgetAPIException

from telethon import TelegramClient, events, sync
from enum import IntEnum
import re
import json
import csv
import time
import os
import copy
import config_telegram
import config_bitget


# Constantes globales
TELEGRAM_API_ID   = config_telegram.API_ID
TELEGRAM_API_HASH = config_telegram.API_HASH
BITGET_APIKEY     = config_bitget.APIKEY
BITGET_SECRETKEY  = config_bitget.SECRETKEY
BITGET_PASSPHRASE = config_bitget.PASSPHRASE
RISK_TPs          = [10, 15, 25, 25, 15, 10]
DEFAULT_LEVERAGE  = 4
DEFAULT_POSITION  = 200
STARTUPSTRING     = "Telegram client connected, awaiting for activity on Ulysse.tif"
ULYSSETIF_ID      = -1001786419872
MA_COMMUNAUTE     = {"romu"     : 6395106917,
                     "bertrand" : 5666144867,
                     "hugo"     : 6571101763}


def getEntryPrice(peBas, peHaut):
    return (float(peBas) + float(peHaut)) / 2.0

def changeLeverage(_symbol, _newLeverage, _Direction):
   
    myAccount = maxAccountApi.AccountApi(BITGET_APIKEY, BITGET_SECRETKEY, BITGET_PASSPHRASE)
    try:
        leverageParams = {}
        leverageParams["symbol"]      = _symbol
        leverageParams["productType"] = "USDT-FUTURES"
        leverageParams["marginCoin"]  = "USDT"
        leverageParams["leverage"]    = _newLeverage
        leverageParams["holdSide"]    = _Direction
        response = myAccount.setLeverage(leverageParams)
        print(response)
    except BitgetAPIException as e:
        print("error:" + e.message)
        sys.exit("Program interrupted due to BitgetAPIException during changeLeverage()")  # Exiting the program

def recapAndConfirm (_orderParams, _newLeverage, _PositionRisk):
    
    print(" ___ ___ ___   _   ___ ___ _____ _   _ _      _ _____ ___ ___ ")
    print("| _ \\ __/ __| /_\\ | _ \\_ _|_   _| | | | |    /_\\_   _|_ _| __|")
    print("|   / _| (__ / _ \\|  _/| |  | | | |_| | |__ / _ \\| |  | || _| ")
    print("|_|_\\___\\___/_/ \\_\\_| |___| |_|  \\___/|____/_/ \\_\\_| |___|_|  ")
    print("")                                                               
    print("MONTANT : " + _PositionRisk + " USDT   ACTIF : " + _orderParams["symbol"] + "    LEVIER : " + _newLeverage + "x")
    print("")  
    print("PE : " + _orderParams["orderList"][0]["price"] + "    SL : " + _orderParams["orderList"][0]["presetStopLossPrice"])
    print("")  

    for i in range(len(_orderParams["orderList"])):
        print("TP" + str(i+1) + " : " + _orderParams["orderList"][i]["presetStopSurplusPrice"] + "      TAILLE : " + _orderParams["orderList"][i]["size"])

    print("---===========================---")
    print("") 


    #user_input = input("Ok pour poser les trades ? (Y/n) ").strip().lower()
    user_input = "y"
    if user_input == "":
        user_input = "y"

    if user_input != "y":
        return False
    
    return True

def placeMultipleOrders(_symbol, _prixEntree, _stopLoss, _ordersDict, _newLeverage, _PositionRisk, _Direction):
    
    orderList   = []
    orderParams = {}  

    for tp in _ordersDict:
        orderInfos = {} 
        orderInfos["price"]                   = _prixEntree
        orderInfos["side"]                    = _Direction
        orderInfos["orderType"]               = "limit"
        orderInfos["tradeSide"]               = "open"
        orderInfos["presetStopLossPrice"]     = _stopLoss
        orderInfos["size"]                    = _ordersDict[tp]['size']
        orderInfos["presetStopSurplusPrice"]  = _ordersDict[tp]['prix']
        orderList.append(orderInfos)

    orderParams["symbol"]          = _symbol
    orderParams["productType"]     = "USDT-FUTURES"
    orderParams["marginMode"]      = "isolated"
    orderParams["marginCoin"]      = "USDT"
    orderParams["orderList"]       = orderList

    if (recapAndConfirm(orderParams, _newLeverage, _PositionRisk)) == False:
        sys.exit("Trades annules par l'utilisateur, on sort !")  # Exiting the program

    # Prepare common order parameters
    myOrders = maxOrderApi.OrderApi(BITGET_APIKEY, BITGET_SECRETKEY, BITGET_PASSPHRASE)

    # Place all the orders
    try:
        response = myOrders.batchPlaceOrder(orderParams)
        #print(response)
        print("Ordres envoyés avec succès à BitGet!")
    except BitgetAPIException as e:
        print("error:" + e.message)
        print("Pour une raison inconnue, les ordres ont été refusés par BitGet!")
        sys.exit("Program interrupted due to BitgetAPIException during changeLeverage()")  # Exiting the program


def trade(donnees):
    # Retrieve values from input fields
    symbol        = donnees['Symbole']
    prixEntree    = str(round(sum(donnees['Prix entrée'])/len(donnees['Prix entrée']), 4))
    stopLoss      = str(donnees['SL'])
    newLeverage   = DEFAULT_LEVERAGE
    PositionRisk  = DEFAULT_POSITION
    direction     = donnees['Type de transaction'].lower()

    ordersDict= {  'tp1' : {'risk' : RISK_TPs[0], 'prix' : float(donnees['TP'][0]), 'size' : ""},
                   'tp2' : {'risk' : RISK_TPs[1], 'prix' : float(donnees['TP'][1]), 'size' : ""},
                   'tp3' : {'risk' : RISK_TPs[2], 'prix' : float(donnees['TP'][2]), 'size' : ""},
                   'tp4' : {'risk' : RISK_TPs[3], 'prix' : float(donnees['TP'][3]), 'size' : ""},
                   'tp5' : {'risk' : RISK_TPs[4], 'prix' : float(donnees['TP'][4]), 'size' : ""},
                   'tp6' : {'risk' : RISK_TPs[5], 'prix' : float(donnees['TP'][5]), 'size' : ""}}

    # calculate the sizes according to risk and investment risk
    for tp in ordersDict:
       size = (1/float(prixEntree))*float(newLeverage)*(ordersDict[tp]["risk"]/100)*float(PositionRisk)
       ordersDict[tp]["size"] = str(round(size * 0.92, 3))
    
    changeLeverage(symbol, newLeverage, direction)
    placeMultipleOrders(symbol, prixEntree, stopLoss, ordersDict, newLeverage, PositionRisk, direction)


def parse_message(message):
    # Définition du dictionnaire pour stocker les données
    donnees = {}

    # Extraction du symbole
    donnees['Symbole'] = re.search(r'([A-Z]+)', message).group(0) + "USDT"

    # Extraction du type de transaction
    donnees['Type de transaction'] = re.search(r'\((\w+)\)', message).group(1)

    # Extraction des prix d'entrée
    prix_entree = re.findall(r'\d+,\d+', message)[:2]
    donnees['Prix entrée'] = [float(p.replace(',', '.')) for p in prix_entree]

    # Extraction des TP
    tps = re.findall(r'\d+,\d+', re.search(r'TP :([\s\S]+?)SL', message).group(1))
    donnees['TP'] = [float(tp.replace(',', '.')) for tp in tps]

    # Extraction du SL
    donnees['SL'] = float(re.search(r'SL : (\d+,\d+)', message).group(1).replace(',', '.'))

    return donnees

def getTextSignal(donnees):
    # Affichage du dictionnaire contenant toutes les données
    resultat = f"""Symbole : {donnees['Symbole']}
Type de transaction : {donnees['Type de transaction']}
Prix d'entrées : {donnees['Prix entrée']}
TPs : {donnees['TP']}
SL : {donnees['SL']}"""

    # Affichage du résultat
    return resultat

with TelegramClient('charlycop2', TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
    
    print(STARTUPSTRING)
    client.send_message('me', STARTUPSTRING)

    pattern_Signal = [re.compile(r'\b{}\b'.format(re.escape(word)), re.IGNORECASE) for word in ["Chaque", "trade", "comporte", "un", "risque"]]
    #Ulyssetif_Annonces_id
    @client.on(events.NewMessage(from_users=ULYSSETIF_ID))
    async def handler(event):

        message_text = event.message.message.lower()  # Convertir en minuscules pour une correspondance insensible à la casse
        if all(pattern.search(message_text) for pattern in pattern_Signal):
            signal_Details = parse_message(event.message.message)
            
            #On envoie à mes potes
            for telegram_id in MA_COMMUNAUTE.values():
               await client.send_message(telegram_id, getTextSignal(signal_Details))

            await client.send_message('me', getTextSignal(signal_Details)) # pour moi

            trade(signal_Details)

    @client.on(events.NewMessage(from_users='me', pattern='caca'))
    async def handler(event):
        await event.reply('boudin_ulysse')
        print("Ping test")


   
    client.run_until_disconnected()