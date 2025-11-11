import os
import sys
import time
import pandas as pd
import mysql.connector
from mysql.connector import Error
from flask import Flask, jsonify
import threading

app = Flask(__name__)


# ------------- Database Config -------------------
host=os.environ.get("MYSQL_HOST", "localhost")
port=int(os.environ.get("MYSQL_PORT", 3306))
user=os.environ.get("MYSQL_USER", "appuser")
password=os.environ.get("MYSQL_PASSWORD", "apppassword")
database=os.environ.get("MYSQL_DATABASE", "stocks")

# ------------- Wait for MySQL to be ready ----------
for i in range(20):
    try: 
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        print("Connected to MySQL")
        break
    except Error:
        print (f"MySQL not ready, retrying ... ({i+1}/20)")
        time.sleep(2)
else:
    raise Exception("Cannot connect to MySQL after multiple retries")




# ---------------- Helper Functions ----------------
def get_connection():
    """Creates a new MySQL connection."""
    return mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
    )


def get_price_data(ticker):
    """Retrieve time-series price data for a ticker."""
    connection = get_connection()
    query = """
        SELECT timestamp, open_price, high_price, low_price, close_price, volume
        FROM price_data
        WHERE ticker = %s
        ORDER BY timestamp ASC
    """

    df = pd.read_sql(query, connection, params=(ticker,))
    connection.close()
    return df


def get_fundamentals(ticker):
    """Retrieve fundamental data for a ticker"""
    connection = get_connection()
    query = """SELECT * FROM fundamentals WHERE ticker = %s"""
    df = pd.read_sql(query, connection, params=(ticker,))
    connection.close()
    return df


def calculate_sma(df, window=20):
    """Calculate a 20-period Simple Moving Average"""
    df["SM20"] = df["close_price"].rolling(window=window).mean()
    return df


def fuse_data(ticker):
    """
    Combines price and fundamentals for a single ticker.
    Perform Analysis (Only SMA for now)
    """

    price_df = get_price_data(ticker)
    fundamentals_df = get_fundamentals(ticker)

    if price_df.empty or fundamentals_df.empty:
        print(f"No data availiable for {ticker}")
        return None
    
    price_df = calculate_sma(price_df)

    # Merge latest fundamentals (single row)
    latest_fund = fundamentals_df.iloc[-1].to_dict()

    return {
        "ticker": ticker,
        "price_data": price_df.to_dict(orient="records"),
        "fundamentals": latest_fund
    }



# ------------- Flask API Routes -----------------------

@app.route("/api/data/<ticker>")
def get_combined_data(ticker):
    fused = fuse_data(ticker)
    if fused is None:
        return jsonify({"error": "Data not availiable"}), 404
    return jsonify(fused)


# --------------- Background Monitoring (Optional) -------------

def periodic_health_check():
    """
    Optional: Background loop to check data availiability periodically.
    Prints status to logs.
    """

    sys.stdout.reconfigure(line_buffering=True)
    while True:
        print("Health check: verifying analysis data...", flush=True)
        for ticker in ["AAPL", "GOOGL", "MSFT"]:
            df = get_price_data(ticker)
            print(f"{ticker}: {len(df)} rows of price data.", flush=True)
        time.sleep(600) # every 10 minutes

# ---------------- Run Flask + Background Thread ---------------
if __name__ == "__main__":
    threading.Thread(target=periodic_health_check, daemon=True).start()
    print("Starting analysis & Visualization Flask server...", flush=True)
    app.run(host="0.0.0.0", port=5003)