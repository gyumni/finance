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
db = SQL("sqlite:///finance.db")


symbol_check = "qd"


# Check if symbol exist in lookup(symbol)
symbol_check2 = lookup(symbol_check)

symbol_name = symbol_check2.get("name")
symbol_price = symbol_check2.get("price")
symbol_symbol = symbol_check2.get("symbol")
print(f"{type(symbol_name)}")
print(f"{type(symbol_price)}")
print(f"{type(symbol_symbol)}")

# Check if shares of name is a integer
shares = 8



# Query database for user's cash
userCash = db.execute("SELECT cash FROM users WHERE id = :userID",
        userID=30)


userCash = (userCash[0]["cash"])
# Check user if have enough money
buyNeed = shares*symbol_price
print(f"buyNeed{buyNeed}")

if userCash > buyNeed:
    # Check purchasetime
    now = datetime.now(timezone('Asia/Shanghai'))

    # Add to buy table
    db.execute("INSERT INTO buy (date, symbol, name, price, shares, costmoney, userID) VALUES (:date, :symbol, :name, :price, :shares, :costmoney, :userID)",
          date=now, symbol=symbol_symbol, name=symbol_name, price=symbol_price, shares=shares, costmoney=buyNeed, userID=30)

    endCash=userCash-buyNeed
    print(f"{endCash}")
    # Update csah in user
    db.execute("UPDATE users SET cash = :cash WHERE id = :userID", cash=endCash, userID=30)

    # Ensure return total shares and costmoney
    sharesTotal = db.execute("SELECT shares FROM buy WHERE userID = :userID ", userID=30)
    costmoneyTotal = db.execute("SELECT costmoney FROM buy WHERE userID = :userID ", userID=30)
    print(f"{sharesTotal}")
    print(f"{costmoneyTotal}")

    # Sum total shares and cost

    st = len(sharesTotal)
    ct = len(sharesTotal)
    sumItem = 0
    for item in range(st):
        sumItem = sharesTotal[item]["shares"] + sumItem

    sharesTotal_2 = sumItem
    sumItem2 = 0
    for item2 in range(ct):
        sumItem2 = costmoneyTotal[item2]["costmoney"] + sumItem2
    costmoneyTotal_2 = sumItem2

    # Test if can update total though shares
    total = db.execute("SELECT sharesTotal FROM total WHERE userID = :userID and name = :name", userID=30, name=symbol_name)
    print(f"{total}")
    if not total:
        db.execute("INSERT INTO total (name, symbol, price, sharesTotal, costmoneyTotal, userID) VALUES (:name, :symbol, :price, :sharesTotal, :costmoneyTotal, :userID)",
          name=symbol_name, symbol=symbol_symbol, price=symbol_price, sharesTotal=sharesTotal_2, costmoneyTotal=costmoneyTotal_2, userID=30)
    else:

        db.execute("UPDATE total SET sharesTotal = :sharesTotal, costmoneyTotal = :costmoneyTotal WHERE userID = :userID and name = :name", sharesTotal=sharesTotal_2, costmoneyTotal=costmoneyTotal_2, userID=30, name=symbol_name)

    # SELECT all rows from total table WHERE userID = session["user_id"]
    total_2 = db.execute("SELECT * FROM total WHERE userID = :userID", userID=30)

    # Give the fit value, from name get symbol
    lenRows = len(total_2)

    soCash = db.execute("SELECT cash FROM users WHERE id = :userID",
          userID=30)
    soCash = soCash[0]["cash"]
    print(f"{soCash}")

    #return render_template("buyed.html", total_2=total_2, lenRows=lenRows,soCash=soCash)






