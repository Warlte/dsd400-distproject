from functools import wraps
from flask import Flask, redirect, request, jsonify, render_template, url_for, session
import pymysql.cursors
import bcrypt  # För password hashing

# pip install flask
# pip install bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key_here' #tänkte byta secret key men orkish inte

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

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        with connection.cursor() as cursor:
            sql = "INSERT INTO Customers (FirstName, LastName, Telephone, Email, Password) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (firstName, lastName, telefon, email, hashed_password))
            connection.commit()
            return {"message": f"User {firstName} registered successfully."}
    except Exception as e:
        return {"error": str(e)}


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login')) 
        return f(*args, **kwargs)
    return decorated_function

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
            SELECT Flights.Flight_ID, Flights.Destination, Flights.Dep_time, Airplanes.Company, Booking.Seat, Booking.Booking_ID, Airport.Airport_name 
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
    
def cancelBooking(bokingID):
    try:
        with connection.cursor() as cursor:

            sql = "SELECT Customer_ID FROM Booking WHERE Booking_ID = %s"
            cursor.execute(sql, (bokingID,))
            booking = cursor.fetchone()
            
            if not booking:
                return {"error": "Booking not found"}, 404
                
            if booking['Customer_ID'] != session['user_id']:
                return {"error": "Not authorized to cancel this booking"}, 403
                

            sql = "DELETE FROM Booking WHERE Booking_ID = %s"
            cursor.execute(sql, (bokingID,))
            connection.commit()
            
            return {"success": True, "message": "Booking cancelled"}
    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.route('/')
def index():
    user_name = None
    booked_flights = None
    if 'user_id' in  session:
        user = doxuser()
        booked_flights = fetch_booked_flights(session['user_id'])
        if user:
            user_name = user['Firstname']
    return render_template('index.html', user_name = user_name, booked_flights = booked_flights)

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/')
def register_page():
    return render_template('register.html')


@app.route('/my-flights')
@login_required
def my_flights():
    user_id = session['user_id']  
    booked_flights = fetch_booked_flights(user_id)  

    if isinstance(booked_flights, dict) and "error" in booked_flights:
        return booked_flights["error"], 500  

    return render_template('my_flights.html', flights=booked_flights)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')


        with connection.cursor() as cursor:
            sql = "SELECT * FROM Customers WHERE Email = %s"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()


        if user:

            stored_password = user['Password'].encode('utf-8') 
            if bcrypt.checkpw(password.encode('utf-8'), stored_password):

                session['user_id'] = user['Customer_ID']
                session['email'] = user['Email']
                print(f"Logged in as {session['user_id']}, with the email {session['email']}")
                return redirect(url_for('index'))  
            else:
                return "Invalid email or password", 401  
        else:
            return "User not found", 404

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        telefon = request.form.get('telefon')
        email = request.form.get('email')
        password = request.form.get('password')

        with connection.cursor() as cursor:
            sql = "SELECT Email FROM Customers WHERE Email = %s"
            cursor.execute(sql, (email,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                return "Email address is already registered", 400

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashed_password_str = hashed_password.decode('utf-8') 

        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO Customers (FirstName, LastName, Telephone, Email, Password) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, (firstName, lastName, telefon, email, hashed_password_str))
                connection.commit()
        except Exception as e:
            return f"Error during registration: {str(e)}", 500

        return redirect(url_for('login')) 

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login')) 

    with connection.cursor() as cursor:
        sql = "SELECT * FROM Customers WHERE Customer_ID = %s"
        cursor.execute(sql, (session['user_id'],))
        user = cursor.fetchone()

    return render_template('dashboard.html', user=user)

@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/bookseats')
@login_required
def show_book_seats():
    flight_id = request.args.get('flight_id')
    seats = request.args.get('seats')
    
    if not flight_id or not seats or not seats.isdigit():
        return "Invalid request", 400
        
    booked_seats = []
    try:
        with connection.cursor() as cursor:
            sql = "SELECT Seat FROM Booking WHERE Flight_ID = %s"
            cursor.execute(sql, (flight_id,))
            results = cursor.fetchall()
            booked_seats = [seat['Seat'] for seat in results] 
    except Exception as e:
        print(f"Error fetching booked seats: {str(e)}")
    
    return render_template('bookSeats.html',
                         seats=int(seats),
                         flight_id=flight_id,
                         booked_seats=booked_seats)

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

@app.route('/api/getUsers', methods=['GET'])
def get_users():
    return jsonify(getAllUsers())

@app.route('/submit-booking', methods=['POST'])
@login_required
def submit_booking():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    selected_seats = request.form.getlist('selected_seats')
    flight_id = request.form.get('flight_id')
    
    print(f"Received booking request - Flight: {flight_id}, Seats: {selected_seats}")  # Debug
    
    if not selected_seats:
        return "No seats selected", 400
        
    try:
        with connection.cursor() as cursor:
            for seat in selected_seats:

                cursor.execute("""
                    SELECT * FROM Booking 
                    WHERE Flight_ID = %s AND Seat = %s
                """, (flight_id, seat))
                if cursor.fetchone():
                    return f"Seat {seat} was just booked by someone else", 400

                cursor.execute("""
                    INSERT INTO Booking (Customer_ID, Flight_ID, Seat)
                    VALUES (%s, %s, %s)
                """, (session['user_id'], flight_id, seat))
            
            connection.commit()
            return redirect(url_for('index', message="Booking successful!"))
            
    except Exception as e:
        print(f"Booking error: {str(e)}") 
        return f"Error creating bookings: {str(e)}", 500
    
@app.route('/api/getBookings', methods=['GET'])
def get_bookings():
    return jsonify(getAllBookings())

@app.route('/api/getFlights', methods=['GET'])
def fetchFlights():
    print("jag tog actually emot medelandet")
    return jsonify(fillFlights())

@app.route('/api/cancelBooking', methods=['POST'])
def cancel_Booking():
    if 'user_id' not in session:
        return jsonify({"error": "how wtf you are not suposed to be able to se this"}), 401
    data = request.json
    booking_id = data.get("booking_id")
    return cancelBooking(booking_id)




if __name__ == '__main__':
    app.run(host='localhost', port=8020, debug=True)