from flask import Flask, render_template, request
from flask_caching import Cache
import mysql.connector
import yfinance as yf
from decimal import *


# ==== Start database connection setup ==== #

db = mysql.connector.connect(
    host="localhost",
    user="test_user",
    password="password",
    database="STOCKS_TRACKER"
)

cursor = db.cursor()

# ==== End database connection setup ==== #



# ==== Start routing and cache setup ==== #

cache = Cache()
app = Flask(__name__)
app.config['CACHE_TYPE'] = "simple"
cache.init_app(app)


@app.route("/", methods=["GET", "POST"])
@cache.cached(timeout=0)
def index():
    # Get ticker symbols from Portfolio as well as constant value columns  
    query = "SELECT Ticker, Quantity, AvgPurchasePrice FROM Portfolio;"
    cursor.execute(query)
    tickers = cursor.fetchall()

    # Update market data for stocks in Portfolio 
    for ticker in tickers:
        yfTicker = yf.Ticker(ticker[0])
        previousClose = previousClose = yfTicker.info["regularMarketPreviousClose"]
        currentPrice = yfTicker.info["regularMarketPrice"]
        valueOfPosition = ticker[1] * currentPrice
        costToPurchase = float(ticker[1] * ticker[2])
        if costToPurchase == valueOfPosition:
            returnOfPosition = "0.00"
            returnSign = ''
        elif costToPurchase < valueOfPosition:
            returnOfPosition = valueOfPosition - costToPurchase
            returnSign = '+'
        else:
            returnOfPosition = costToPurchase - valueOfPosition
            returnSign = '-'
        
        query = "UPDATE Portfolio SET PrevClose = {}, CurrPrice = {}, ValueOfPosition = {}, ReturnOfPosition = {}, ReturnSign = '{}' WHERE Ticker = '{}';"
        query = query.format(previousClose, currentPrice, valueOfPosition, returnOfPosition, returnSign, ticker[0])
        cursor.execute(query)
        
    db.commit()

    # Get Portfolio from database
    query = "SELECT * FROM Portfolio;"
    cursor.execute(query)
    portfolio = cursor.fetchall()

    return render_template("index.html", portfolio=portfolio)


@app.route("/search/<stock>", methods=["GET", "POST"])
def search(stock):
    if request.method == "POST":
        searchStock = request.form["tickerSymbol"]
        ticker = yf.Ticker(searchStock)
        currentPrice = ticker.info["regularMarketPrice"]
        previousClose = ticker.info["regularMarketPreviousClose"]
        companySummary = ticker.info["longBusinessSummary"]
    
    return render_template("search.html", ticker=searchStock.upper(), companySummary=companySummary, currentPrice=currentPrice, previousClose=previousClose)


@app.route("/update/<action>/<stock>/<quantity>/<price>", methods=["GET", "POST"])
@app.route("/update/<action>/<stock>/<quantity>", methods=["GET", "POST"])
def update(action, stock, quantity, price):
    if request.method == "POST":
        cache.clear()
        # Get ticker symbols from Portfolio as well as constant value columns  
        query = "SELECT Ticker, Quantity, AvgPurchasePrice FROM Portfolio;"
        cursor.execute(query)
        tickers = cursor.fetchall()

        if action == "add":
            stockName = (request.form["addStockName"]).upper()
            stockQuantity = int(request.form["addStockQuantity"])
            stockPurchasePrice = Decimal(request.form["addStockPrice"])
            for ticker in tickers:
                if ticker[0] == stockName:
                    newAvgPurchasePrice = ((Decimal(stockQuantity)*stockPurchasePrice) + (ticker[1]*ticker[2])) / Decimal((stockQuantity + ticker[1]))
                    query = "UPDATE Portfolio SET Quantity = {}, AvgPurchasePrice = {} WHERE Ticker = '{}';"
                    query = query.format(stockQuantity + ticker[1], round(newAvgPurchasePrice, 2), stockName)
                    cursor.execute(query)
                    db.commit()
                    break
            return render_template("update.html", action=action, stock=stockName, quantity=stockQuantity)
        else:
            action = "remov"
            stockName = (request.form["removeStockName"]).upper()
            stockQuantity = int(request.form["removeStockQuantity"])
            for ticker in tickers:
                if ticker[0] == stockName:
                    if ticker[1] < stockQuantity:
                        errorMsg = "You cannot remove more shares than you currently own!"
                        return render_template("error.html", errorMsg=errorMsg)
                    else:
                        newQuantity = ticker[1] - stockQuantity
                        query = "UPDATE Portfolio SET Quantity = {} WHERE Ticker = '{}';"
                        query = query.format(newQuantity, stockName)
                        cursor.execute(query)
                        db.commit()
                    break
            return render_template("update.html", action=action, stock=stockName, quantity=stockQuantity)

    return render_template("update.html")


@app.route("/refresh")
def refresh():
    cache.clear()
    return render_template("refresh.html")

# ==== End routing setup ==== #



# Run app
if __name__ == "__main__":
    app.run(debug=True)