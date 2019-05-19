@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("buy.html")
    else:
        symbol_check = request.form.get("symbol")
        if not symbol_check:
            return apology("must provide symbol", 400)
        # Check if symbol exist in lookup(symbol)

        symbol_check2 = lookup(symbol_check)
        symbol_name = symbol_check2.get('name')
        symbol_price = symbol_check2.get('price')
        symbol_symbol = symbol_check2.get('symbol')
        if not symbol_check2 or not symbol_name or not symbol_symbol or not symbol_price:
            return apology("symbol doesn't exist,sorry", 400)
        else:


            # Check if shares of name is a integer
            shares = request.form.get("shares")

            # https://www.geeksforgeeks.org/program-check-input-integer-string/
            number_shares = len(shares)
            for i in range(number_shares) :
                if shares[i].isdigit() != True :
                    return apology("shares need to be a number", 400)

                elif shares > 0:

                    # Query database for user's cash
                    userCash = db.execute("SELECT cash FROM users WHERE id = :userID",
                              userID=session["user_id"])


                    # Check user if have enough money
                    buyNeed = shares*symbol_price
                    if userCash > buyNeed:
                        # Check purchasetime
                        now = datetime.now(timezone('China/Beijing'))

                        # Add to buy table
                        db.execute("INSERT INTO buy (date,symbol,name,shares,purchasePrice,costmoney,userID) VALUES (:date,:symbol,:name,:shares,:purchasePrice,:costmoney,:userID)",
                              data=now,symbol=symbol_symbol,name=symbol_name,shares=shares,purchasePrice=symbol_price,costmoney=buyNeed,userID=session["user_id"])

                        endCash=userCash-buyNeed
                        # Update csah in user
                        db.execute("UPDATE users SET cash = :cash WHERE id = :userID",cash=endCash,userID=session["user_id"])

                        # Ensure return total shares and costmoney
                        sharesTotal = db.execute("SELECT shares FROM buy WHERE id = :userID and symbol = :symbol",userID=session["user_id"],symbol=symbol_check2)
                        costmoneyTotal = db.execute("SELECT costmoney FROM buy WHERE id = :userID and symbol = :symbol",userID=session["user_id"],symbol=symbol_check2)

                        sharesTotal_2 = sum(sharesTotal)
                        costmoneyTotal_2 = sum(costmoneyTotal)

                        return render_template("buyed.html",symbol_check2,sharesTotal_2,costmoneyTotal_2)



                    else:
                        return apology("cash not enough",400)



                else:
                    return apology("positive number",400)





    return apology("TODO")


CREATE TABLE 'buy' ('id' integer PRIMARY KEY AUTOINCREMENT NOT NULL, 'date' datetime NOT NULL, 'symbol' text NOT NULL, 'name' text NOT NULL, 'price' double precision NOT NULL, 'shares' integer NOT NULL, 'costmoney' double precision NOT NULL, 'userID' integer NOT NULL)
db.execute("INSERT INTO total (name, symbol, price, sharesTotal, costmoneyTotal, userID) VALUES (:name, :symbol, :price, :sharesTotal, :costmoneyTotal, :userID)",
                              name=symbol_name, symbol=symbol_symbol, price=symbol_price, sharesTotal=sharesTotal_2, costmoneyTotal=costmoneyTotal_2, userID=session["user_id"])

                              , price, sharesTotal, costmoneyTotal