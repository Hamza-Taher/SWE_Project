from flask import Flask, request, session, render_template, redirect, url_for, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

# Import separated classes
from models.user import User
from models.passenger import Passenger
from models.pilot import Pilot
from models.crew import Crew

app = Flask(__name__)
app.secret_key = "secret_key_here"

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Htee2005#@275'
app.config['MYSQL_DB'] = 'rightdatabase'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


# ---------------------------------------------------------
# USERNAME GENERATION HELPERS
# ---------------------------------------------------------

def generate_username_passenger(first_name):
    cur = mysql.connection.cursor()
    cur.execute("SELECT username FROM passenger WHERE username LIKE %s", [first_name + "%"])
    existing = cur.fetchall()
    cur.close()

    if not existing:
        return first_name

    return f"{first_name}{len(existing)}"


def generate_username_pilot(first_name):
    cur = mysql.connection.cursor()
    cur.execute("SELECT username FROM pilot WHERE username LIKE %s", [first_name + "%"])
    existing = cur.fetchall()
    cur.close()

    if not existing:
        return first_name + "P"

    return f"{first_name}{len(existing)}P"


def generate_username_crew(first_name):
    cur = mysql.connection.cursor()
    cur.execute("SELECT username FROM crew WHERE username LIKE %s", [first_name + "%"])
    existing = cur.fetchall()
    cur.close()

    if not existing:
        return first_name + "C"

    return f"{first_name}{len(existing)}C"


# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------

@app.route('/')
def home():
    return render_template("home.html")


