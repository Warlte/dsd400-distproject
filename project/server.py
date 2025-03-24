from functools import wraps
from flask import Flask, redirect, request, jsonify, render_template, url_for, session
import pymysql.cursors
import bcrypt  # For password hashing

# pip install flask
# pip install bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure secret key

connection = pymysql.connect(
    host='database-2.cx8goywsq9y4.eu-north-1.rds.amazonaws.com',
    user='admin',
    password='BananMos12'.encode().decode('latin1'),
    database='FlygDatabas',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

def fetchFlightsDB():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Flights")
        return cursor.fetchall()

def getAllUsers():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Customers")
        return cursor.fetchall()

def getAllBookings():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Booking")
        return cursor.fetchall()

def doxuser():
    with connection.cursor() as cursor:
        sql = "SELECT Firstname FROM Customers WHERE Customer_ID = %s"
        cursor.execute(sql, (session['user_id'],))
        user = cursor.fetchone()
        return user


def postToBookDB(name, author, genre):
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO Bok (Namn, Author, Genre) VALUES (%s, %s, %s)"
            cursor.execute(sql, (name, author, genre))
            connection.commit()
            return {"message": f"Book '{name}' by {author} inserted successfully."}
    except Exception as e:
        return {"error": str(e)}

def registerUser(firstName, lastName, telefon, email, password):
    try:
        # Hash the password before storing it
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        with connection.cursor() as cursor:
            sql = "INSERT INTO Customers (FirstName, LastName, Telephone, Email, Password) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (firstName, lastName, telefon, email, hashed_password))
            connection.commit()
            return {"message": f"User {firstName} registered successfully."}
    except Exception as e:
        return {"error": str(e)}

def bookFlight(flight_id, user_id):
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO Booking (Customer_ID, Flight_ID) VALUES (%s, %s)"
            cursor.execute(sql, (user_id, flight_id))
            connection.commit()
            return {"message": f"User {user_id} booked flight {flight_id} successfully."}
    except Exception as e:
        return {"error": str(e)}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))  # Redirect to login page if not logged in
        return f(*args, **kwargs)
    return decorated_function
'''
def fillFlights():
    try:
        with connection.cursor() as cursor:
            #sql kod kommer att göra mig galen
            sql = "SELECT Flights.Destination, Flights.Dep_time, Airplanes.Company, Airplanes.Seats, Airport.Airport_name FROM ((Flights INNER JOIN Airport ON Flights.Plane_ID = Airplane.Plane_ID) INNER JOIN Airport ON Fligts.Start_ID = Airport.Airport_ID)"
            hej = cursor.execute(sql)
            print(hej)
            print("du borde ha fått en json")
            return hej
    except Exception as e:
        return {"error":str(e)}
'''
def fillFlights():
    try:
        with connection.cursor() as cursor:
            sql = """
            SELECT Flights.Destination, Flights.Dep_time, Flights.Flight_ID, Airplanes.Company, Airplanes.Seats, Airport.Airport_name 
            FROM Flights 
            INNER JOIN Airplanes ON Flights.Plane_ID = Airplanes.Plane_ID 
            INNER JOIN Airport ON Flights.Start_ID = Airport.Airport_ID
            """
            cursor.execute(sql)
            flights = cursor.fetchall()
            print(flights)
            return flights
    except Exception as e:
        return {"error": str(e)}

def fetch_booked_flights(user_id):
    try:
        with connection.cursor() as cursor:
            sql = """
            SELECT Flights.Flight_ID, Flights.Destination, Flights.Dep_time, Airplanes.Company, Airplanes.Seats, Airport.Airport_name 
            FROM Booking 
            INNER JOIN Flights ON Booking.Flight_ID = Flights.Flight_ID 
            INNER JOIN Airplanes ON Flights.Plane_ID = Airplanes.Plane_ID 
            INNER JOIN Airport ON Flights.Start_ID = Airport.Airport_ID 
            WHERE Booking.Customer_ID = %s
            """
            cursor.execute(sql, (user_id,))
            booked_flights = cursor.fetchall()
            return booked_flights
    except Exception as e:
        return {"error": str(e)}





