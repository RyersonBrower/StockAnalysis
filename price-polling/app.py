import os
import sys
import time
import yfinance as yf
import pandas as pd
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

#-------------- MAIN LOOP -----------------
sys.stdout.reconfigure(line_buffering=True)  # <-- ensures print() flushes instantly

first_cycle = True

while True:
    print("\n--- Starting new polling cycle ---", flush=True)
    fetch_and_store()

    if first_cycle:
        print("Initial polling complete. Starting regular 5-minute cycles.\n", flush=True)
        first_cycle = False
    else:
        print("Sleeping for 5 minutes ... \n", flush=True)
        time.sleep(60)