# ---------------------------------------------------------
# PASSENGER REGISTRATION
# ---------------------------------------------------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name'].strip().lower()
        last_name = request.form['last_name'].strip()
        email = request.form['email'].strip()
        passport_number = request.form['passport_number'].strip()
        phone_number = request.form['phone_number'].strip()
        password = request.form['password']

        if not all([first_name, last_name, email, passport_number, phone_number, password]):
            flash("All fields are required.", "error")
            return redirect(url_for('register'))

        username = generate_username_passenger(first_name)
        hashed_password = generate_password_hash(password)

        cur = mysql.connection.cursor()

        # Check email uniqueness
        cur.execute("SELECT id FROM passenger WHERE email = %s", [email])
        if cur.fetchone():
            flash("This email is already registered.", "error")
            cur.close()
            return redirect(url_for('register'))

        cur.execute("""
            INSERT INTO passenger 
            (username, password, first_name, last_name, email, passport_number, phone_number)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (username, hashed_password, first_name, last_name, email, passport_number, phone_number))

        mysql.connection.commit()
        cur.close()

        flash(f"Account created! Your username is: {username}", "success")
        return redirect(url_for('login'))

    return render_template("register.html")


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        # Admin login
        if username == "admin" and password == "adminpass":
            session['role'] = 'admin'
            session['username'] = 'admin'
            return redirect(url_for('admin'))

        cur = mysql.connection.cursor()

        # Pilot login
        cur.execute("SELECT * FROM pilot WHERE username = %s", [username])
        pilot_row = cur.fetchone()
        if pilot_row and check_password_hash(pilot_row['password'], password):
            session['role'] = 'pilot'
            session['username'] = username
            cur.close()
            return redirect(url_for('pilot'))

        # Crew login
        cur.execute("SELECT * FROM crew WHERE username = %s", [username])
        crew_row = cur.fetchone()
        if crew_row and check_password_hash(crew_row['password'], password):
            session['role'] = 'crew'
            session['username'] = username
            cur.close()
            return redirect(url_for('crew'))

        # Passenger login
        cur.execute("SELECT * FROM passenger WHERE username = %s", [username])
        passenger_row = cur.fetchone()
        if passenger_row and check_password_hash(passenger_row['password'], password):
            session['role'] = 'user'
            session['username'] = username
            cur.close()
            return redirect(url_for('add_passenger'))

        cur.close()
        flash("Invalid username or password.", "error")
        return redirect(url_for('login'))

    return render_template("login.html")


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


# ---------------------------------------------------------
# ADMIN DASHBOARD
# ---------------------------------------------------------

@app.route('/admin')
def admin():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    return render_template("admin.html")


# ---------------------------------------------------------
# ADMIN CREATES PILOT
# ---------------------------------------------------------

@app.route('/admin/create_pilot', methods=['GET', 'POST'])
def create_pilot():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        first_name = request.form['first_name'].strip().lower()
        last_name = request.form['last_name'].strip()
        passport_number = request.form['passport_number'].strip()
        phone_number = request.form['phone_number'].strip()
        password = request.form['password']

        username = generate_username_pilot(first_name)
        hashed = generate_password_hash(password)

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO pilot (username, password, first_name, last_name, passport_number, phone_number)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (username, hashed, first_name, last_name, passport_number, phone_number))
        mysql.connection.commit()
        cur.close()

        flash(f"Pilot created! Username is: {username}", "success")
        return redirect(url_for('admin'))

    return render_template("create_pilot.html")


# ---------------------------------------------------------
# ADMIN CREATES CREW
# ---------------------------------------------------------

@app.route('/admin/create_crew', methods=['GET', 'POST'])
def create_crew():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        first_name = request.form['first_name'].strip().lower()
        last_name = request.form['last_name'].strip()
        passport_number = request.form['passport_number'].strip()
        phone_number = request.form['phone_number'].strip()
        password = request.form['password']

        username = generate_username_crew(first_name)
        hashed = generate_password_hash(password)

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO crew (username, password, first_name, last_name, passport_number, phone_number)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (username, hashed, first_name, last_name, passport_number, phone_number))
        mysql.connection.commit()
        cur.close()

        flash(f"Crew member created! Username is: {username}", "success")
        return redirect(url_for('admin'))

    return render_template("create_crew.html")


# ---------------------------------------------------------
# ADMIN VIEWS LISTS
# ---------------------------------------------------------

@app.route('/admin/passengers')
def view_passengers():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM passenger")
    passengers = cur.fetchall()
    cur.close()

    return render_template("view_passengers.html", passengers=passengers)


@app.route('/admin/pilots')
def view_pilots():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM pilot")
    pilots = cur.fetchall()
    cur.close()

    return render_template("view_pilots.html", pilots=pilots)


@app.route('/admin/crews')
def view_crews():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM crew")
    crews = cur.fetchall()
    cur.close()

    return render_template("view_crews.html", crews=crews)


# ---------------------------------------------------------
# PILOT DASHBOARD
# ---------------------------------------------------------

@app.route('/pilot')
def pilot():
    if session.get('role') != 'pilot':
        return redirect(url_for('login'))
    return render_template("pilot.html", username=session.get('username'))


# ---------------------------------------------------------
# CREW DASHBOARD
# ---------------------------------------------------------

@app.route('/crew')
def crew():
    if session.get('role') != 'crew':
        return redirect(url_for('login'))
    return render_template("crew.html", username=session.get('username'))


# ---------------------------------------------------------
# PASSENGER DASHBOARD
# ---------------------------------------------------------

@app.route('/add_passenger', methods=['GET', 'POST'])
def add_passenger():
    if session.get('role') != 'user':
        return redirect(url_for('login'))

    username = session.get('username')
    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM passenger WHERE username = %s", [username])
    passenger_row = cur.fetchone()

    # Convert DB row → Passenger object (optional but clean)
    passenger = Passenger(
        username=passenger_row["username"],
        first_name=passenger_row["first_name"],
        last_name=passenger_row["last_name"],
        email=passenger_row["email"],
        passport_number=passenger_row["passport_number"],
        phone_number=passenger_row["phone_number"],
         flight_number=passenger_row["flight_number"]
    )

    if request.method == 'POST':
        flight_number = request.form['flight_number']
        cur.execute("UPDATE passenger SET flight_number = %s WHERE username = %s",
                    (flight_number, username))
        mysql.connection.commit()
        cur.close()
        flash("Flight information updated!", "success")
        return redirect(url_for('add_passenger'))

    cur.close()
    return render_template("add_passenger.html", passenger=passenger)


# ---------------------------------------------------------
# RUN APP
# ---------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)