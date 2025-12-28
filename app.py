from flask import Flask, request, session, render_template, redirect, url_for, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

# Import separated classes
from models.user import User
from models.passenger import Passenger
from models.pilot import Pilot
from models.crew import Crew
from models.plane import Plane
from models.seat import Seat
from models.flight import Flight

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
# ADMIN CREATES PLANE
# ---------------------------------------------------------

@app.route('/admin/create_plane', methods=['GET', 'POST'])
def create_plane():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        model = request.form['model'].strip()
        capacity = int(request.form['capacity'])
        seats_A = int(request.form['seats_A'])
        seats_B = int(request.form['seats_B'])
        seats_C = int(request.form['seats_C'])

        # Validate seat distribution
        if seats_A + seats_B + seats_C != capacity:
            flash("Seat distribution does not match plane capacity!", "error")
            return redirect(url_for('create_plane'))

        # Insert plane
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO plane (model, capacity, seats_A, seats_B, seats_C)
            VALUES (%s, %s, %s, %s, %s)
        """, (model, capacity, seats_A, seats_B, seats_C))
        mysql.connection.commit()

        plane_id = cur.lastrowid  # get new plane ID

        # Auto-generate seats
        for _ in range(seats_A):
            cur.execute("INSERT INTO seat (plane_id, seat_class, is_available) VALUES (%s, 'A', TRUE)", [plane_id])

        for _ in range(seats_B):
            cur.execute("INSERT INTO seat (plane_id, seat_class, is_available) VALUES (%s, 'B', TRUE)", [plane_id])

        for _ in range(seats_C):
            cur.execute("INSERT INTO seat (plane_id, seat_class, is_available) VALUES (%s, 'C', TRUE)", [plane_id])

        mysql.connection.commit()
        cur.close()

        flash("Plane and seats created successfully!", "success")
        return redirect(url_for('admin'))

    return render_template("create_plane.html")


# ---------------------------------------------------------
# PILOT DASHBOARD
# ---------------------------------------------------------

@app.route('/pilot')
def pilot():
    if session.get('role') != 'pilot':
        return redirect(url_for('login'))
    return render_template("pilot.html", username=session.get('username'))


# ---------------------------------------------------------
# CREW DASHBOARD & TASKS
# ---------------------------------------------------------

@app.route('/crew')
def crew():
    if session.get('role') != 'crew':
        return redirect(url_for('login'))

    username = session.get('username')
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT f.id, f.flight_date, f.departure_time, f.arrival_time, 
               src.name AS source_airport, dest.name AS dest_airport
        FROM flight f
        JOIN crew_flight cf ON f.id = cf.flight_id
        JOIN crew c ON cf.crew_id = c.id
        JOIN airport src ON f.source_id = src.id
        JOIN airport dest ON f.dest_id = dest.id
        WHERE c.username = %s
        ORDER BY f.flight_date, f.departure_time
    """, [username])
    
    tasks = cur.fetchall()
    cur.close()

    return render_template("crew.html", username=username, tasks=tasks)


# ---------------------------------------------------------
# PASSENGER DASHBOARD
# ---------------------------------------------------------

