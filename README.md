# stocks-tracker

Stocks Tracker is a simple website you can use to store and update your investment portfolio.
I developed this website mainly to test out [yfinance](https://github.com/ranaroussi/yfinance), a Yahoo Finance API, as I have recently been intrigued by fintech products and so I wanted to just get my feet wet with some sort of finances related side project.
I also used this opportunity to test out Flask-Caching, an extension I didn't get the chance to try out last time I worked with Flask. 

The website itself is pretty basic - it allows you to search stocks and ETFs, and also save a 'Portfolio' with various stocks and ETFs, along with the purchase price and quantity. Of course, you can also add and remove stocks from your Portfolio, and I'm using Average Cost Basis for adding/removing stocks since that's what Canadian taxpayers would use.  

This project is far from a finished product – for example GET request method handling hasn’t been implemented nor have I implemented error handling. The original plan was to continue working on this project and implement more features such as graphs with various indicators, however, I recently decided I want to try something new so I plan on using this code base as a starting point for a RESTful API that I'll use to connect a mobile app (haven't decided whether I want to do an Android or iOS app yet) with a database. The end result for the mobile app will probably be something similar to Apple's Stocks app. 

To use the website, download the repo, then create a venv with Python 3 and run *python -m pip install -r requirements.txt*.
If you're unfamiliar with virtual environments, you can install the following project dependencies individually with pip:
- Flask-Caching
- requests
- yfinance
- mysql-connector-python
- Flask

I've also included a SQL dump in the top level directory you can use to populate your Portfolio with 100 shares of none other than FAANG.

