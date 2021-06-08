from flask import Flask, render_template, request, jsonify
import sqlite3 as sql
import re
import webcolors

# app - The flask application where all the magical things are configured.
app = Flask(__name__)

# Constants - Stuff that we need to know that won't ever change!
DATABASE_FILE = "database.db"
DEFAULT_BUGGY_ID = "1"
BUGGY_RACE_SERVER_URL = "https://rhul.buggyrace.net"

#------------------------------------------------------------
# the index page
#------------------------------------------------------------
@app.route('/')
def home():
    return render_template('index.html', server_url=BUGGY_RACE_SERVER_URL)

#------------------------------------------------------------
# creating a new buggy:
#  if it's a POST request process the submitted data
#  but if it's a GET request, just show the form
#------------------------------------------------------------
@app.route('/new', methods = ['POST', 'GET'])
def create_buggy():
    if request.method == 'GET':
        # con = sql.connect(DATABASE_FILE)
        # con.row_factory = sql.Row
        # cur = con.cursor()
        # cur.execute("SELECT * FROM buggies")
        # record = cur.fetchone();
        return render_template("buggy-form.html", buggy = None)
    elif request.method == 'POST':
        msg=""
        qty_wheels = request.form['qty_wheels'].strip()
        tyres = request.form['tyres']
        qty_tyres = request.form['qty_tyres'].strip()
        flag_color = request.form['flag_color'].strip()
        flag_color_secondary = request.form['flag_color_secondary'].strip()
        flag_pattern = request.form['flag_pattern']
        power_type = request.form['power_type']
        power_units = request.form['power_units'].strip()
        autofill = request.form['autofill']
        buggy_id = request.form['id']

        con = sql.connect(DATABASE_FILE)
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM buggies WHERE id=?", (buggy_id,))
        record = cur.fetchone();

        if autofill == "auto":
            qty_wheels = "4"
            tyres = "knobbly"
            qty_tyres = "4"
            flag_color = "purple"
            flag_color_secondary = "orange"
            flag_pattern = "plain"
            power_type = "petrol"
            power_units = "25"

        if qty_wheels == "":
            qty_wheels = "4"
        if not qty_wheels.isdigit():
            msg = f"Not an integer, you inputted: {qty_wheels}, Please input a whole number for example: 4"
            return render_template("buggy-form.html", msg = msg, buggy = record)
        if (int(qty_wheels) % 2) != 0:
            msg = f"Not an even number, you inputted: {qty_wheels}, Please input an even number for example: 8"
            return render_template("buggy-form.html", msg = msg, buggy = record)
        if int(qty_wheels) < 1:
            msg = f"Not a number greater than 0, you inputted: {qty_wheels}, Please input a number greater than 0 for example: 6"
            return render_template("buggy-form.html", msg = msg, buggy = record)

        if qty_tyres == "":
            qty_tyres = qty_wheels
        if tyres == "":
            tyres = "knobbly"

        if not qty_tyres.isdigit():
            msg = f"Not an integer, you inputted: {qty_tyres}, Please input a whole number for example: 4"
            return render_template("buggy-form.html", msg = msg, buggy = record)
        if (int(qty_tyres)) < int(qty_wheels):
            msg = f"Less tyres than wheels you inputted: {qty_wheels}, Please input a number of tryes greater than or equal to number of tyres"
            return render_template("buggy-form.html", msg = msg, buggy = record)

        if flag_color == "":
            flag_color = "purple"
        try:
            flag_color = webcolors.name_to_hex(flag_color)
        except:
            match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', flag_color)
            if not match:
                msg = f"Not a hex: {flag_color}, Please input a hex code for example: #ffffff"
                return render_template("buggy-form.html", msg = msg, buggy = record)

        if flag_color_secondary == "":
            flag_color_secondary = "orange"
        try:
            flag_color_secondary = webcolors.name_to_hex(flag_color_secondary)
        except:
            match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', flag_color_secondary)
            if not match:
                msg = f"Not a hex: {flag_color_secondary}, Please input a hex code for example: #ffffff"
                return render_template("buggy-form.html", msg = msg, buggy = record)

        if flag_pattern == "":
            flag_pattern = "plain"

        if power_units == "":
            power_units = "25"
        if power_type == "":
            power_type = "petrol"

        if not power_units.isdigit():
            msg = f"Not an integer, you inputted: {power_units}, Please input a whole number for example: 5"
            return render_template("buggy-form.html", msg = msg, buggy = record)

        if int(power_units) < 1:
            msg = f"Not a number greater than 0, you inputted: {power_units}, Please input a number greater than 0 for example: 100"
            return render_template("buggy-form.html", msg = msg, buggy = record)

        #cost calulation
        total_cost = total_cost_calc(power_type, power_units, tyres, qty_tyres)
        #print(total_cost)



        try:
            with sql.connect(DATABASE_FILE) as con:
                cur = con.cursor()
                if buggy_id:
                    cur.execute(
                    "UPDATE buggies set qty_wheels=?, flag_color=?, flag_color_secondary=?, flag_pattern=?, power_type=?, power_units=?, total_cost=?, tyres =?, qty_tyres=?  WHERE id=?",
                    (qty_wheels, flag_color, flag_color_secondary, flag_pattern, power_type, power_units, total_cost, tyres, qty_tyres, buggy_id)
                    )
                else:
                    cur.execute(
                        "INSERT INTO buggies (qty_wheels, flag_color, flag_color_secondary, flag_pattern, power_type, power_units, total_cost, tyres, qty_tyres) VALUES(?,?,?,?,?,?,?,?,?)",
                        (qty_wheels, flag_color, flag_color_secondary, flag_pattern, power_type, power_units, total_cost, tyres, qty_tyres,)
                    )
                    con.commit()
                msg = f"You have created a buggy with: {qty_wheels} wheels and a {flag_color} flag"
        except:
            con.rollback()
            msg = "error in update operation"
        finally:
            con.close()
        return render_template("updated.html", msg = msg)

