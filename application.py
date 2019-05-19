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

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":

        # FORM TABLE total SELECT name for lookup(name) of now price, price, total costmoney ,totalshares
        portf = db.execute("SELECT name, symbol, price, sharesTotal, costmoneyTotal FROM total WHERE userID = :userID", userID=session["user_id"])

        # Len of portf list, rows
        porLen = len(portf)

        # For loop portf index "nowPrice" to new dict, costmoneyTotal
        for item in range(porLen):
            e = portf[item]["symbol"]
            nowPrice = lookup(e).get("price")
            portf[item]['nowPrice'] = nowPrice
            portf[item]['costmoneyTotal'] = usd(portf[item]['costmoneyTotal'])

        # List reversed
        portf = list(reversed(portf))


        # FORM TABLE users SELECT end cash
        endPrice = db.execute("SELECT cash FROM users WHERE id = :userID", userID=session["user_id"])

        endPrice = usd(endPrice[0]["cash"])
        return render_template("index.html", portf=portf, endPrice = endPrice, porLen=porLen)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("buy.html")
    else:
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide symbol", 400)

        # Check if symbol exist in lookup(symbol)
        symbol = lookup(symbol)

        if not symbol :
            return apology("symbol doesn't exist,sorry", 400)
        else:
            name = symbol.get("name")
            price = symbol.get("price")
            symbol = symbol.get("symbol")

            # Check if shares of name is a integer
            shares = request.form.get("shares")

            # https://www.geeksforgeeks.org/program-check-input-integer-string/
            n = len(shares)
            for i in range(n) :
                if shares[i].isdigit() != True :
                    return apology("shares need to be a number", 400)

            shares = int(shares)

            # if positive number
            if shares > 0:

                # Query database for user's cash
                cash = db.execute("SELECT cash FROM users WHERE id = :userID",
                          userID=session["user_id"])

                # Get cash
                cash = cash[0]["cash"]

                # Check user if have enough money
                buyNeed = shares*price
                if cash > buyNeed:

                    # Update csah in users TABLE
                    db.execute("UPDATE users SET cash = :cash WHERE id = :userID", cash=cash-buyNeed, userID=session["user_id"])

                    # Check purchase time
                    now = datetime.now(timezone('Asia/Shanghai'))

                    # Add to buy table
                    db.execute("INSERT INTO buy (date, symbol, name, price, shares, costmoney, userID) VALUES (:date, :symbol, :name, :price, :shares, :costmoney, :userID)",
                          date=now, symbol=symbol, name=name, price=price, shares=shares, costmoney=buyNeed, userID=session["user_id"])

                    # Add to buy-sell table
                    db.execute("INSERT INTO bs (symbol, price, shares, date, userID) VALUES (:symbol, :price, :shares, :date, :userID)", symbol=symbol, price=usd(price), shares=shares, date=now, userID=session["user_id"])

                    # Count finally cash
                    endCash=cash-buyNeed

                    # Count total shares and costmoney by buy
                    sharesTotal = db.execute("SELECT shares FROM buy WHERE userID = :userID and name = :name", userID=session["user_id"], name=name)
                    costmoneyTotal = db.execute("SELECT costmoney FROM buy WHERE userID = :userID and name = :name", userID=session["user_id"], name=name)

                    # len(sharesTotal)
                    st = len(sharesTotal)

                    # Sum shares
                    sumItem = 0
                    for item in range(st):
                        sumItem = sharesTotal[item]["shares"] + sumItem
                    sharesTotal_2 = sumItem

                    # Sum cost money
                    sumItem2 = 0
                    for item2 in range(st):
                        sumItem2 = costmoneyTotal[item2]["costmoney"] + sumItem2
                    costmoneyTotal_2 = sumItem2


                    # Ensure return total number and totalGet by sell
                    sharesTotalSell = db.execute("SELECT shares FROM sell WHERE userID = :userID and name = :name", userID=session["user_id"], name=name)
                    costmoneyTotalSell = db.execute("SELECT totalGet FROM sell WHERE userID = :userID and name = :name", userID=session["user_id"], name=name)

                    # Len of sharesTotalSell
                    stS = len(sharesTotalSell)

                    # Sum of sell shares
                    sumItem3 = 0
                    for item3 in range(stS):
                        sumItem3 = sharesTotalSell[item3]["shares"] + sumItem3

                    # Buy - sell shares
                    sharesTotal_2 = sharesTotal_2-sumItem3

                    # Sum of sell totalGet
                    sumItem4 = 0
                    for item4 in range(stS):
                        sumItem4= costmoneyTotalSell[item4]["totalGet"] + sumItem4

                    # Buy -sell totalGet
                    costmoneyTotal_2 = costmoneyTotal_2-sumItem4

                    # Test if can update total though shares
                    total = db.execute("SELECT sharesTotal FROM total WHERE userID = :userID and name = :name", userID=session["user_id"], name=name)

                    # Insert total TABLE
                    if not total:
                        db.execute("INSERT INTO total (name, symbol, price, sharesTotal, costmoneyTotal, userID) VALUES (:name, :symbol, :price, :sharesTotal, :costmoneyTotal, :userID)",
                          name=name, symbol=symbol, price=price, sharesTotal=sharesTotal_2, costmoneyTotal=costmoneyTotal_2, userID=session["user_id"])
                    # Update total TABLE
                    else:
                        db.execute("UPDATE total SET sharesTotal = :sharesTotal, costmoneyTotal = :costmoneyTotal WHERE userID = :userID and name = :name", sharesTotal=sharesTotal_2, costmoneyTotal=costmoneyTotal_2, userID=session["user_id"], name=name)

                    # SELECT all rows from total TABLE WHERE userID = session["user_id"]
                    total = db.execute("SELECT * FROM total WHERE userID = :userID", userID=session["user_id"])

                    # Len of total
                    tlen = len(total)

                    # Get user cash
                    cash = db.execute("SELECT cash FROM users WHERE id = :userID",
                          userID=session["user_id"])

                    cash = usd(cash[0]["cash"])

                    # Change price, costmoney to usd format
                    for n in range(tlen):
                        total[n]["price"] = usd(total[n]["price"])
                        total[n]["costmoneyTotal"] = usd(total[n]["costmoneyTotal"])
                    total = list(reversed(total))

                    # Flash
                    flash("buy")
                    return render_template("buyed.html", total=total, tlen=tlen, cash=cash)

                else:
                    # Else cash not enough
                    return apology("cash not enough", 400)

            else:
                # Else not positive number
                return apology("not positive number", 400)


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""

    # Check length of request.form.get("username")
    if not request.args.get("username"):
        return jsonify(False)

    # Query database for username
    rows = db.execute("SELECT * FROM users WHERE username = :username",
                      username=request.args.get("username"))



    # Ensure username not exists
    if not rows:
        return jsonify(True)
    else:
        return jsonify(False)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        # Select to buy-sell table
        bs = db.execute("SELECT * FROM bs WHERE userID=:userID", userID=session["user_id"])

        # len of buy sell table
        bslen = len(bs)

        # Falsh massage
        flash('history')

        # Rander buy sell and total return value list
        return render_template("history.html", bs=bs, bslen=bslen)

