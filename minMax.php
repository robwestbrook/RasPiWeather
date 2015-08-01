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

list ($maxTemp, $maxTempTime) = dayMax( $currentDate, 'temperature', 2, $connection);
list ($minTemp, $minTempTime) = dayMin( $currentDate, 'temperature', 2, $connection);

list ($maxHum, $maxHumTime) = dayMax( $currentDate, 'humidity', 3, $connection);
list ($minHum, $minHumTime) = dayMin( $currentDate, 'humidity', 3, $connection);

list ($maxDP, $maxDPTime) = dayMax( $currentDate, 'dewpoint', 4, $connection);
list ($minDP, $minDPTime) = dayMin( $currentDate, 'dewpoint', 4, $connection);

list ($maxHI, $maxHITime) = dayMax( $currentDate, 'heatindex', 5, $connection);
list ($minHI, $minHITime) = dayMin( $currentDate, 'heatindex', 5, $connection);

list ($maxPress, $maxPressTime) = dayMax( $currentDate, 'pressure', 6, $connection);
list ($minPress, $minPressTime) = dayMin( $currentDate, 'pressure', 6, $connection);

list($monthMaxTempDate, $monthMaxTempTime, $monthMaxTemp) = monthMax('temperature', 2, $connection);
list($monthMinTempDate, $monthMinTempTime, $monthMinTemp) = monthMin('temperature', 2, $connection);

list($monthMaxHumDate, $monthMaxHumTime, $monthMaxHum) = monthMax('humidity', 3, $connection);
list($monthMinHumDate, $monthMinHumTime, $monthMinHum) = monthMin('humidity', 3, $connection);

list($monthMaxDPDate, $monthMaxDPTime, $monthMaxDP) = monthMax('dewpoint', 4, $connection);
list($monthMinDPDate, $monthMinDPTime, $monthMinDP) = monthMin('dewpoint', 4, $connection);

list($monthMaxHIDate, $monthMaxHITime, $monthMaxHI) = monthMax('heatindex', 5, $connection);
list($monthMinHIDate, $monthMinHITime, $monthMinHI) = monthMin('heatindex', 5, $connection);

list($monthMaxPressDate, $monthMaxPressTime, $monthMaxPress) = monthMax('pressure', 6, $connection);
list($monthMinPressDate, $monthMinPressTime, $monthMinPress) = monthMin('pressure', 6, $connection);

list($yearMaxTempDate, $yearMaxTempTime, $yearMaxTemp) = yearMax('temperature', 2, $connection);
list($yearMinTempDate, $yearMinTempTime, $yearMinTemp) = yearMin('temperature', 2, $connection);

list($yearMaxHumDate, $yearMaxHumTime, $yearMaxHum) = yearMax('humidity', 3, $connection);
list($yearMinHumDate, $yearMinHumTime, $yearMinHum) = yearMin('humidity', 3, $connection);

list($yearMaxDPDate, $yearMaxDPTime, $yearMaxDP) = yearMax('dewpoint', 4, $connection);
list($yearMinDPDate, $yearMinDPTime, $yearMinDP) = yearMin('dewpoint', 4, $connection);

list($yearMaxHIDate, $yearMaxHITime, $yearMaxHI) = yearMax('heatindex', 5, $connection);
list($yearMinHIDate, $yearMinHITime, $yearMinHI) = yearMin('heatindex', 5, $connection);

list($yearMaxPressDate, $yearMaxPressTime, $yearMaxPress) = yearMax('pressure', 6, $connection);
list($yearMinPressDate, $yearMinPressTime, $yearMinPress) = yearMin('pressure', 6, $connection);

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
	'minPressTime' => $minPressTime,
	'monthMaxTempDate' => $monthMaxTempDate,
	'monthMaxTempTime' => $monthMaxTempTime,
	'monthMaxTemp' => $monthMaxTemp,
	'monthMinTempDate' => $monthMinTempDate,
	'monthMinTempTime' => $monthMinTempTime,
	'monthMinTemp' => $monthMinTemp,
	'monthMaxHumDate' => $monthMaxHumDate,
	'monthMaxHumTime' => $monthMaxHumTime,
	'monthMaxHum' => $monthMaxHum,
	'monthMinHumDate' => $monthMinHumDate,
	'monthMinHumTime' => $monthMinHumTime,
	'monthMinHum' => $monthMinHum,
	'monthMaxDPDate' => $monthMaxDPDate,
	'monthMaxDPTime' => $monthMaxDPTime,
	'monthMaxDP' => $monthMaxDP,
	'monthMinDPDate' => $monthMinDPDate,
	'monthMinDPTime' => $monthMinDPTime,
	'monthMinDP' => $monthMinDP,
	'monthMaxHIDate' => $monthMaxHIDate,
	'monthMaxHITime' => $monthMaxHITime,
	'monthMaxHI' => $monthMaxHI,
	'monthMinHIDate' => $monthMinHIDate,
	'monthMinHITime' => $monthMinHITime,
	'monthMinHI' => $monthMinHI,
	'monthMaxPressDate' => $monthMaxPressDate,
	'monthMaxPressTime' => $monthMaxPressTime,
	'monthMaxPress' => $monthMaxPress,
	'monthMinPressDate' => $monthMinPressDate,
	'monthMinPressTime' => $monthMinPressTime,
	'monthMinPress' => $monthMinPress,
	'yearMaxTempDate' => $yearMaxTempDate,
	'yearMaxTempTime' => $yearMaxTempTime,
	'yearMaxTemp' => $yearMaxTemp,
	'yearMinTempDate' => $yearMinTempDate,
	'yearMinTempTime' => $yearMinTempTime,
	'yearMinTemp' => $yearMinTemp,
	'yearMaxHumDate' => $yearMaxHumDate,
	'yearMaxHumTime' => $yearMaxHumTime,
	'yearMaxHum' => $yearMaxHum,
	'yearMinHumDate' => $yearMinHumDate,
	'yearMinHumTime' => $yearMinHumTime,
	'yearMinHum' => $yearMinHum,
	'yearMaxDPDate' => $yearMaxDPDate,
	'yearMaxDPTime' => $yearMaxDPTime,
	'yearMaxDP' => $yearMaxDP,
	'yearMinDPDate' => $yearMinDPDate,
	'yearMinDPTime' => $yearMinDPTime,
	'yearMinDP' => $yearMinDP,
	'yearMaxHIDate' => $yearMaxHIDate,
	'yearMaxHITime' => $yearMaxHITime,
	'yearMaxHI' => $yearMaxHI,
	'yearMinHIDate' => $yearMinHIDate,
	'yearMinHITime' => $yearMinHITime,
	'yearMinHI' => $yearMinHI,
	'yearMaxPressDate' => $yearMaxPressDate,
	'yearMaxPressTime' => $yearMaxPressTime,
	'yearMaxPress' => $yearMaxPress,
	'yearMinPressDate' => $yearMinPressDate,
	'yearMinPressTime' => $yearMinPressTime,
	'yearMinPress' => $yearMinPress);

