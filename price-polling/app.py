import os
import sys
import time
import yfinance as yf
import pandas as pd
import mysql.connector
from mysql.connector import Error
from flask import Flask, jsonify
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
    connection = get_connection()
    cursor = connection.cursor()

    
    sql = """
        INSERT INTO price_data (ticker, timestamp, open_price, high_price, low_price, close_price, volume)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            timestamp = VALUES(timestamp),
            open_price = VALUES(open_price),
            high_price = VALUES(high_price),
            low_price = VALUES(low_price),
            close_price = VALUES(close_price),
            volume = VALUES(volume)
    """

    latest_row = data.tail(1).iloc[0]
    timestamp = data.tail(1).index[0].to_pydatetime()

    values = (
        ticker, 
        timestamp,
        float(latest_row["Open"]),
        float(latest_row["High"]),
        float(latest_row["Low"]),
        float(latest_row["Close"]),
        float(latest_row["Volume"]),
    )

    cursor.execute(sql, values)
    connection.commit()
    cursor.close()
    connection.close()

    

def fetch_and_store():
    tickers = ["AAPL", "GOOGL", "MSFT"]

    for ticker in tickers:
        stock = yf.Ticker(ticker)
        data = stock.history(period = "1d", interval = "5m")

        if not data.empty:
            data = data[["Open", "High", "Low", "Close", "Volume"]]

            latest_row = data.tail(1)
            print(f"\n--- {ticker} ---")
            print(latest_row)
            insert_price_data(ticker, latest_row)
            print(f"{ticker} Latest data inserted.")
        else:
            print(f"No data returned for {ticker}")





# ---------------Flask Communication ------------------

def get_prices(ticker):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM price_data WHERE ticker = %s ORDER BY timestamp", (ticker,))
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows


# ---------------Flask API Route ----------------------

@app.route("/api/prices/<ticker>")
def prices_api(ticker):
    """API endpoint to get all price data for a ticker"""
    return jsonify(get_prices(ticker))

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