@app.route('/add_passenger', methods=['GET', 'POST'])
def add_passenger():
    if session.get('role') != 'user':
        return redirect(url_for('login'))

    username = session.get('username')
    cur = mysql.connection.cursor()

    # Get passenger info
    cur.execute("SELECT * FROM passenger WHERE username = %s", [username])
    row = cur.fetchone()

    passenger = Passenger(
        username=row["username"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        email=row["email"],
        passport_number=row["passport_number"],
        phone_number=row["phone_number"],
        flight_number=row.get("flight_number") if "flight_number" in row else None
    )

    # Handle update
    if request.method == 'POST':
        flight_number = request.form['flight_number']
        cur.execute("UPDATE passenger SET flight_number = %s WHERE username = %s",
                    (flight_number, username))
        mysql.connection.commit()
        flash("Flight updated!", "success")
        return redirect(url_for('add_passenger'))

    # PROBLEM SOLVED: Added Date Filtering to hide past flights
    cur.execute("""
        SELECT f.id, a.name AS destination, f.flight_date, f.departure_time, f.arrival_time
        FROM flight f
        INNER JOIN airport a ON f.dest_id = a.id
        WHERE f.flight_date >= CURDATE()
        ORDER BY f.flight_date, f.departure_time
    """)
    flights = cur.fetchall()
    cur.close()

    return render_template("add_passenger.html", passenger=passenger, flights=flights)


# ---------------------------------------------------------
# PASSENGER VIEWS FLIGHTS
# ---------------------------------------------------------

@app.route('/add_passenger/flights')
def passenger_flights():
    if session.get('role') != 'user':
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    # PROBLEM SOLVED: Added Date Filtering here as well
    cur.execute("""
        SELECT f.id, a.name AS destination, f.flight_date, f.departure_time,
                 f.arrival_time, f.cost
        FROM flight f
        INNER JOIN airport a ON f.dest_id = a.id
        WHERE f.flight_date >= CURDATE()
        ORDER BY f.flight_date, f.departure_time
    """)
    flights = cur.fetchall()
    cur.close()

    return render_template("passenger_flight.html", flights=flights)


# ---------------------------------------------------------
# ADMIN CREATES AIRPORT
# ---------------------------------------------------------

@app.route('/admin/create_airport', methods=['GET', 'POST'])
def create_airport():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        country = request.form['country'].strip()
        city = request.form['city'].strip()
        name = request.form['name'].strip()

        if not all([country, city, name]):
            flash("All fields are required.", "error")
            return redirect(url_for('create_airport'))

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO airport (country, city, name)
            VALUES (%s, %s, %s)
        """, (country, city, name))
        mysql.connection.commit()
        cur.close()

        flash("Airport added successfully!", "success")
        return redirect(url_for('admin'))

    return render_template("create_airport.html")


# ---------------------------------------------------------
# ADMIN CREATES FLIGHT
# ---------------------------------------------------------

@app.route('/admin/create_flight', methods=['GET', 'POST'])
def create_flight():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, username FROM pilot")
    pilots = cur.fetchall()
    cur.execute("SELECT id, model FROM plane")
    planes = cur.fetchall()
    cur.execute("SELECT id, name, city FROM airport")
    airports = cur.fetchall()
    
    # PROBLEM SOLVED: Added this line to fetch the crew members so they appear in the dropbox
    cur.execute("SELECT id, username FROM crew")
    crews = cur.fetchall()
    cur.close()

    if request.method == 'POST':
        source_id = request.form['source_id']
        dest_id = request.form['dest_id']
        pilot_id = request.form['pilot_id']
        plane_id = request.form['plane_id']
        departure_time = request.form['departure_time']
        arrival_time = request.form['arrival_time']
        flight_date = request.form['flight_date']
        distance_km = request.form['distance_km']
        cost = request.form.get('cost', 0) 
        crew_ids = request.form.getlist('crew_ids') 

        cur = mysql.connection.cursor()
        # 2. Insert the flight first
        cur.execute("""
            INSERT INTO flight (source_id, dest_id, pilot_id, plane_id,
                                departure_time, arrival_time, flight_date, distance_km, cost)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (source_id, dest_id, pilot_id, plane_id, departure_time, arrival_time, flight_date, distance_km, cost))
        
        flight_id = cur.lastrowid # Get the ID of the flight we just made

        # 3. LINK THE CREW: This is the part that makes flights appear in the portal!
        for c_id in crew_ids:
            cur.execute("INSERT INTO crew_flight (crew_id, flight_id) VALUES (%s, %s)", (c_id, flight_id))

        mysql.connection.commit()
        cur.close()
        flash("Flight created and crew assigned!", "success")
        return redirect(url_for('admin'))

    # PROBLEM SOLVED: You MUST pass 'crews' here so the HTML can see them
    return render_template("create_flight.html", pilots=pilots, planes=planes, airports=airports, crews=crews)


# ---------------------------------------------------------
# USER VIEWS FLIGHTS
# ---------------------------------------------------------

@app.route('/flights')
def flights():
    if session.get('role') != 'user':
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    # PROBLEM SOLVED: Added Date Filtering to hide past flights
    cur.execute("""
        SELECT f.id, 
               src.name AS source, 
               dest.name AS destination, 
               f.flight_date, 
               f.departure_time, 
               f.arrival_time,
               f.cost
        FROM flight f
        INNER JOIN airport src ON f.source_id = src.id
        INNER JOIN airport dest ON f.dest_id = dest.id
        WHERE f.flight_date >= CURDATE()
        ORDER BY f.flight_date, f.departure_time
    """)
    flights = cur.fetchall()
    cur.close()

    return render_template("flights.html", flights=flights)

# ---------------------------------------------------------
# PILOT ASSIGNED TASKS (FLIGHTS)
# ---------------------------------------------------------

@app.route('/pilot/tasks')
def pilot_tasks():
    if session.get('role') != 'pilot':
        return redirect(url_for('login'))

    username = session.get('username')
    cur = mysql.connection.cursor()

    cur.execute("SELECT id FROM pilot WHERE username = %s", [username])
    pilot_data = cur.fetchone()
    
    if not pilot_data:
        flash("Pilot record not found.", "error")
        return redirect(url_for('home'))

    cur.execute("""
        SELECT f.id, f.flight_date, f.departure_time, f.arrival_time, 
               src.name AS source_airport, dest.name AS dest_airport, p.model as plane_model
        FROM flight f
        JOIN airport src ON f.source_id = src.id
        JOIN airport dest ON f.dest_id = dest.id
        JOIN plane p ON f.plane_id = p.id
        WHERE f.pilot_id = %s
        ORDER BY f.flight_date, f.departure_time
    """, [pilot_data['id']])
    
    tasks = cur.fetchall()
    cur.close()

    return render_template("pilot_tasks.html", tasks=tasks)