$json = json_encode($data);
echo $json;

function dayMax( $currentDate, $param, $rowPosition, $connection) {
	$sql = "SELECT * FROM weatherLog WHERE date = '$currentDate' ORDER BY $param DESC LIMIT 1";
	if($result = mysqli_query($connection, $sql)) {
		while($row = mysqli_fetch_row($result)) {
			$getTime = strtotime($row[1]);
			$formattedTime = date("h:i a", $getTime);
			$maxTime = $formattedTime;
			$max = $row[$rowPosition];
			return array ($max, $maxTime);
		}	
	} else {
		echo "Query failed.";
	}
}

function dayMin( $currentDate, $param, $rowPosition, $connection) {
	$sql = "SELECT * FROM weatherLog WHERE date = '$currentDate' ORDER BY $param ASC LIMIT 1";
	if($result = mysqli_query($connection, $sql)) {
		while($row = mysqli_fetch_row($result)) {
			$getTime = strtotime($row[1]);
			$formattedTime = date("h:i a", $getTime);
			$minTime = $formattedTime;
			$min = $row[$rowPosition];
			return array ($min, $minTime);
		}	
	} else {
		echo "Query failed.";
	}
}

function monthMax( $param, $rowPosition, $connection) {
	$sql = "SELECT * FROM weatherLog WHERE YEAR(date) = YEAR(now()) AND MONTH(date) = MONTH(now()) ORDER BY $param DESC LIMIT 1";

	if($result = mysqli_query($connection, $sql)) {
		while($row = mysqli_fetch_row($result)) {
			$getDate = strtotime($row[0]);
			$maxDate = date("F j Y", $getDate);
			$getTime = strtotime($row[1]);
			$maxTime = date("h:i a", $getTime);
			$max = $row[$rowPosition];
			return array ($maxDate, $maxTime, $max);
		}	
	} else {
		echo "Query failed.";
	}
}

function monthMin( $param, $rowPosition, $connection) {
	$sql = "SELECT * FROM weatherLog WHERE YEAR(date) = YEAR(now()) AND MONTH(date) = MONTH(now()) ORDER BY $param ASC LIMIT 1";

	if($result = mysqli_query($connection, $sql)) {
		while($row = mysqli_fetch_row($result)) {
			$getDate = strtotime($row[0]);
			$minDate = date("F j Y", $getDate);
			$getTime = strtotime($row[1]);
			$minTime = date("h:i a", $getTime);
			$min = $row[$rowPosition];
			return array ($minDate, $minTime, $min);
		}	
	} else {
		echo "Query failed.";
	}
}

function yearMax( $param, $rowPosition, $connection) {
	$sql = "SELECT * FROM weatherLog WHERE YEAR(date) = YEAR(now()) ORDER BY $param DESC LIMIT 1";

	if($result = mysqli_query($connection, $sql)) {
		while($row = mysqli_fetch_row($result)) {
			$getDate = strtotime($row[0]);
			$maxDate = date("F j Y", $getDate);
			$getTime = strtotime($row[1]);
			$maxTime = date("h:i a", $getTime);
			$max = $row[$rowPosition];
			return array ($maxDate, $maxTime, $max);
		}	
	} else {
		echo "Query failed.";
	}
}

function yearMin( $param, $rowPosition, $connection) {
	$sql = "SELECT * FROM weatherLog WHERE YEAR(date) = YEAR(now()) ORDER BY $param ASC LIMIT 1";

	if($result = mysqli_query($connection, $sql)) {
		while($row = mysqli_fetch_row($result)) {
			$getDate = strtotime($row[0]);
			$minDate = date("F j Y", $getDate);
			$getTime = strtotime($row[1]);
			$minTime = date("h:i a", $getTime);
			$min = $row[$rowPosition];
			return array ($minDate, $minTime, $min);
		}	
	} else {
		echo "Query failed.";
	}
}
?>
