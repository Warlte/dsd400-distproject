// Exempel på JSON POST

// Sending and receiving data in JSON format using POST method
//
var xhr = new XMLHttpRequest();
var url = "url";
xhr.open("POST", url, true);
xhr.setRequestHeader("Content-Type", "application/json");
xhr.onreadystatechange = function () {
    if (xhr.readyState === 4 && xhr.status === 200) {
        var json = JSON.parse(xhr.responseText);
        console.log(json.email + ", " + json.password);
    }
};
var data = JSON.stringify({"email": "hey@mail.com", "password": "101010"});
xhr.send(data);


// Motsvarande pythonkod på serversidan:

def do_POST(self):
  content_len = int(self.headers['content-length'])
  post_body = self.rfile.read(content_len)
  test_data = json.loads(post_body)


