import csv
import time
import os

def isFileStillPresent(file_name):
    return os.path.exists(file_name)

# Define the dictionary
datas = {"order_type": "vends", "symbol": "ger40", "price": "16870", "sl": "17000", "tp1": "16800", "tp2": "16360"}

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

sendToMT4(datas)