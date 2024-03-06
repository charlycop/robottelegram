#/usr/bin/python -m nuitka'

from telethon import TelegramClient, events, sync
from enum import IntEnum
import re
import json
import csv
import time
import os
import copy
import config_telegram

def isFileStillPresent(file_name):
    return os.path.exists(file_name)

class cles(IntEnum):
    vends  = 0
    achete = 1
    sl     = 2
    tp1    = 3
    tp2    = 4
    tp3    = 5
    price  = 6
    type   = 7
    symbol = 8

# Constantes globales
TELEGRAM_API_ID   = config_telegram.API_ID
TELEGRAM_API_HASH = config_telegram.API_HASH
STARTUPSTRING = "Telegram client connected, awaiting for activity on investX"
MACOMMUNAUTE  = {"romu"     : 6395106917,
                 "bertrand" : 5666144867,
                 "hugo"     : 6571101763}
INVESTX_ID    = -1001240221457
KEYS_MSG  = ["vends", "achète", "stop loss", "take profit 1", "take profit 2", "take profit 3"]
KEYS_DICT = ["vends", "achète", "sl", "tp1", "tp2", "tp3", "price", "order_type", "symbol"]
TRADINGACCOUNT_PATHS = {"charly": 'C:\\MetaQuotes\\Production\\MT4_VANTAGE\\MQL4\\Files\\', 
                        "hugo"  : 'C:\\MetaQuotes\\Production\\MT4_VANTAGE_HUGO\\MQL4\\Files\\'}

def contains_only_numbers_and_commas(string):
    pattern = r'^[0-9,]+$'
    return bool(re.match(pattern, string))

def is_dictionary_valid(dictionary_to_check):
    required_keys = [KEYS_DICT[cles.type], KEYS_DICT[cles.sl], KEYS_DICT[cles.tp1], KEYS_DICT[cles.price], KEYS_DICT[cles.symbol]]
    
    if any(key not in dictionary_to_check for key in required_keys):
        return False
    
    return True

def parse_message(message):

    order_info = {}

    for line in message.lower().splitlines():   
        for keyword in KEYS_MSG:
            if keyword in line:
                if (KEYS_MSG[cles.vends] is keyword or KEYS_MSG[cles.achete] is keyword):
                    order_info[KEYS_DICT[cles.type]] = keyword
                    order_info[KEYS_DICT[cles.symbol]] = line.split()[-3]
                    if (contains_only_numbers_and_commas(line.split()[-1])):
                        order_info[KEYS_DICT[cles.price]]  = line.split()[-1]
                    
                elif (KEYS_MSG[cles.sl] == keyword):  
                    if (contains_only_numbers_and_commas(line.split()[-1])):
                        order_info[KEYS_DICT[cles.sl]] = line.split()[-1]
                
                elif (KEYS_MSG[cles.tp1] == keyword):
                    if (contains_only_numbers_and_commas(line.split()[-1])):
                        order_info[KEYS_DICT[cles.tp1]] = line.split()[-1]

                elif (KEYS_MSG[cles.tp2] == keyword):
                    if (contains_only_numbers_and_commas(line.split()[-1])):
                        order_info[KEYS_DICT[cles.tp2]] = line.split()[-1]

                elif (KEYS_MSG[cles.tp3] == keyword):
                    if (contains_only_numbers_and_commas(line.split()[-1])):
                        order_info[KEYS_DICT[cles.tp3]] = line.split()[-1]

    return [True, order_info] if is_dictionary_valid(order_info) else [False, order_info]


def sendToMT4(trade_infos):

    for terminal_name, MT4_path in TRADINGACCOUNT_PATHS.items():
        # Specify the file name
        file_name = MT4_path + "trade.csv"

        # Writing the dictionary to a CSV file
        with open(file_name, mode='w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            
            # Write the header (keys of the dictionary)
            writer.writerow(trade_infos.keys())
            
            # Write the values
            writer.writerow(trade_infos.values())

        print("CSV file has been written successfully...waiting for "+ terminal_name + "'s MT4 to send the order on the market")


def areAllTradesProceeded (plateformAnswers):
    for terminal_name, proceeded in plateformAnswers.items():
        if (proceeded == False):
            return False
    
    return True


def waitingForMT4():
    
    tradingaccount_result = copy.deepcopy(TRADINGACCOUNT_PATHS)

    # Replace the values with False
    for key in tradingaccount_result:
        tradingaccount_result[key] = False
        
    while(areAllTradesProceeded(tradingaccount_result) == False):

        time.sleep(10)
        for terminal_name, proceeded in tradingaccount_result.items():

            if (proceeded):
                continue

            file_name = TRADINGACCOUNT_PATHS[terminal_name] + "trade.csv"
            
            if isFileStillPresent(file_name):
                print("File still present, trade not proceeded by " + terminal_name + "'s MT4 yet")
            else:
                tradingaccount_result[terminal_name] = True
                print("Trade sent to market succesfully by "+ terminal_name + "'s MT4")


with TelegramClient('charlycop2', TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
    
    print(STARTUPSTRING)
    client.send_message('me', STARTUPSTRING)

    @client.on(events.NewMessage(from_users=INVESTX_ID, pattern='(?i).*ALERTE'))
    async def handler(event):
        trade = parse_message(event.message.message)
        result = "--=== Nouvelle alerte ! ===--" + "\n" + json.dumps(trade[1]) + "\n" + ("WARNING, VERIFIER LE TRADE, PARSING NOT COMPLETE !" if trade[0] is False else "TRADE PARSE AVEC SUCCES!") + "\n" + "---======---"
        print(result)
        await client.send_message('me', result)

        # On envoie à mes potes
        for telegram_id in MACOMMUNAUTE.values():
            await client.send_message(telegram_id, event.message.message)

        # On envoie à MT4 pour placer les trades
        if trade[0]:
            await client.send_message('me', "Sending the trade to MT4 platforms...")
            sendToMT4(trade[1])
            waitingForMT4()
            await client.send_message('me', "Trade sent to market succesfully on all MT4 accounts !")

    @client.on(events.NewMessage(from_users='me', pattern='caca'))
    async def handler(event):
        await event.reply('boudin')
        print("Ping test")


   
    client.run_until_disconnected()