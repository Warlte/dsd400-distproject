import json
import os
from http.server import SimpleHTTPRequestHandler, HTTPServer
import pymysql.cursors
import pprint

connection = pymysql.connect(host='database-2.cx8goywsq9y4.eu-north-1.rds.amazonaws.com',
                             user='admin',
                             password='BananMos12'.encode().decode('latin1'),
                             database='FlygDatabas',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

INTERFACES = 'localhost'
PORT = 8020


def fetchFlightsDB():
    #innit_connection()

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Flights")
        result = cursor.fetchall()
        print(result)
        return result

def getAllUsers():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Customers")
        result = cursor.fetchall()
        print(result)
        print('hej')
        return result


def postToBookDB(name,author,genre):
    try:
        #innit_connection()
        with connection.cursor() as cursor:
            
            sql = "INSERT INTO Bok (Namn, Author, Genre) VALUES (%s, %s, %s)"
            cursor.execute(sql, (name, author, genre))
            cursor.execute("COMMIT;")
            print(f"hello there Book '{name}' by {author} inserted into database.")
    except Exception as e:
        print(f"Error inserting data: {e}")


getAllUsers()


class RequestHandler(SimpleHTTPRequestHandler):
        
    # Override handler for GET requests
    def do_GET(self):
        if self.path.startswith('/api'):
            self.send_response(200)
            self.send_header('Content-type','text/json')
            self.end_headers()
            if self.path.startswith('/api/getFligts'):
                response = fetchFlightsDB()
            elif self.path.startswith('/api/login'):
                response = getAllUsers()
            else:
                response = {'error': 'Not implemented'}
            self.wfile.write(json.dumps(response).encode())
            return
        

        # Call default serving static files if not '/api'
        # from 'html' subdirectory
        
        self.path = 'H:/Python/distsystem/labb4/html' + self.path
        print("Serving file from path:", self.path)
        return super().do_GET()
    
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()
        content_len = int(self.headers['content-length'])
        post_body = self.rfile.read(content_len)
        test_data = json.loads(post_body)
        #print(test_data)

        book_name = test_data.get("name")
        book_author = test_data.get("author")
        book_genre = test_data.get("genre")
        print("postar till db function <<<<<<<<<")
        postToBookDB(book_name,book_author,book_genre)
        response = ""
        self.wfile.write(json.dumps(response).encode())
        return 

try:
    #Create a web server and define the handler to manage the
    #incoming request
    server = HTTPServer((INTERFACES, PORT), RequestHandler)
    print('Starting HTTP server on http://' + INTERFACES + ":" + str(PORT))
    server.serve_forever()
    
except KeyboardInterrupt:
    print('Ctrl-C received, shutting down the web server')
    server.socket.close()



















"""
class RequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Handle API requests (for example, /api/flights)
        if self.path.startswith("/api/flights"):
            self.handle_api_request()
        else:
            # Default behavior: serve static files (HTML, CSS)
            super().do_GET()

    def handle_api_request(self):
        # Extract query parameters for filtering flights
        params = self.get_query_params()
        departure = params.get('departure', 'all')
        destination = params.get('destination', 'all')

        # Simulate some flight data (in practice, this could come from a database)
        flights = [
            {'departure_city': 'New York', 'destination_city': 'London', 'flight_number': 'NY001', 'departure_time': '10:00 AM', 'price': 500},
            {'departure_city': 'New York', 'destination_city': 'London', 'flight_number': 'NY002', 'departure_time': '2:00 PM', 'price': 550},
            {'departure_city': 'New York', 'destination_city': 'Paris', 'flight_number': 'NY010', 'departure_time': '9:00 AM', 'price': 600},
            {'departure_city': 'Los Angeles', 'destination_city': 'Tokyo', 'flight_number': 'LA001', 'departure_time': '8:00 AM', 'price': 700},
            {'departure_city': 'Miami', 'destination_city': 'Sydney', 'flight_number': 'MI001', 'departure_time': '7:00 AM', 'price': 800}
        ]

        # Filter the flight data based on query parameters
        filtered_flights = [
            flight for flight in flights
            if (departure == 'all' or flight['departure_city'] == departure) and
               (destination == 'all' or flight['destination_city'] == destination)
        ]

        # Send JSON response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(filtered_flights).encode('utf-8'))

    def get_query_params(self):
        Extract query parameters from the URL (e.g., ?departure=New%20York&destination=London).
        params = {}
        query_string = self.path.split('?', 1)[-1] if '?' in self.path else ''
        if query_string:
            for param in query_string.split('&'):
                key, value = param.split('=')
                params[key] = value
        return params

# Run the HTTP server on port 8000
def run_server():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))  # Set current directory for static file serving
    httpd = HTTPServer(('localhost', 8000), RequestHandler)
    print("Server running at http://localhost:8000/")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
"""