def total_cost_calc(power_type, power_units, tyres, qty_tyres):
    total_cost = 0
    if power_type == "petrol":
        total_cost = 4 * int(power_units)
    if power_type == "fusion":
        total_cost = 400 * int(power_units)
    if power_type == "steam":
        total_cost = 3 * int(power_units)
    if power_type == "bio":
        total_cost = 5 * int(power_units)
    if power_type == "electric":
        total_cost = 20 * int(power_units)
    if power_type == "rocket":
        total_cost = 16 * int(power_units)
    if power_type == "hamster":
        total_cost = 3 * int(power_units)
    if power_type == "thermo":
        total_cost = 300 * int(power_units)
    if power_type == "solar":
        total_cost = 40 * int(power_units)
    if power_type == "wind":
        total_cost = 20 * int(power_units)
    if tyres == "knobbly":
        total_cost += 15 * int(qty_tyres)
    if tyres == "slick":
        total_cost += 10 * int(qty_tyres)
    if tyres == "steelband":
        total_cost += 20 * int(qty_tyres)
    if tyres == "reactive":
        total_cost += 40 * int(qty_tyres)
    if tyres == "maglev":
        total_cost += 50 * int(qty_tyres)
    return(total_cost)


#------------------------------------------------------------
# a page for displaying the buggy
#------------------------------------------------------------
@app.route('/buggy')
def show_buggies():
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies")
    records = cur.fetchall();
    return render_template("buggy.html", buggies = records)

#------------------------------------------------------------
# a placeholder page for editing the buggy: you'll need
# to change this when you tackle task 2-EDIT
#------------------------------------------------------------
@app.route('/edit/<buggy_id>')
def edit_buggy(buggy_id):
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies WHERE id=?", (buggy_id,))
    record = cur.fetchone();
    return render_template("buggy-form.html", buggy=record)

#------------------------------------------------------------
# You probably don't need to edit this... unless you want to ;)
#
# get JSON from current record
#  This reads the buggy record from the database, turns it
#  into JSON format (excluding any empty values), and returns
#  it. There's no .html template here because it's *only* returning
#  the data, so in effect jsonify() is rendering the data.
#------------------------------------------------------------
@app.route('/json')
def summary():
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies WHERE id=? LIMIT 1", (DEFAULT_BUGGY_ID))

    buggies = dict(zip([column[0] for column in cur.description], cur.fetchone())).items()
    return jsonify({ key: val for key, val in buggies if (val != "" and val is not None) })

# You shouldn't need to add anything below this!
if __name__ == '__main__':
    app.run(debug = True, host="0.0.0.0")