# ---------------------------------------------------------
# CREW ASSIGNED TASKS (FLIGHTS)
# ---------------------------------------------------------

@app.route('/crew/tasks')
def crew_tasks():
    if session.get('role') != 'crew':
        return redirect(url_for('login'))

    username = session.get('username')
    cur = mysql.connection.cursor()

    cur.execute("SELECT id FROM crew WHERE username = %s", [username])
    crew_data = cur.fetchone()

    if not crew_data:
        flash("Crew record not found.", "error")
        return redirect(url_for('home'))

    cur.execute("""
        SELECT f.id, f.flight_date, f.departure_time, f.arrival_time, 
               src.name AS source_airport, dest.name AS dest_airport
        FROM flight f
        JOIN crew_flight cf ON f.id = cf.flight_id
        JOIN airport src ON f.source_id = src.id
        JOIN airport dest ON f.dest_id = dest.id
        WHERE cf.crew_id = %s
        ORDER BY f.flight_date, f.departure_time
    """, [crew_data['id']])
    
    tasks = cur.fetchall()
    cur.close()

    return render_template("crew_tasks.html", tasks=tasks)

# ---------------------------------------------------------
# PASSENGER BOOKS TICKET
# ---------------------------------------------------------
# ---------------------------------------------------------
# PASSENGER BOOKS SPECIFIC SEAT
# ---------------------------------------------------------
@app.route('/book_ticket', methods=['GET', 'POST'])
def book_ticket():
    if session.get('role') != 'user':
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    
    # GET: Show the booking form and available seats
    if request.method == 'GET':
        flight_id = request.args.get('flight_id')
        seats = []
        flight_info = None

        if flight_id:
            # Fetch flight details
            cur.execute("""
                SELECT f.id, src.name as source, dest.name as destination, f.flight_date 
                FROM flight f
                JOIN airport src ON f.source_id = src.id
                JOIN airport dest ON f.dest_id = dest.id
                WHERE f.id = %s
            """, [flight_id])
            flight_info = cur.fetchone()

            # Fetch all available seats for the plane assigned to this flight
            cur.execute("""
                SELECT s.id, s.seat_class 
                FROM seat s
                JOIN flight f ON s.plane_id = f.plane_id
                WHERE f.id = %s AND s.is_available = TRUE
                ORDER BY s.seat_class, s.id
            """, [flight_id])
            seats = cur.fetchall()

        cur.close()
        return render_template("book_ticket.html", seats=seats, flight=flight_info)

    # POST: Process the booking for the specific seat
    if request.method == 'POST':
        flight_id = request.form['flight_id']
        seat_id = request.form['seat_id'] # User picks this now
        username = session.get('username')

        try:
            # 1. Get Passenger ID
            cur.execute("SELECT id FROM passenger WHERE username = %s", [username])
            passenger = cur.fetchone()
            passenger_id = passenger['id']

            # 2. Check if seat is still available (safety check)
            cur.execute("SELECT is_available FROM seat WHERE id = %s", [seat_id])
            seat_check = cur.fetchone()

            if not seat_check or not seat_check['is_available']:
                flash("Sorry, that seat was just taken. Please pick another.", "error")
                return redirect(url_for('book_ticket', flight_id=flight_id))

            # 3. TRANSACTION: Insert Ticket and Mark Seat as Booked
            cur.execute("INSERT INTO ticket (passenger_id, flight_id, seat_id) VALUES (%s, %s, %s)", 
                        (passenger_id, flight_id, seat_id))
            
            cur.execute("UPDATE seat SET is_available = FALSE WHERE id = %s", [seat_id])

            mysql.connection.commit()
            flash(f"Success! Seat #{seat_id} is booked for your journey.", "success")
            return redirect(url_for('add_passenger'))

        except Exception as e:
            mysql.connection.rollback()
            flash("An error occurred during booking.", "error")
            print(f"Error: {e}")
        finally:
            cur.close()

    return redirect(url_for('add_passenger'))

# ---------------------------------------------------------
# ADMIN VIEWS ALL BOOKINGS
# ---------------------------------------------------------
@app.route('/admin/view_bookings')
def admin_view_bookings():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT f.id, src.name AS source, dest.name AS destination, 
               f.flight_date, f.cost, p.model AS plane
        FROM flight f
        JOIN airport src ON f.source_id = src.id
        JOIN airport dest ON f.dest_id = dest.id
        JOIN plane p ON f.plane_id = p.id
        ORDER BY f.flight_date
    """)
    flights = cur.fetchall()
    cur.close()

    return render_template("admin_bookings.html", flights=flights)
# ---------------------------------------------------------
# RUN APP
# ---------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)