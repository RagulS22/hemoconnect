from flask import Flask, render_template, request, redirect, session
from datetime import datetime, timedelta
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "blood.db")

app = Flask(__name__)
app.secret_key = "mysecretkey"

@app.route("/")
def home():
    return render_template("index.html")

    
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        blood_group = request.form["blood_group"]
        phone = request.form["phone"]
        city = request.form["city"]
        age = request.form["age"]
        last_donated = request.form["last_donated"]
        units = request.form["units"]
        availability = request.form["availability"]
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO donors
        (name,blood_group,phone,city,age,last_donated,units,availability,username,password)
        VALUES (?,?,?,?,?,?,?,?,?,?)
        """,(name,blood_group,phone,city,age,last_donated,units,availability,username,password))

        conn.commit()
        conn.close()

        return redirect("/donors")

    return render_template("register.html")
    
@app.route("/donors")
def donors():

    blood_group = request.args.get("blood_group")

    conn = sqlite3.connect("blood.db")
    cursor = conn.cursor()

    if blood_group:
        cursor.execute("SELECT * FROM donors WHERE blood_group=?", (blood_group,))
    else:
        cursor.execute("SELECT * FROM donors")

    donors = cursor.fetchall()

    new_donors = []

    for donor in donors:

        last_donated = donor[6]

        try:
            last_date = datetime.strptime(last_donated, "%Y-%m-%d")
            next_date = last_date + timedelta(days=90)
            eligible = "Yes" if datetime.today() >= next_date else "No"
        except:
            eligible = "Unknown"

        donor = list(donor)
        donor.append(eligible)

        new_donors.append(donor)

    conn.close()

    return render_template("donors.html", donors=new_donors)

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "ragul" and password == "221006":
            session["admin"] = True
            return redirect("/admin_dashboard")
        else:
            error = "Invalid Credentials"

    return render_template("admin_login.html", error=error)

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/")

@app.route("/search", methods=["GET","POST"])
def search():

    blood_group = request.form.get("blood_group")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM donors WHERE blood_group=?", (blood_group,))
    donors = cursor.fetchall()

    conn.close()

    return render_template("donors.html", donors=donors)

@app.route("/delete/<int:id>")
def delete(id):

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM donors WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/donors")

@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit_donor(id):

    conn = sqlite3.connect("blood.db")
    cursor = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        blood = request.form["blood_group"]
        phone = request.form["phone"]
        city = request.form["city"]
        availability = request.form["availability"]

        cursor.execute("""
        UPDATE donors
        SET name=?, blood_group=?, phone=?, city=?, availability=?
        WHERE id=?
        """,(name,blood,phone,city,availability,id))

        conn.commit()
        conn.close()

        return redirect("/donors")

    cursor.execute("SELECT * FROM donors WHERE id=?", (id,))
    donor = cursor.fetchone()

    conn.close()

    return render_template("edit.html", donor=donor)

@app.route("/donor_login", methods=["GET","POST"])
def donor_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("blood.db")
        cur = conn.cursor()

        cur.execute("SELECT * FROM donors WHERE username=? AND password=?", (username,password))
        donor = cur.fetchone()

        conn.close()

        if donor:
            session["donor"] = username
            return redirect("/donor_dashboard")
        else:
            return "Invalid Username or Password"

    return render_template("donor_login.html")

@app.route("/donor_dashboard")
def donor_dashboard():

    if "donor" not in session:
        return redirect("/donor_login")

    username = session["donor"]

    conn = sqlite3.connect("blood.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM donors WHERE username=?", (username,))
    donor = cursor.fetchone()

    conn.close()

    return render_template("donor_dashboard.html", donor=donor)

@app.route("/toggle_availability")
def toggle_availability():

    if "donor" not in session:
        return redirect("/donor_login")

    username = session["donor"]

    conn = sqlite3.connect("blood.db")
    cursor = conn.cursor()

    cursor.execute("SELECT availability FROM donors WHERE username=?", (username,))
    current = cursor.fetchone()[0]

    if current == "Available":
        new_status = "Not Available"
    else:
        new_status = "Available"

    cursor.execute("UPDATE donors SET availability=? WHERE username=?", (new_status, username))

    conn.commit()
    conn.close()

    return redirect("/donor_dashboard")

@app.route("/donor_edit", methods=["GET","POST"])
def donor_edit():

    if "donor" not in session:
        return redirect("/donor_login")

    username = session["donor"]

    conn = sqlite3.connect("blood.db")
    cursor = conn.cursor()

    if request.method == "POST":

        phone = request.form["phone"]
        city = request.form["city"]
        availability = request.form["availability"]

        cursor.execute("""
        UPDATE donors
        SET phone=?, city=?, availability=?
        WHERE username=?
        """,(phone,city,availability,username))

        conn.commit()
        conn.close()

        return redirect("/donor_dashboard")

    cursor.execute("SELECT * FROM donors WHERE username=?", (username,))
    donor = cursor.fetchone()

    conn.close()

    return render_template("donor_edit.html", donor=donor)

@app.route("/admin_dashboard")
def admin_dashboard():

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Total donors
    cursor.execute("SELECT COUNT(*) FROM donors")
    total_donors = cursor.fetchone()[0]

    # Available donors
    cursor.execute("SELECT COUNT(*) FROM donors WHERE availability='Available'")
    available_donors = cursor.fetchone()[0]

    # Not available donors
    cursor.execute("SELECT COUNT(*) FROM donors WHERE availability='Not Available'")
    not_available = cursor.fetchone()[0]

    # Blood group chart
    cursor.execute("SELECT blood_group, COUNT(*) FROM donors GROUP BY blood_group")
    data = cursor.fetchall()

    labels = []
    values = []

    for row in data:
        labels.append(row[0])
        values.append(row[1])

    conn.close()

    return render_template(
        "admin_dashboard.html",
        total_donors=total_donors,
        available_donors=available_donors,
        not_available=not_available,
        labels=labels,
        values=values
    )

@app.route("/request_blood", methods=["GET","POST"])
def request_blood():

    if request.method == "POST":

        blood_group = request.form["blood_group"]

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM donors 
        WHERE blood_group=? AND availability='Available'
        """,(blood_group,))

        donors = cursor.fetchall()

        conn.close()

        return render_template("donors.html", donors=donors)

    return render_template("request_blood.html")

if __name__ == "__main__":
    app.run(debug=True)

