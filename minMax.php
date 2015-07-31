<?php
header('Content-Type: application/json');
static $connection;

$config = parse_ini_file("config.ini");
$connection = mysqli_connect($config['host'], $config['user'], $config['passwd'], $config['db']);
if(!mysql_errno) {
	die("MySQL connection failed: " . mysqli_connect_error());
}

// get last record for current date
$sqlCurrent = "SELECT date FROM weatherLog ORDER BY id DESC LIMIT 1";
if($current = mysqli_query($connection, $sqlCurrent)) {
		while($currentRow = mysqli_fetch_row($current)) {
			$currentDate = $currentRow[0];
		}
} else {
	echo "Current Query failed.";
}

// get max temp row - use desc to get maximum temp for date
$sqlTempMax = "SELECT * FROM weatherLog WHERE date = '$currentDate' ORDER BY temperature DESC LIMIT 1";
//echo "<h4>" . $sqlTempMax . "</h4>";

if($result = mysqli_query($connection, $sqlTempMax)) {
	//echo "<h4>Temp max query successful</h4>";
	while($row = mysqli_fetch_row($result)) {
		$getTime = strtotime($row[1]);
		$formattedTime = date("h:i a", $getTime);
		$maxTempTime = $formattedTime;
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
		$getTime = strtotime($row[1]);
		$formattedTime = date("h:i a", $getTime);
		$minTempTime = $formattedTime;
		$minTemp = $row[2];
	}	
} else {
	//echo "Query failed.";
}

// get max hum row - use desc to get maximum temp for date
$sqlHumMax = "SELECT * FROM weatherLog WHERE date = '$currentDate' ORDER BY humidity DESC LIMIT 1";

if($result = mysqli_query($connection, $sqlHumMax)) {
	while($row = mysqli_fetch_row($result)) {
		$getTime = strtotime($row[1]);
		$formattedTime = date("h:i a", $getTime);
		$maxHumTime = $formattedTime;
		$maxHum = $row[3];
	}	
} else {
	//echo "Query failed.";
}

// get min hum row - use asc to get minimum temp for date
$sqlHumMin = "SELECT * FROM weatherLog WHERE date = '$currentDate' ORDER BY humidity ASC LIMIT 1";


if($result = mysqli_query($connection, $sqlHumMin)) {
	//echo "<h4>Temp min query successful</h4>";
	while($row = mysqli_fetch_row($result)) {
		$getTime = strtotime($row[1]);
		$formattedTime = date("h:i a", $getTime);
		$minHumTime = $formattedTime;
		$minHum = $row[3];
	}	
} else {
	//echo "Query failed.";
}

// get max dp row - use desc to get maximum temp for date
$sqlDPMax = "SELECT * FROM weatherLog WHERE date = '$currentDate' ORDER BY dewpoint DESC LIMIT 1";

if($result = mysqli_query($connection, $sqlDPMax)) {
	while($row = mysqli_fetch_row($result)) {
		$getTime = strtotime($row[1]);
		$formattedTime = date("h:i a", $getTime);
		$maxDPTime = $formattedTime;
		$maxDP = $row[4];
	}	
} else {
	//echo "Query failed.";
}

// get min dp row - use asc to get minimum temp for date
$sqlDPMin = "SELECT * FROM weatherLog WHERE date = '$currentDate' ORDER BY dewpoint ASC LIMIT 1";


if($result = mysqli_query($connection, $sqlDPMin)) {
	//echo "<h4>Temp min query successful</h4>";
	while($row = mysqli_fetch_row($result)) {
		$getTime = strtotime($row[1]);
		$formattedTime = date("h:i a", $getTime);
		$minDPTime = $formattedTime;
		$minDP = $row[4];
	}	
} else {
	//echo "Query failed.";
}

// get max dp row - use desc to get maximum temp for date
$sqlHIMax = "SELECT * FROM weatherLog WHERE date = '$currentDate' ORDER BY heatindex DESC LIMIT 1";

if($result = mysqli_query($connection, $sqlHIMax)) {
	while($row = mysqli_fetch_row($result)) {
		$getTime = strtotime($row[1]);
		$formattedTime = date("h:i a", $getTime);
		$maxHITime = $formattedTime;
		$maxHI = $row[5];
	}	
} else {
	//echo "Query failed.";
}

// get min heatI row - use asc to get minimum temp for date
$sqlHIMin = "SELECT * FROM weatherLog WHERE date = '$currentDate' ORDER BY heatindex ASC LIMIT 1";


if($result = mysqli_query($connection, $sqlHIMin)) {
	//echo "<h4>Temp min query successful</h4>";
	while($row = mysqli_fetch_row($result)) {
		$getTime = strtotime($row[1]);
		$formattedTime = date("h:i a", $getTime);
		$minHITime = $formattedTime;
		$minHI = $row[5];
	}	
} else {
	//echo "Query failed.";
}

// get max dp row - use desc to get maximum temp for date
$sqlPressMax = "SELECT * FROM weatherLog WHERE date = '$currentDate' ORDER BY pressure DESC LIMIT 1";

if($result = mysqli_query($connection, $sqlPressMax)) {
	while($row = mysqli_fetch_row($result)) {
		$getTime = strtotime($row[1]);
		$formattedTime = date("h:i a", $getTime);
		$maxPressTime = $formattedTime;
		$maxPress = $row[6];
	}	
} else {
	//echo "Query failed.";
}

// get min heatI row - use asc to get minimum temp for date
$sqlPressMin = "SELECT * FROM weatherLog WHERE date = '$currentDate' ORDER BY pressure ASC LIMIT 1";


if($result = mysqli_query($connection, $sqlPressMin)) {
	//echo "<h4>Temp min query successful</h4>";
	while($row = mysqli_fetch_row($result)) {
		$getTime = strtotime($row[1]);
		$formattedTime = date("h:i a", $getTime);
		$minPressTime = $formattedTime;
		$minPress = $row[6];
	}	
} else {
	//echo "Query failed.";
}

$data[] = array(
	'maxTemp' => $maxTemp,
	'maxTempTime' => $maxTempTime,
	'minTemp' => $minTemp,
	'minTempTime' => $minTempTime,
	'maxHum' => $maxHum,
	'maxHumTime' => $maxHumTime,
	'minHum' => $minHum,
	'minHumTime' => $minHumTime,
	'maxDP' => $maxDP,
	'maxDPTime' => $maxDPTime,
	'minDP' => $minDP,
	'minDPTime' => $minDPTime,
	'maxHI' => $maxHI,
	'maxHITime' => $maxHITime,
	'minHI' => $minHI,
	'minHITime' => $minHITime,
	'maxPress' => $maxPress,
	'maxPressTime' => $maxPressTime,
	'minPress' => $minPress,
	'minPressTime' => $minPressTime);

$json = json_encode($data);
echo $json;
?>
