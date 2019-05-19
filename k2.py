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






symCash = "nflx"
number = "1"
# Change user cash
symbol_name1 = lookup(symCash).get("name")
symbol_price1 = lookup(symCash).get("price")
symbol_symbol1 = lookup(symCash).get("symbol")
sellPrice = lookup(symCash).get("price")




# SELECT if symbol in TABLE total
symbolIn = db.execute("SELECT name FROM total WHERE userID = :userID and symbol = :symbol",
                  userID=35, symbol=symbol_symbol1)




# Ensure sell number is a number
number_number = len(number)
for i in range(number_number) :
    if number[i].isdigit() != True :
        s=1

number = int(number)
if number > 0:



    # Ensure user have enough this symbol
    symbolNum = db.execute("SELECT sharesTotal FROM total WHERE userID = :userID and symbol = :symbol",
                      userID=35, symbol=symbol_symbol1)



    # Cash = cash + sellPrice*number
    cash = db.execute("SELECT cash FROM users WHERE id = :userID",
                          userID=35)
    totalGet = sellPrice*number
    v = cash[0]["cash"]
    print(f"{v}")
    f = v + totalGet
    print(f"{f}")
    # Update csah in user
    db.execute("UPDATE users SET cash = :cash WHERE id = :userID", cash=f, userID=35)

    # INSERT sell TABLE date, shares, price, name, symbol, totalGet
    # Check sell time
    now = datetime.now(timezone('Asia/Shanghai'))

    # Add to sell table
    db.execute("INSERT INTO sell (date, symbol, name, price, number, totalGet, userID) VALUES (:date, :symbol, :name, :price, :number, :totalGet, :userID)",date=now, symbol=symbol_symbol1, name=symbol_name1, price=symbol_price1, number=number, totalGet=totalGet, userID=35)

    # SELECT and change costmoneyTotal FROM total
    costTot = db.execute("SELECT costmoneyTotal FROM total WHERE userID = :userID and name = :name",
                          userID=35, name = symbol_name1)
    costTotEnd = costTot[0]["costmoneyTotal"]-totalGet

    # Update sharesTotal costmoneyTotal total did by order
    db.execute("UPDATE total SET sharesTotal = :sharesTotal, costmoneyTotal = :costmoneyTotal WHERE userID = :userID and name = :name", sharesTotal=symbolNum[0]["sharesTotal"]-number, costmoneyTotal=costTotEnd, userID=35, name = symbol_name1)

    # render selled template
    #return render_template("selled.html",symbol=symbol_symbol1, name=symbol_name1, price=symbol_price1, number=number, totalGet=totalGet, costTotEnd=costTotEnd)
