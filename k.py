import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from pytz import timezone

from helpers import apology, login_required, lookup, usd



# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


"""Show portfolio of stocks"""
# FORM TABLE total SELECT name for lookup(name) of now price, price, total costmoney ,totalshares
portf = db.execute("SELECT name, symbol, price, sharesTotal, costmoneyTotal FROM total WHERE userID = :userID", userID=36)

# Len of portf list, rows
porLen = len(portf)

# For loop portf index "nowPrice" to new dict
for item in range(porLen):
    e = portf[item]["symbol"]
    print(f"{e}")
    nowPrice = lookup(e).get("price")
    print(f"{nowPrice}")
    portf[item]['nowPrice'] = nowPrice
    v = portf[item]['costmoneyTotal']
    print(f"{v}")
    s = type(v)
    print(f"{s}")
    """df = portf[item]['costmoneyTotal'] = usd(portf[item]['costmoneyTotal'])
    print(f"{df}")"""

soCash = db.execute("SELECT cash FROM users WHERE id = :userID",
                          userID=13)

sd = soCash[0]["cash"]
print(f"{sd}")
asw = type(sd)
print(f"{asw}")
soCash = usd(soCash[0]["cash"])
print(f"{soCash}")
symbolIn = "nc"


lin = lookup(symbolIn).get('symbol')



# SELECT if symbol in TABLE total
symbolIn = db.execute("SELECT name FROM total WHERE userID = :userID and symbol = :symbol",
                      userID=36, symbol=lin)


#if lin != sym:
print(f"{lin}")
if not symbolIn:

    print(f"{symbolIn}")
# FORM TABLE users SELECT end cash
endPrice = db.execute("SELECT cash FROM users WHERE id = :userID", userID=36)

CREATE TABLE 'total' ('id' integer PRIMARY KEY AUTOINCREMENT NOT NULL, 'name' text NOT NULL, 'symbol' text NOT NULL, 'price' real NOT NULL, 'sharesTotal' integer NOT NULL, 'costmoneyTotal' real NOT NULL, 'userID' integer NOT NULL)
CREATE TABLE 'buy' ('id' integer PRIMARY KEY AUTOINCREMENT NOT NULL, 'date' datetime NOT NULL, 'symbol' text NOT NULL, 'name' text NOT NULL, 'price' real NOT NULL, 'shares' integer NOT NULL, 'costmoney' real NOT NULL, 'userID' integer NOT NULL)
CREATE TABLE 'sell' ('id' integer PRIMARY KEY AUTOINCREMENT NOT NULL, 'date' datetime NOT NULL, 'symbol' text NOT NULL, 'name' text NOT NULL, 'price' real NOT NULL, 'shares' integer NOT NULL, 'totalGet' real NOT NULL, 'userID' integer NOT NULL)
CREATE TABLE 'users' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'username' TEXT NOT NULL, 'hash' TEXT NOT NULL, 'cash' NUMERIC NOT NULL DEFAULT 10000.00 )
CREATE TABLE 'bs' ('id' integer PRIMARY KEY AUTOINCREMENT NOT NULL, 'symbol' text NOT NULL, 'price' real NOT NULL, 'shares' integer NOT NULL, 'date' datetime NOT NULL, 'userID' integer NOT NULL)
# Select date, symbol, name, price, shares, costmoney from buy table
        buy = db.execute("SELECT * FROM buy WHERE userID=:userID", userID=session["user_id"])

        # Select date, symbol, name, price, number, totalGet from sell table
        sell = db.execute("SELECT *  FROM sell WHERE userID=:userID", userID=session["user_id"])

        # Select name, symbol, price, sharesTotal, costmoneyTotal from total table
        total = db.execute("SELECT * FROM total WHERE userID=:userID", userID=session["user_id"])

        # len of buy sell total
        bLen = len(buy)
        sLen = len(sell)
        tLen = len(total)


        sumb = 0
        # for in to change price costmoney totalGet costmoneyTotal
        for item in range(bLen):
            # convert buy list to buy[item] dict
            buy[item]["price"] = usd(buy[item]["price"])

            # For in get endPrice1
            sumb = buy[item]["costmoney"] + sumb


            buy[item]["costmoney"] = usd(buy[item]["costmoney"])

        endPrice1 = sumb


        sums = 0
        for item2 in range(sLen):
            sell[item2]["price"] = usd(sell[item2]["price"])

            # For in get endPrice2
            sums = sell[item2]["totalGet"] + sums

            sell[item2]["totalGet"] = usd(sell[item2]["totalGet"])

        endPrice2 = sums


        for item3 in range(tLen):
            total[item3]["price"] = usd(total[item3]["price"])
            total[item3]["costmoneyTotal"] = usd(total[item3]["costmoneyTotal"])

            # Add look Up symbol now price
            nowSymbol = total[item3]["symbol"]
            nowPrice = lookup(nowSymbol).get("price")

            # Usd now price
            total[item3]["nowPrice"] = usd(nowPrice)

        # Falsh massage
        flash('history')


        # Rander buy sell and total return value list
        return render_template("history.html", endPrice3=usd(endPrice1-endPrice2), endPrice1=usd(endPrice1), endPrice2=usd(endPrice2), buy=buy, sell=sell, total=total, bLen=bLen, sLen=sLen, tLen=tLen)
        return apology("TODO")