@app.route('/')
def index():
    user_name = None
    if 'user_id' in  session:
        user = doxuser()
        if user:
            user_name = user['Firstname']
    return render_template('index.html', user_name = user_name)

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/')
def register_page():
    return render_template('register.html')


@app.route('/my-flights')
@login_required
def my_flights():
    user_id = session['user_id']  # Get the logged-in user's ID from the session
    booked_flights = fetch_booked_flights(user_id)  # Fetch booked flights for the user

    if isinstance(booked_flights, dict) and "error" in booked_flights:
        return booked_flights["error"], 500  # Return error if something went wrong

    return render_template('my_flights.html', flights=booked_flights)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Fetch user from the database
        with connection.cursor() as cursor:
            sql = "SELECT * FROM Customers WHERE Email = %s"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()

        # Validate user and password
        if user:
            # Ensure the stored password is in bytes
            stored_password = user['Password'].encode('utf-8')  # Encode to bytes
            if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                # Store user ID in the session
                session['user_id'] = user['Customer_ID']
                session['email'] = user['Email']
                print(f"Logged in as {session['user_id']}, with the email {session['email']}")
                return redirect(url_for('index'))  # Redirect to a dashboard or home page
            else:
                return "Invalid email or password", 401  # Return an error message
        else:
            return "User not found", 404

    # Render the login page for GET requests
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        telefon = request.form.get('telefon')
        email = request.form.get('email')
        password = request.form.get('password')

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashed_password_str = hashed_password.decode('utf-8')  # Convert to string for storage

        # Insert user into the database
        with connection.cursor() as cursor:
            sql = "INSERT INTO Customers (FirstName, LastName, Telephone, Email, Password) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (firstName, lastName, telefon, email, hashed_password_str))
            connection.commit()

        return redirect(url_for('login'))  # Redirect to login after registration

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    # Check if the user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not authenticated

    # Fetch user details from the database
    with connection.cursor() as cursor:
        sql = "SELECT * FROM Customers WHERE Customer_ID = %s"
        cursor.execute(sql, (session['user_id'],))
        user = cursor.fetchone()

    return render_template('dashboard.html', user=user)

@app.route('/logout')
@login_required
def logout():
    # Clear the session
    session.pop('user_id', None)
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/bookseats')
def book_seats():
    seats = request.args.get("seats")
    if seats is not None and seats.isdigit():  # Check if seats is a valid number
        seats = int(seats)  # Convert to integer
    else:
        return "Invalid number of seats", 400  # Return an error if seats is not a valid number
    return render_template('bookSeats.html', seats=seats)

@app.route('/api/getSeats', methods=['POST'])
def get_seats():
    data = request.json
    flight_id = data.get("flight_id")
    try:
        with connection.cursor() as cursor:
            sql = "SELECT Airplanes.Seats FROM Flights INNER JOIN Airplanes ON %s = Airplanes.Plane_ID"
            cursor.execute(sql, (flight_id,))
            result = cursor.fetchone()
            if result:
                return jsonify({"seats": result["Seats"]})
            else:
                return jsonify({"error": "Flight not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

'''

@app.route('/api/getFlights', methods=['GET'])
def get_flights():
    return jsonify(fetchFlightsDB())

@app.route('/api/getSeats', methods=['POST'])
def getflights():
    data = request.json
    return jsonify(get_seats(data.get("flight_id")))
'''

@app.route('/api/getUsers', methods=['GET'])
def get_users():
    return jsonify(getAllUsers())

@app.route('/submit-booking', methods=['POST'])
def submit_booking():
    selected_seats = request.form.getlist('selected_seats')  # Get all selected seats
    print(f"Selected seats: {selected_seats}")  # Debugging: Print selected seats
    # Add your logic here to save the selected seats to the database
    return redirect('index.html')  # Redirect to the homepage or a confirmation page

@app.route('/api/getBookings', methods=['GET'])
def get_bookings():
    return jsonify(getAllBookings())

@app.route('/api/getFlights', methods=['GET'])
def fetchFlights():
    print("jag tog actually emot medelandet")
    return jsonify(fillFlights())

@app.route('/api/bookFlight', methods=['POST'])
def book_flight():
    data = request.json
    return jsonify(bookFlight(data.get("flight_id"), data.get("user_id")))


if __name__ == '__main__':
    app.run(host='localhost', port=8020, debug=True)