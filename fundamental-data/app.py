import os
import sys
import time
import pandas as pd
import yfinance as yf
import mysql.connector
from mysql.connector import Error
import datetime


# --------------- Database Config -------------------
host=os.environ.get("MYSQL_HOST", "localhost")
port=int(os.environ.get("MYSQL_PORT", 3306))
user=os.environ.get("MYSQL_USER", "appuser")
password=os.environ.get("MYSQL_PASSWORD", "apppassword")
database=os.environ.get("MYSQL_DATABASE", "stocks")


# -------------Wait for MySQL to be ready --------------
for i in range(20):  # try 20 times
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        print("Connected to MySQL")
        break
    except Error as e:
        print(f"MySQL not ready, retrying... ({i+1}/20)")
        time.sleep(2)
else:
    raise Exception("Cannot connect to MySQL after multiple retries")



# --------------------- Helper Functions --------------------


#def insert_fundamental_data():
    
    

def fetch_and_store():
    tickers = ["AAPL", "GOOGL", "MSFT"]

    for ticker in tickers:
        stock = yf.Ticker(ticker)
        info = stock.info

        #only gathers relavent fields
        market_cap = info.get("marketCap")
        pe_ratio = info.get("trailingPE")
        dividend_yield = info.get("dividendYield")

        print(f"\n--- {ticker} ---")
        print(f"Market Cap: {market_cap}, PE Ratio: {pe_ratio}, Divident Yield: {dividend_yield}")

        #insert_fundamental_data(ticker, market_cap, pe_ratio, dividend_yield)

   


#-------------- MAIN LOOP -----------------
sys.stdout.reconfigure(line_buffering=True)  # <-- ensures print() flushes instantly

first_cycle = True

first_cycle = True

while True:
    print("\n--- Retrieving Fundamental Data ---", flush=True)
    fetch_and_store()
    print("Fundamental Data Retrieved.\n", flush=True)

    if first_cycle:
        first_cycle = False
        print("Initial fetch complete. Next fetch will be in 24 hours.", flush=True)
    
    time.sleep(86400)  # sleep 24 hours before next fetch




