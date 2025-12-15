from flask import Flask, request, session, render_template, redirect, url_for, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret_key_here"

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Htee2005#@275'
app.config['MYSQL_DB'] = 'rightdatabase'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # return rows as dicts

mysql = MySQL(app)

# ---------- Optional classes (not required for logic) ----------

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password


class Passenger(User):
    pass


class CrewMember(User):
    pass


class Pilot(CrewMember):
    pass



# ---------- Home ----------

@app.route('/')
def home():
    return render_template("home.html")


# ---------- Registration (passenger only) ----------

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Register a new PASSENGER account.
    - Username must be unique across passenger, pilot, and crew.
    - Pilot and crew accounts are created by admin only.
    """
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        if not username or not password:
            flash("All fields are required.", "error")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        cur = mysql.connection.cursor()

        # Check if username exists in passenger
        cur.execute("SELECT id FROM passenger WHERE username = %s", [username])
        if cur.fetchone():
            flash("Username already exists as a passenger.", "error")
            cur.close()
            return redirect(url_for('register'))

        # Check if username exists in pilot
        cur.execute("SELECT id FROM pilot WHERE username = %s", [username])
        if cur.fetchone():
            flash("Username already exists as a pilot.", "error")
            cur.close()
            return redirect(url_for('register'))

        # Check if username exists in crew
        cur.execute("SELECT id FROM crew WHERE username = %s", [username])
        if cur.fetchone():
            flash("Username already exists as crew.", "error")
            cur.close()
            return redirect(url_for('register'))

        # Create a passenger account by default
        try:
            cur.execute(
                "INSERT INTO passenger (username, password) VALUES (%s, %s)",
                (username, hashed_password)
            )
            mysql.connection.commit()
            flash("Passenger account created successfully! Please log in.", "success")
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error creating account: {e}", "error")
        finally:
            cur.close()

        return redirect(url_for('login'))

    return render_template("register.html")


# ---------- Login / Logout ----------

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login logic:
    - admin (hard-coded)
    - pilot (pilot table)
    - crew (crew table)
    - passenger (passenger table)
    """
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        # Admin check (hard-coded)
        if username == "admin" and password == "adminpass":
            session['role'] = 'admin'
            session['username'] = 'admin'
            return redirect(url_for('admin'))

        cur = mysql.connection.cursor()

        # Pilot login
        cur.execute("SELECT * FROM pilot WHERE username = %s", [username])
        pilot = cur.fetchone()
        if pilot and check_password_hash(pilot['password'], password):
            session['role'] = 'pilot'
            session['username'] = username
            cur.close()
            return redirect(url_for('pilot'))

        # Crew login
        cur.execute("SELECT * FROM crew WHERE username = %s", [username])
        crew = cur.fetchone()
        if crew and check_password_hash(crew['password'], password):
            session['role'] = 'crew'
            session['username'] = username
            cur.close()
            return redirect(url_for('crew'))

        # Passenger login (user role)
        cur.execute("SELECT * FROM passenger WHERE username = %s", [username])
        passenger = cur.fetchone()
        if passenger and check_password_hash(passenger['password'], password):
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


# ---------- Admin dashboard & admin-only actions ----------

@app.route('/admin')
def admin():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    return render_template("admin.html", username=session.get('username'))


@app.route('/admin/create_pilot', methods=['GET', 'POST'])
def create_pilot():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        if not username or not password:
            flash("Both fields are required.", "error")
            return redirect(url_for('create_pilot'))

        hashed = generate_password_hash(password)
        cur = mysql.connection.cursor()

        # Check collisions with existing usernames
        cur.execute("SELECT id FROM pilot WHERE username = %s", [username])
        if cur.fetchone():
            flash("Username already exists as a pilot.", "error")
            cur.close()
            return redirect(url_for('create_pilot'))

        cur.execute("SELECT id FROM passenger WHERE username = %s", [username])
        if cur.fetchone():
            flash("Username already exists as a passenger.", "error")
            cur.close()
            return redirect(url_for('create_pilot'))

        cur.execute("SELECT id FROM crew WHERE username = %s", [username])
        if cur.fetchone():
            flash("Username already exists as crew.", "error")
            cur.close()
            return redirect(url_for('create_pilot'))

        cur.execute("INSERT INTO pilot (username, password) VALUES (%s, %s)", (username, hashed))
        mysql.connection.commit()
        cur.close()

        flash("Pilot account created successfully!", "success")
        return redirect(url_for('admin'))

    return render_template("create_pilot.html")


@app.route('/admin/create_crew', methods=['GET', 'POST'])
def create_crew():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        if not username or not password:
            flash("Both fields are required.", "error")
            return redirect(url_for('create_crew'))

        hashed = generate_password_hash(password)
        cur = mysql.connection.cursor()

        # Check collisions with existing usernames
        cur.execute("SELECT id FROM crew WHERE username = %s", [username])
        if cur.fetchone():
            flash("Username already exists as crew.", "error")
            cur.close()
            return redirect(url_for('create_crew'))

        cur.execute("SELECT id FROM passenger WHERE username = %s", [username])
        if cur.fetchone():
            flash("Username already exists as a passenger.", "error")
            cur.close()
            return redirect(url_for('create_crew'))

        cur.execute("SELECT id FROM pilot WHERE username = %s", [username])
        if cur.fetchone():
            flash("Username already exists as a pilot.", "error")
            cur.close()
            return redirect(url_for('create_crew'))

        cur.execute("INSERT INTO crew (username, password) VALUES (%s, %s)", (username, hashed))
        mysql.connection.commit()
        cur.close()

        flash("Crew account created successfully!", "success")
        return redirect(url_for('admin'))

    return render_template("create_crew.html")


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


# ---------- Pilot & crew dashboards ----------

@app.route('/pilot')
def pilot():
    if session.get('role') != 'pilot':
        return redirect(url_for('login'))
    return render_template("pilot.html", username=session.get('username'))


@app.route('/crew')
def crew():
    if session.get('role') != 'crew':
        return redirect(url_for('login'))
    return render_template("crew.html", username=session.get('username'))


# ---------- Passenger add/update flight info ----------

@app.route('/add_passenger', methods=['GET', 'POST'])
def add_passenger():
    """
    For logged-in passengers (role 'user'):
    - On GET: show form with their existing data (if any)
    - On POST: update their own record (name, passport, flight)
      in the passenger table, matched by username.
    """
    if session.get('role') != 'user':
        return redirect(url_for('login'))

    username = session.get('username')
    cur = mysql.connection.cursor()

    # Get existing data for this passenger (if any)
    cur.execute("SELECT * FROM passenger WHERE username = %s", [username])
    passenger = cur.fetchone()

    if request.method == 'POST':
        name = request.form['name']
        passport_number = request.form['passport_number']
        flight_number = request.form['flight_number']

        if passenger:
            # Update existing record
            cur.execute(
                """
                UPDATE passenger
                SET name = %s, passport_number = %s, flight_number = %s
                WHERE username = %s
                """,
                (name, passport_number, flight_number, username)
            )
        else:
            # Fallback: create full record if somehow missing
            cur.execute(
                """
                INSERT INTO passenger (username, password, name, passport_number, flight_number)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (username, generate_password_hash("temp1234"), name, passport_number, flight_number)
            )

        mysql.connection.commit()
        cur.close()
        flash("Passenger data saved successfully!", "success")
        return redirect(url_for('add_passenger'))

    cur.close()
    return render_template("add_passenger.html", username=username, passenger=passenger)


if __name__ == '__main__':
    app.run(debug=True)