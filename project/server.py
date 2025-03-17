from flask import Flask, request, jsonify, render_template
import pymysql.cursors
import bcrypt  # For password hashing

app = Flask(__name__)

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


def fillFlights():
    try:
        with connection.cursor() as cursor:
            pass
        except Exception as e:
            return {"error":str(e)}



def loginUser(email, password):
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM Customers WHERE Email = %s"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()
            if user and bcrypt.checkpw(password.encode('utf-8'), user['Password'].encode('utf-8')):
                return {"message": "Login successful", "user": user}
            else:
                return {"error": "Invalid email or password"}
    except Exception as e:
        return {"error": str(e)}


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/getFlights', methods=['GET'])
def get_flights():
    return jsonify(fetchFlightsDB())

@app.route('/api/getUsers', methods=['GET'])
def get_users():
    return jsonify(getAllUsers())

@app.route('/api/getBookings', methods=['GET'])
def get_bookings():
    return jsonify(getAllBookings())

@app.route('/api/bookFlight', methods=['POST'])
def book_flight():
    data = request.json
    return jsonify(bookFlight(data.get("flight_id"), data.get("user_id")))

@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.json
    return jsonify(registerUser(data.get("firstName"), data.get("lastName"), data.get("telefon"), data.get("email"), data.get("password")))

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    return jsonify(loginUser(data.get("email"), data.get("password")))

if __name__ == '__main__':
    app.run(host='localhost', port=8020, debug=True)