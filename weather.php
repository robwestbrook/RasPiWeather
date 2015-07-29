<?php
/* 	weather.php
	PHP backend to read data from MySQL database
	populated by RasPiWeather.py script
*/
?>

<h1>Current Weather at the Westbrook Home</h1>

<?php
static $connection;
// parse config file for mysql credentials
$config = parse_ini_file("config.ini");
$connection = mysqli_connect($config['host'], $config['user'], $config['passwd'], $config['db']);

if(!$connection) {
	die("<h4>Gathering data failed: " . mysqli_connect_error() . "</h4>");
}

echo "<h4>Gathering data...</h4>";

// get last record for current weather
$sqlCurrent = "SELECT * FROM weatherLog ORDER BY id DESC LIMIT 1";


if($current = mysqli_query($connection, $sqlCurrent)) {
	//echo "<h4>Current query successful</h4>";
		while($currentRow = mysqli_fetch_row($current)) {
			//echo "Fetched current row.";
			$currentDate = $currentRow[0];
			$currentTime = $currentRow[1];
			$currentTemp = $currentRow[2];
			$currentHum = $currentRow[3];
			$currentDP = $currentRow[4];
			$currentHI = $currentRow[5];
			$currentPress = $currentRow[6];
			$currentPacket = $currentRow[7];
			$currentNode = $currentRow[8];
			$currentID = $currentRow[9];
			echo "There are " . $currentID . " records in our weather database";
		}
} else {
	//echo "Current Query failed.";
}

// get max temp row - use desc to get maximum temp for date
$sqlTempMax = "SELECT * FROM weatherLog WHERE date = '$currentDate' ORDER BY temperature DESC LIMIT 1";
//echo "<h4>" . $sqlTempMax . "</h4>";

if($result = mysqli_query($connection, $sqlTempMax)) {
	//echo "<h4>Temp max query successful</h4>";
	while($row = mysqli_fetch_row($result)) {
		$maxTempTime = $row[1];
		$maxTemp = $row[2];
	}	
} else {
	//echo "Query failed.";
}

// get min temp row - use asc to get minimum temp for date
$sqlTempMin = "SELECT * FROM weatherLog WHERE date = '$currentDate' ORDER BY temperature ASC LIMIT 1";
//echo "<h4>" . $sqlTempMax . "</h4>";

if($result = mysqli_query($connection, $sqlTempMin)) {
	//echo "<h4>Temp min query successful</h4>";
	while($row = mysqli_fetch_row($result)) {
		$minTempTime = $row[1];
		$minTemp = $row[2];
	}	
} else {
	//echo "Query failed.";
}

// get max heat index row - use desc to get maximum heat index for date
$sqlHIMax = "SELECT * FROM weatherLog WHERE date = '$currentDate' ORDER BY heatindex DESC LIMIT 1";
//echo "<h4>" . $sqlTempMax . "</h4>";

if($result = mysqli_query($connection, $sqlHIMax)) {
	//echo "<h4>Temp min query successful</h4>";
	while($row = mysqli_fetch_row($result)) {
		$maxHITime = $row[1];
		$maxHI = $row[5];
	}	
} else {
	//echo "Query failed.";
}

// close connection
if(mysqli_close($connection)) {
	echo "<h4>Gathering data is complete</h4>";
}
?>

Current Date: <?php echo $currentDate; ?><br />
Current Time: <?php echo $currentTime; ?><br />
Current Temperature: <?php echo $currentTemp; ?><br />
Current Humidity: <?php echo $currentHum; ?><br />
Current Dew Point: <?php echo $currentDP; ?><br />
Current Heat Index: <?php echo $currentHI; ?><br />
Current Pressure: <?php echo $currentPress; ?><br />
Current Packet: <?php echo $currentPacket; ?><br />
Current Node: <?php echo $currentNode; ?><br />
<br />
Max Temperature Today: <?php echo $maxTemp; ?><br />
Max Temperature Today Time: <?php echo $maxTempTime; ?> <br />
<br />
Min Temperature Today: <?php echo $minTemp; ?><br />
Min Temperature Today Time: <?php echo $minTempTime; ?><br />
<br />
Max Heat Index Today: <?php echo $maxHI; ?><br />
Max Heat Index Today Time: <?php echo $maxHITime; ?><br />
