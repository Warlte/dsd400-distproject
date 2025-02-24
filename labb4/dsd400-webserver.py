#!/usr/bin/env python3
#
# Exempel för DSD400-kursen. Webbserver som tillhandahåller statiska
# filer från "html"-katalogen samt genererad dynamiskt JSON för
# URL:er som börjar på "/api".


from http.server import SimpleHTTPRequestHandler, HTTPServer
import json, random
import pymysql.cursors
import pprint
#pyMCPET
#lurigtpassword
connection = pymysql.connect(host='dsd400.port0.org',
                             user='pyMCPET',
                             password='lurigtpassword'.encode().decode('latin1'),
                             database='MaltePeterGrupp',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)




INTERFACES = '212.25.133.203'
PORT = 8020

# This class will handle any incoming GET requests
# URLs starting with /api/ is catched for REST/JSON calls
# Other URLs are handled by default handler to serve static
# content (directories, files)

def fetchDB():
    #innit_connection()

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Bok")
        result = cursor.fetchall()
        print(result)
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




class RequestHandler(SimpleHTTPRequestHandler):
        
    # Override handler for GET requests
    def do_GET(self):
        if self.path.startswith('/api'):
            self.send_response(200)
            self.send_header('Content-type','text/json')
            self.end_headers()
            if self.path.startswith('/api/slump'):
                # Send the response dict as json message
                response = {'title': 'Min fina rubrik',
                            'text': 'Lite slump: ',
                            'slump': random.randint(0,100)}
            elif self.path.startswith('/api/getbooks'):
                response = fetchDB()
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