@app.route("/password", methods=["GET", "POST"])
def password():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username1", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Ensure password was confirmated
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("must provide confirmation password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1:
            return apology("invalid username", 403)
        else:
            # Get password from form
            password = request.form.get("password")

            # Hash password through Hash function
            hash0 = generate_password_hash(password)

            # Change database
            db.execute("UPDATE users SET hash = :hash1 WHERE username = :username", hash1=hash0, username=request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Falsh massage
        flash('password change')

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("password.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username1", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Falsh massage
        flash('login')

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Falsh massage
    flash('logout')

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # User reached route via GET (as by submitting a form via GET)
    if request.method == "GET":
        return render_template("quote.html")
    else:
        # Ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)

        # Get symbol
        symbol = request.form.get("symbol")

        # Check symbol
        symbol= lookup(symbol)

        # Ensure symbol is exist
        if not symbol:
            return apology("must provide right symbol", 400)

        return render_template("quoted.html",name=symbol.get("name"), symbol=symbol.get("symbol"), price=usd(symbol.get("price")))


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password") :
            return apology("must provide password", 400)

        # Ensure password was confirmated
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("must provide same password", 400)

        # Get password from form
        password = request.form.get("password")

        # Hash password through Hash function
        hash0 = generate_password_hash(password)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username not exists
        if not rows:
            db.execute("INSERT INTO users (username,hash) VALUES (:username,:hash1)",
                          username=request.form.get("username"), hash1 = hash0 )
        else:
            return apology("username can't be the same", 400)

        # Query database again for username
        rows_2 = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows_2[0]["id"]

        # Falsh massage
        flash('register!')

        # Redirect user to home page
        return redirect("/")


    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # User reached route via GET (as by submitting a form via GET)
    if request.method == "GET":

        # Select user symbol from total
        symbol_sel = db.execute("SELECT symbol FROM total WHERE userID = :userID", userID=session["user_id"])
        return render_template("sell.html", symbol_sel=symbol_sel, sslen=len(symbol_sel) )
    else:
        # Get symbol and number through input form
        symbol = request.form.get("symbol")
        number = request.form.get("shares")

        # Ensure sell symbol was submitted
        if not symbol:
            return apology("must provide symbol", 400)

        # Ensure sell number was submitted
        if not number:
            return apology("must provide number", 400)

        # Check if request.form.get("symbol") in lookup() table
        symbol = lookup(symbol)
        if not symbol:
            return apology("must provide right symbol", 400)
        else:

            # Get name, price, symbol from lookup function
            name = symbol.get("name")
            price = symbol.get("price")
            symbol = symbol.get("symbol")

            # SELECT symbol in TABLE total
            symbolIn = db.execute("SELECT symbol FROM total WHERE userID = :userID and symbol = :symbol",
                                  userID=session["user_id"], symbol=symbol)

            # Ensure user have this symbol
            if not symbolIn:
                return apology("you don't have this symbol", 400)

            # Ensure sell number is a number
            nlen = len(number)
            for i in range(nlen) :
                if number[i].isdigit() != True :
                    return apology("sell number need to be a number", 400)

            number = int(number)

            # Check positive number
            if number > 0:

                # SELECT sharesTotal in TABLE total
                symbolNum = db.execute("SELECT sharesTotal FROM total WHERE userID = :userID and symbol = :symbol",
                                      userID=session["user_id"], symbol=symbol)

                # Ensure user have sharesTotal
                if symbolNum[0]["sharesTotal"] < number:
                    return apology("you don't have this number", 400)

                # Selsct cash from user TABLE
                cash = db.execute("SELECT cash FROM users WHERE id = :userID",
                                      userID=session["user_id"])

                # Count total
                totalGet = price*number
                cash = cash[0]["cash"] + totalGet

                # Update csah in user
                db.execute("UPDATE users SET cash = :cash WHERE id = :userID", cash=cash, userID=session["user_id"])

                # Check sell time
                now = datetime.now(timezone('Asia/Shanghai'))

                # INSERT sell TABLE date, shares, price, name, symbol, totalGet
                db.execute("INSERT INTO sell (date, symbol, name, price, shares, totalGet, userID) VALUES (:date, :symbol, :name, :price, :shares, :totalGet, :userID)",date=now, symbol=symbol, name=name, price=price, shares=number, totalGet=totalGet, userID=session["user_id"])

                # Add to buy-sell table
                db.execute("INSERT INTO bs (symbol, price, shares, date, userID) VALUES (:symbol, :price, :shares, :date, :userID)", symbol=symbol, price=usd(price), shares=-number, date=now, userID=session["user_id"])

                # SELECT costmoneyTotal FROM total
                costTot = db.execute("SELECT costmoneyTotal FROM total WHERE userID = :userID and name = :name",
                                      userID=session["user_id"], name = name)

                # Change costmoneyTotal FROM total
                costTotEnd = costTot[0]["costmoneyTotal"]-totalGet

                # Update sharesTotal, costmoneyTotal total did by order
                db.execute("UPDATE total SET sharesTotal = :sharesTotal, costmoneyTotal = :costmoneyTotal WHERE userID = :userID and name = :name", sharesTotal=symbolNum[0]["sharesTotal"]-number, costmoneyTotal=costTotEnd, userID=session["user_id"], name=name)

                # Falsh massage
                flash('sell')

                # render selled template
                return render_template("selled.html",symbol=symbol, name=name, price=price, number=symbolNum[0]["sharesTotal"]-number, totalGet=usd(totalGet), costTotEnd=usd(cash))
            else:
                return apology("positive number", 400)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
