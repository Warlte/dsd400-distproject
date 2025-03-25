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

            var cell6 = row.insertCell(5);
            var button = document.createElement("button");
            button.textContent = "Book Flight";
            button.setAttribute("data-flight-id", myArr[i].Flight_ID);

            button.addEventListener("click", function() {
                var flightId = this.getAttribute("data-flight-id");
                fetchSeatsAndRedirect(flightId); // Call a function to handle booking
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
        if (xhr.readyState === 4 && xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            if (response.seats) {
                // Redirect to the bookseats.html page with the number of seats as a query parameter
                window.location.href = `/bookseats?seats=${response.seats}`;
            } else {
                alert("Failed to fetch seat information: " + response.error);
            }
        } else if (xhr.readyState === 4) {
            alert("Failed to fetch seat information: " + xhr.responseText);
        }
    };
    xhr.send(JSON.stringify({ flight_id: flightId }));
}

// make it so it sends api request to cancel flight

// Add this function to handle cancellation
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
                    // Refresh the page to update the bookings list
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

// Update your event listener setup
function setupCancelButtons() {
    document.querySelectorAll('.cancel-btn').forEach(button => {
        button.addEventListener('click', function() {
            const bookingId = this.getAttribute('data-booking-id');
            cancelBooking(bookingId);
        });
    });
}

// Call this after loading the bookings table
setupCancelButtons();
