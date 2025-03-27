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

     if (httpRequest.readyState === 4 && httpRequest.status === 200) {
        var myArr = JSON.parse(httpRequest.responseText);
        console.log("jag började asignDB")

        var table = document.getElementById("FlightsTabel");

        for (var i = 0; i < myArr.length; i++) {
            var row = table.insertRow();  


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

            var cell6 = row.insertCell(5);
            var button = document.createElement("button");
            button.textContent = "Book Flight";
            button.setAttribute("data-flight-id", myArr[i].Flight_ID);

            button.addEventListener("click", function() {
                var flightId = this.getAttribute("data-flight-id");
                fetchSeatsAndRedirect(flightId); 
            });
            cell6.appendChild(button);
        }
    } else if (httpRequest.readyState === 4) {
        console.error('Request failed');
    }

    
}

function fetchSeatsAndRedirect(flightId) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/api/getSeats", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                try {
                    var response = JSON.parse(xhr.responseText);
                    if (response.seats) {
                        window.location.href = `/bookseats?seats=${response.seats}&flight_id=${flightId}`;
                    } else {
                        alert("Failed to fetch seat information: " + (response.error || "Unknown error"));
                    }
                } catch (e) {
                    console.error("Error parsing response:", e);
                    alert("Failed to process server response");
                }
            } else {
                try {
                    var errorResponse = JSON.parse(xhr.responseText);
                    alert("Error: " + (errorResponse.error || "Server returned status " + xhr.status));
                } catch (e) {
                    alert("Failed to fetch seat information. Please try again.");
                }
            }
        }
    };
    
    xhr.onerror = function() {
        alert("Network error occurred. Please check your connection.");
    };
    
    xhr.send(JSON.stringify({ flight_id: flightId }));
}


function cancelBooking(bookingId) {
    if (!confirm("Are you sure you want to cancel this booking?")) {
        return;
    }

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/api/cancelBooking", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                if (response.success) {
                    alert("Booking cancelled successfully!");
                    window.location.reload();
                } else {
                    alert("Failed to cancel booking: " + (response.error || "Unknown error"));
                }
            } else {
                try {
                    var errorResponse = JSON.parse(xhr.responseText);
                    alert("Failed to cancel booking: " + (errorResponse.error || "Server error"));
                } catch (e) {
                    alert("Failed to cancel booking: Server error");
                }
            }
        }
    };
    
    xhr.send(JSON.stringify({ booking_id: bookingId }));
}

function setupCancelButtons() {
    document.querySelectorAll('.cancel-btn').forEach(button => {
        button.addEventListener('click', function() {
            const bookingId = this.getAttribute('data-booking-id');
            cancelBooking(bookingId);
        });
    });
}


setupCancelButtons();
