#/usr/bin/python -m nuitka'

from telethon import TelegramClient, events, sync
from enum import IntEnum
import re
import json
import csv
import time
import os

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

api_id = 26090511
api_hash = '7c525d46d000616892aa2455a62b98a0'
invextX_privateSpace_id = -1001240221457
romu_id = 6395106917
keys_msg  = ["vends", "achète", "stop loss", "take profit 1", "take profit 2", "take profit 3"]
keys_dict = ["vends", "achète", "sl", "tp1", "tp2", "tp3", "price", "order_type", "symbol"]

def contains_only_numbers_and_commas(string):
    pattern = r'^[0-9,]+$'
    return bool(re.match(pattern, string))

def is_dictionary_valid(dictionary_to_check):
    required_keys = [keys_dict[cles.type], keys_dict[cles.sl], keys_dict[cles.tp1], keys_dict[cles.price], keys_dict[cles.symbol]]
    
    if any(key not in dictionary_to_check for key in required_keys):
        return False
    
    return True

def parse_message(message):

    order_info = {}

    for line in message.lower().splitlines():   
        for keyword in keys_msg:
            if keyword in line:
                if (keys_msg[cles.vends] is keyword or keys_msg[cles.achete] is keyword):
                    order_info[keys_dict[cles.type]] = keyword
                    order_info[keys_dict[cles.symbol]] = line.split()[-3]
                    if (contains_only_numbers_and_commas(line.split()[-1])):
                        order_info[keys_dict[cles.price]]  = line.split()[-1]
                    
                elif (keys_msg[cles.sl] == keyword):  
                    if (contains_only_numbers_and_commas(line.split()[-1])):
                        order_info[keys_dict[cles.sl]] = line.split()[-1]
                
                elif (keys_msg[cles.tp1] == keyword):
                    if (contains_only_numbers_and_commas(line.split()[-1])):
                        order_info[keys_dict[cles.tp1]] = line.split()[-1]

                elif (keys_msg[cles.tp2] == keyword):
                    if (contains_only_numbers_and_commas(line.split()[-1])):
                        order_info[keys_dict[cles.tp2]] = line.split()[-1]

                elif (keys_msg[cles.tp3] == keyword):
                    if (contains_only_numbers_and_commas(line.split()[-1])):
                        order_info[keys_dict[cles.tp3]] = line.split()[-1]

    return [True, order_info] if is_dictionary_valid(order_info) else [False, order_info]

def sendToMT4(trade_infos):
    # Specify the file name
    MT4_path = 'C:\\MetaQuotes\\Production\\MT4_VANTAGE\\MQL4\\Files\\'
    file_name = MT4_path + "trade.csv"

    # Writing the dictionary to a CSV file
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        
        # Write the header (keys of the dictionary)
        writer.writerow(trade_infos.keys())
        
        # Write the values
        writer.writerow(trade_infos.values())

    print("CSV file has been written successfully...waiting for MT4 to send the order on the market")

    while isFileStillPresent(file_name):
        print("File still present, trade not proceeded by MT4 yet")
        time.sleep(10)

    print("Trade sent to market succesfully by MT4")

with TelegramClient('charlycop2', api_id, api_hash) as client:
    # for dialog in client.iter_dialogs():
    #     print(dialog.name, 'has ID', dialog.id)

    # for message in client.iter_messages(invextX_privateSpace_id):
    #     if (message.text is not None and "ALERTE" in message.text):
    #         trade = parse_message(message.text)
    #         result = "--=== Nouvelle alerte ! ===--" + "\n" + json.dumps(trade[1]) + "\n" + ("WARNING, VERIFIER LE TRADE, PARSING NOT COMPLETE !" if trade[0] is False else "TRADE PARSE AVEC SUCCES!")
    #         print(result)
    #         client.send_message('me', result)
    
    print("Telegram client connected, awaiting for activity")
    client.send_message('me', "Telegram client connected, awaiting for activity")

    @client.on(events.NewMessage(from_users=invextX_privateSpace_id, pattern='(?i).*ALERTE'))
    async def handler(event):
        trade = parse_message(event.message.message)
        result = "--=== Nouvelle alerte ! ===--" + "\n" + json.dumps(trade[1]) + "\n" + ("WARNING, VERIFIER LE TRADE, PARSING NOT COMPLETE !" if trade[0] is False else "TRADE PARSE AVEC SUCCES!") + "\n" + "---======---"
        print(result)
        await client.send_message('me', result)
        await client.send_message(romu_id, result)
        if trade[0]:
            await client.send_message('me', "sending the trade to MT4...")
            sendToMT4(trade[1])
            await client.send_message('me', "Trade sent to market succesfully by MT4!")

    @client.on(events.NewMessage(from_users='me', pattern='caca'))
    async def handler(event):
        await event.reply('boudin')
        print("Ping test")


   
    client.run_until_disconnected()