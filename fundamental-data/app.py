import os
import sys
import time
import pandas as pd
import yfinance as yf
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from flask import Flask, jsonify
import threading

app = Flask(__name__)

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



# gets and stores mysql connection function
def get_connection():
    return mysql.connector.connect(
        host=host,
        port=port, #if not working check this first
        user=user,
        password=password,
        database=database,
    )


def insert_fundamentals(ticker, market_cap, pe_ratio, dividend_yield, last_updated):

    connection = get_connection()
    cursor = connection.cursor()

    sql = """
        INSERT INTO fundamentals(ticker, market_cap, pe_ratio, dividend_yield, last_updated)
        VALUES(%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            ticker = VALUES(ticker),
            market_cap = VALUES(market_cap),
            pe_ratio = VALUES(pe_ratio),
            dividend_yield = VALUES(dividend_yield),
            last_updated = VALUES(last_updated)
    """

    values = (ticker, market_cap, pe_ratio, dividend_yield, last_updated)

    cursor.execute(sql, values)
    connection.commit()
    cursor.close()
    connection.close()

    print(f"/n Last Updated at {last_updated}")
    
    

def fetch_and_store():
    tickers = ["AAPL", "GOOGL", "MSFT"]

    for ticker in tickers:
        stock = yf.Ticker(ticker)
        info = stock.info

        #only gathers relavent fields
        market_cap = info.get("marketCap")
        pe_ratio = info.get("trailingPE")
        dividend_yield = info.get("dividendYield")
        last_updated = datetime.now()

        print(f"\n--- {ticker} ---")
        print(f"Market Cap: {market_cap}, PE Ratio: {pe_ratio}, Divident Yield: {dividend_yield}")

        insert_fundamentals(ticker, market_cap, pe_ratio, dividend_yield, last_updated)

   


# --------------- Flask Communication ----------------

def get_fundamentals(ticker):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM fundamentals WHERE ticker = %s"
    cursor.execute(query, (ticker,))
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows



# ---------------- Flask API Route ------------------

@app.route("/api/fundamentals/<ticker>")
def fundamentals_api(ticker):
    data = get_fundamentals(ticker)
    return jsonify(data)


# ---------------- Background Loop --------------------
def start_fetch_loop():
    """Continuously fetch fundamentals every 24 hours in a background thread."""
    sys.stdout.reconfigure(line_buffering=True)  # ensures print flushes instantly
    first_cycle = True
    while True:
        print("\n--- Retrieving Fundamental Data ---", flush=True)
        fetch_and_store()
        print("Fundamental Data Retrieved.\n", flush=True)
        if first_cycle:
            first_cycle = False
            print("Initial fetch complete. Next fetch in 24 hours.", flush=True)
        time.sleep(86400)  # 24 hours

#-------------- RUN BOTH Flask + Fetch Loop -----------------

if __name__ == "__main__":
    #start fetch loop in background thread
    threading.Thread(target=start_fetch_loop, daemon=True).start()
    #Start Flask Server
    app.run(host="0.0.0.0", port=5002)



