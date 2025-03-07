<?php
// Connect to the database
$host = 'localhost';
$username = 'root';  // replace with your database username
$password = '';      // replace with your database password
$dbname = 'flight_booking';

$conn = new mysqli($host, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Default query to fetch all flights
$query = "SELECT * FROM flights";

// If the user selects a departure and destination city, add conditions to the query
if (isset($_GET['departure']) && isset($_GET['destination'])) {
    $departure = $_GET['departure'];
    $destination = $_GET['destination'];

    // Build the query with the filters
    $query = "SELECT * FROM flights WHERE departure_city = '$departure' AND destination_city = '$destination'";
}

// Execute the query
$result = $conn->query($query);

// Check if there are any flights
if ($result->num_rows > 0) {
    // Output the data of each flight
    while($row = $result->fetch_assoc()) {
        echo "<div class='flight'>";
        echo "<h4>" . $row['departure_city'] . " to " . $row['destination_city'] . "</h4>";
        echo "<ul>";
        echo "<li>Flight Number: " . $row['flight_number'] . "</li>";
        echo "<li>Departure Time: " . $row['departure_time'] . "</li>";
        echo "<li>Price: $" . $row['price'] . "</li>";
        echo "</ul>";
        echo "</div>";
    }
} else {
    echo "No flights found.";
}

$conn->close();
?>
