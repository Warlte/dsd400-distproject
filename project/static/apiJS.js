window.onload = requestDB;
function requestDB(){
    httpRequest = new XMLHttpRequest();
    console.log("hello world")

    if (!httpRequest){
        alert('Giving up');
        return false;
    }
    httpRequest.onreadystatechange = asignDB;
    httpRequest.open('GET', '/api/getFlights');
    httpRequest.send();
}

function asignDB(){
     // Check if the request is complete and successful
     if (httpRequest.readyState === 4 && httpRequest.status === 200) {
        var myArr = JSON.parse(httpRequest.responseText);
        console.log("jag började asignDB")
        // Get the table element
        var table = document.getElementById("FlightsTabel");

        // Loop through the JSON array and create rows for each book
        for (var i = 0; i < myArr.length; i++) {
            var row = table.insertRow();  // Insert a new row at the end of the table

            // Create cells in the row and set their content from JSON data
            var cell1 = row.insertCell(0);
            cell1.textContent = myArr[i].Airport_name;

            var cell2 = row.insertCell(1);
            cell2.textContent = myArr[i].Destination;

            var cell3 = row.insertCell(2);
            cell3.textContent = myArr[i].Company;

            var cell4 = row.insertCell(3);
            cell4.textContent = myArr[i].Dep_time;
            
            var cell5 = row.insertCell(4);
            cell5.textContent = myArr[i].Seats
        }
    } else if (httpRequest.readyState === 4) {
        console.error('Request failed');
    }
}