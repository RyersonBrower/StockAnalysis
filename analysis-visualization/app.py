import os
import sys
import time
import pandas as pd
import mysql.connector
from mysql.connector import Error
from flask import Flask, jsonify
from flask_cors import CORS
import threading

app = Flask(__name__)
CORS(app)


# ------------- Database Config -------------------
host=os.environ.get("MYSQL_HOST", "mysql")
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
        connection.close()
        break
    except Error:
        print (f"MySQL not ready, retrying ... ({i+1}/20)")
        time.sleep(2)
else:
    raise Exception("Cannot connect to MySQL after multiple retries")




# ---------------- Query Functions ----------------
def get_connection():
    """Creates a new MySQL connection."""
    return mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
    )


def get_price_data(ticker, limit=80):
    connection = get_connection()
    query = """
        SELECT timestamp, open_price, high_price, low_price, close_price, volume
        FROM price_data
        WHERE ticker = %s
        ORDER BY timestamp DESC
        LIMIT %s
    """
    df = pd.read_sql(query, connection, params=(ticker, limit))
    connection.close()
    return df[::-1]


def get_fundamentals(ticker):
    connection = get_connection()
    query = """
        SELECT pe_ratio, market_cap, dividend_yield, last_updated
        FROM fundamentals
        WHERE ticker = %s
        ORDER BY last_updated DESC
        LIMIT 1
    """
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query, (ticker,))
    row = cursor.fetchone()
    cursor.close()
    connection.close()
    return row if row else {}




# ------------------- Indication calculation ----------------
def calculate_sma(df, window=20):
    df["SM20"] = df["close_price"].rolling(window=window).mean()
    return df

def calculate_rsi(df, window=14):
    delta = df["close_price"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=window, min_periods=window).mean()
    avg_loss = loss.rolling(window=window, min_periods=window).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))
    return df

# ------------------------ Data Fusion) ------------------------
def fuse_data(ticker):
    """""
    Combines price and fundamentals for a single ticker.
    Perform Analysis (Only SMA for now)
    """

    price_df = get_price_data(ticker)
    fundamentals = get_fundamentals(ticker)

    if price_df.empty or not fundamentals:
        print(f"No data availiable for {ticker}")
        return None
    
    # Doesn't send SMA if it's empty
    price_df = calculate_sma(price_df)
    price_df = calculate_rsi(price_df)
    price_df = price_df.dropna(subset=["SM20", "RSI"])


    return {
        "ticker": ticker,
        "price_data": price_df.to_dict(orient="records"),
        "fundamentals": fundamentals
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