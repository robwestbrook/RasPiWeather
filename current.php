<?php
header('Content-Type: application/json');
static $connection;
// parse config file for mysql credentials
$config = parse_ini_file("config.ini");
$connection = mysqli_connect($config['host'], $config['user'], $config['passwd'], $config['db']);
if(!mysql_errno) {
	die("MySQL connection failed: " . mysqli_connect_error());
}

// get last record for current weather
$sql = "SELECT * FROM weatherLog ORDER BY id DESC LIMIT 1";


if($result = mysqli_query($connection, $sql)) {
	while($row = mysqli_fetch_assoc($result)) {
		$getDate = strtotime($row['date']);
		$formattedDate = date("F j Y", $getDate);
		$getTime = strtotime($row['time']);
		$formattedTime = date("h:i a", $getTime);
		$data[] = array(
		'Date' => $formattedDate,
		'Time' => $formattedTime,
		'Temperature' => $row['temperature'],
		'Humidity' => $row['humidity'],
		'DewPoint' => $row['dewpoint'],
		'HeatIndex' => $row['heatindex'],
		'Pressure' => $row['pressure'],
		'PacketID' => $row['packetid'],
		'Node' => $row['node'],
		'RecordID' => $row['id']);
	}
	$json = json_encode($data);
	echo $json;
} else {
	echo json_encode("ERROR");
}
