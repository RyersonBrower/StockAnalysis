import os
import sys
import time
import yfinance as yf
import pandas as pd
import mysql.connector
from mysql.connector import Error
from flask import Flask, jsonify, request
import threading
import datetime 

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

#----------------Helper Functions-----------------

# gets and stores mysql connection function
def get_connection():
    return mysql.connector.connect(
        host=host,
        port=port, #if not working check this first
        user=user,
        password=password,
        database=database,
    )


#inserts price data into table
def insert_price_data(ticker, data):
    """
    Inserts multiple rows from a DataFrame into MySQL.
    Keeps UNIQUE KEY on (ticker, timestamp) to prevent duplicates.
    Only prints the latest row for logging.
    """
    connection = get_connection()
    cursor = connection.cursor()

    sql = """
        INSERT INTO price_data (ticker, timestamp, open_price, high_price, low_price, close_price, volume)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            open_price = VALUES(open_price),
            high_price = VALUES(high_price),
            low_price = VALUES(low_price),
            close_price = VALUES(close_price),
            volume = VALUES(volume)
    """

    for idx, row in data.iterrows():
        timestamp = idx.to_pydatetime()  # convert index to datetime
        values = (
            ticker,
            timestamp,
            float(row["Open"]),
            float(row["High"]),
            float(row["Low"]),
            float(row["Close"]),
            float(row["Volume"]),
        )
        cursor.execute(sql, values)

    connection.commit()
    cursor.close()
    connection.close()

    # Print only the last row for logging
    latest_row = data.tail(1)
    print(f"\n--- {ticker} Latest Row ---")
    print(latest_row)
    print(f"{ticker} data inserted.\n")



    

def fetch_and_store():
    tickers = ["AAPL", "GOOGL", "MSFT"]

    for ticker in tickers:
        stock = yf.Ticker(ticker)

        # Historical daily data
        historical = stock.history(period="60d", interval="1d")
        if not historical.empty:
            historical = historical[["Open", "High", "Low", "Close", "Volume"]]
            insert_price_data(ticker, historical)
            print(f"{ticker} historical daily data inserted.")
        else:
            print(f"No historical data for {ticker}")

        # Intraday 5-min data
        intraday = stock.history(period="1d", interval="5m")
        if not intraday.empty:
            intraday = intraday[["Open", "High", "Low", "Close", "Volume"]]
            insert_price_data(ticker, intraday)
            print(f"{ticker} intraday 5-min data inserted.")
        else: print(f"No intraday data for {ticker}")

        # Log the last row only
        latest_row = intraday.tail(1) if not intraday.empty else historical.tail(1)
        print(f"\n--- {ticker} Latest Row ---")
        print(latest_row)
        print(f"{ticker} fetch complete.\n")





# ---------------Flask Communication ------------------

def get_prices(ticker, limit=80):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM price_data WHERE ticker = %s ORDER BY timestamp",
        (ticker, limit))
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return list(reversed(rows))


# ---------------Flask API Route ----------------------

@app.route("/api/prices/<ticker>")
def prices_api(ticker):
    """API endpoint to 80 rows because that is optimal for this time prime"""
    limit = request.args.get("limit", default=80, type=int) #default = last 80 rows
    rows = get_prices(ticker, limit)
    return jsonify(rows)
#-------------- MAIN LOOP -----------------

def start_price_loop():
    #continuously fetch price data every x minutes in background
    sys.stdout.reconfigure(line_buffering=True)
    first_cycle = True

    while True:
        print("\n --- Retrieving Price Data ---", flush=True)
        fetch_and_store()
        print("Price Data Retrieved.\n", flush=True)

        if first_cycle:
            first_cycle = False
            print("Initial fetch complete. Next fetch will be in 5 minutes", flush=True)
        
        time.sleep(300)






if __name__ == "__main__":
    # Start polling thread
    t = threading.Thread(target=start_price_loop, daemon=True)
    t.start()

    print("🟢 Starting Flask server...", flush=True)
    app.run(host="0.0.0.0", port=5001)


