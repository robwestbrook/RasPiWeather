##################################################################################
# RasPiWeather.py
##################################################################################
# Python program running on a RaspBerry Pi Model B
# RasPi is functioning as a network hub for various arduino network nodes
# Using an NRF24L01+ radio, the RF24 library, and the RF24Network library
#
# By: Rob Westbrook
##################################################################################

# import all libraries
import time
import csv
from struct import *
from RF24 import *
from RF24Network import *
import time
from datetime import datetime
from time import gmtime, strftime, sleep
import MySQLdb
import httplib, urllib
import socket
import dbConfig as cfg

# global variables used to hold seconds and samples
# Used in calculating amphours and watthours
wattStartSeconds = time.time()
wattElapsedTime = 0
wattSample = 0
wattTotal = 0
wattAverage = 0
wattSeconds = 0
wattHours = 0

ampStartSeconds = time.time()
ampElapsedSeconds = 0
ampSample = 0
ampTotal = 0
ampAverage = 0
ampSeconds = 0
ampHours = 0

# get current day of month for use in watt hour and amp hour new day determination
startDay = strftime("%d")

##################################################################################
# function to calculate simplified dew point using only temperature and humidity
# formula from http://pydoc.net/Python/weather/0.9.1/weather.units.temp/
# requires temperature and humidity
##################################################################################
def calcDewPoint(temp, hum):
 	c = (temp - 32.0) * 0.555556 # convert temp to celcius
	# begin formula
	x = 1 - 0.01 * hum
	dewpoint = (14.55 + 0.114 * c) * x
	dewpoint = dewpoint + ((2.5 + 0.007 * c) * x) ** 3
	dewpoint = dewpoint + (15.9 + 0.117 * c) * x ** 14
	dewpoint = c - dewpoint
	dPoint = (dewpoint * 1.8) + 32 # convert dewpoint to fahrenheit
	print 'Dew Point -> ', ("%.2f" % dPoint),u'\u00b0' # dew point to 2 places and degree symbol
	print"----------------------"
	return dPoint

##################################################################################
# function to check heat index when temperature is under 70 degrees
##################################################################################	
def checkHeatIndex(temp, heatI):
	if temp < 70:
		heatI = temp 
		return heatI
	elif temp >= 70:
		return heatI

##################################################################################
# function to print weather node results to the terminal
##################################################################################
def weatherToTerminal(header, temp, hum, heatI, inHg):
	#print results to terminal
	print"----------------------"
	print 'From Node -> ', oct(header.from_node)       # node data is from
	print 'To Node -> ', header.to_node                # this node
	print 'ID ->', header.id                           # packet ID number
	print 'Header Type ->', header.type                # type of network header
	print 'Temperature -> ', ("%.2f" % temp),u'\u00b0' # temperature to 2 places and degree symbol
	print 'Humidity -> ', ("%.2f" % hum),'%'           # humidity to 2 places and percent symbol
	print 'Heat Index -> ', ("%.2f" % heatI),u'\u00b0' # heat index to 2 places and degree symbol
	print 'Pressure -> ', ("%.2f" % inHg),'inHg'       # pressure to 2 places and inHg symbol

##################################################################################
# function to store weather data to a MySQL database
# MySQL parameters are stored in a config file
##################################################################################
def weatherToSQL(header, temp, hum, dPoint, heatI, inHg):
	# mysql setup
	db = MySQLdb.connect(cfg.mysql['host'], cfg.mysql['user'], cfg.mysql['passwd'], cfg.mysql['db'])
		
	# mysql insertion object
	cur = db.cursor()
		
	# get date and time
	dbDate = time.strftime("%Y-%m-%d")
	dbTime = time.strftime("%H:%M")
		
	# construct sql statement
	sql = ("""INSERT INTO weather (date, time, temperature, humidity, dewpoint, heatindex, pressure, packetid, node) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""", (dbDate, dbTime, dbTemp, dbHum, dbDewPt, dbHeatIndex, dbPress, dbPacket, dbFromNode))
		
	try:
		print "Writing to MySql database..."
		# send to mysql
		cur.execute(*sql)
		# commit to mysql
		db.commit()
		print "Writing to MySql database complete..."
		print"----------------------"
	except:
		#rollback if there is an error
		db.rollback()
		print"Failed to write to MySql database!!!"
		print"----------------------"
		
	# close mysql connection
	cur.close()
	db.close()

##################################################################################
# function to store solar data to a MySQL database
# MySQL parameters are stored in a config file
##################################################################################
def solarToSQL(solarNode, solarPacket, batteryvoltage, panelvoltage, chargecurrent, watts, dbWattHours, dbAmpHours):
	# mysql setup
	db = MySQLdb.connect(cfg.mysql['host'], cfg.mysql['user'], cfg.mysql['passwd'], cfg.mysql['db'])
		
	# mysql insertion object
	cur = db.cursor()
		
	# get date and time
	dbDate = time.strftime("%Y-%m-%d")
	dbTime = time.strftime("%H:%M")
		
	# construct sql statement
	sql = ("""INSERT INTO solar (date, time, batteryvoltage, panelvoltage, chargecurrent, watts, watthours, amphours, packetid, node) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", (dbDate, dbTime, batteryvoltage, panelvoltage, chargecurrent, watts, dbWattHours, dbAmpHours, solarPacket, solarNode))
		
	try:
		print "Writing to MySql database..."
		# send to mysql
		cur.execute(*sql)
		# commit to mysql
		db.commit()
		print "Writing to MySql database complete..."
		print"----------------------"
	except:
		#rollback if there is an error
		db.rollback()
		print"Failed to write to MySql database!!!"
		print"----------------------"
		
	# close mysql connection
	cur.close()
	db.close()
	
##################################################################################
# function to store greenhouse data to a MySQL database
# MySQL parameters are stored in a config file
##################################################################################
def greenhouseToSQL(greenNode, greenPacket, greenTemp, greenHum, greenHI, greenHeatOn):
	# mysql setup
	db = MySQLdb.connect(cfg.mysql['host'], cfg.mysql['user'], cfg.mysql['passwd'], cfg.mysql['db'])
		
	# mysql insertion object
	cur = db.cursor()
		
	# get date and time
	dbDate = time.strftime("%Y-%m-%d")
	dbTime = time.strftime("%H:%M")
		
	# construct sql statement
	sql = ("""INSERT INTO greenhouse (date, time, temperature, humidity, heatindex, heateron, packetid, node) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""", (dbDate, dbTime, greenTemp, greenHum, greenHI, greenHeatOn, greenPacket, greenNode))
		
	try:
		print "Writing to MySql database..."
		# send to mysql
		cur.execute(*sql)
		# commit to mysql
		db.commit()
		print "Writing to MySql database complete..."
		print"----------------------"
	except:
		#rollback if there is an error
		db.rollback()
		print"Failed to write to MySql database!!!"
		print"----------------------"
		
	# close mysql connection
	cur.close()
	db.close()

##################################################################################
# function to write weather data to a SparkFun cloud database
# Sparkfun credentials are stored in a config file
##################################################################################
def weatherToSparkFun(dbTemp, dbHum, dbDewPt, dbHeatIndex, dbPress):
	# array holding my sparkfun data fields
	fields = ['temperature', 'humidity', 'dewpoint', 'heatindex', 'pressure']	
	# prepare data for upload to sparkfun
	# following example found at
	# https://learn.sparkfun.com/tutorials/pushing-data-to-datasparkfuncom/raspberry-pi-python
	uploadData = {}
	uploadData[fields[0]] = dbTemp
	uploadData[fields[1]] = dbHum
	uploadData[fields[2]] = dbDewPt
	uploadData[fields[3]] = dbHeatIndex
	uploadData[fields[4]] = dbPress
	params = urllib.urlencode(uploadData)
		
	# headers for upload to data.sparkfun.com
	headers = {}
	headers['Content-Type'] = 'application/x/www/form-urlencoded'
	headers['Connection'] = 'close'
	headers['Content-Length'] = len(params)
	headers['Phant-Private-Key'] = cfg.upload['privateKey']
		
	try:
		# initiate connection to sparkfun
		socket.setdefaulttimeout(3)						# set timer for connection error
		c = httplib.HTTPConnection(cfg.upload['server'])
		c.timeout = 3									# initialize timeout
		c.request('POST', '/input/' + cfg.upload['publicKey'] + '.txt', params, headers)
		r = c.getresponse()
		print "Upload to data.sparkfun.com succeeded"
		print r.status, r.reason
		print "----------------------"
	except:
		print "Upload to data.sparkfun.com failed"
		print "----------------------"

##################################################################################
# function to write weather data to Weather Underground
# Weather Underground credentials are stored in a config file
##################################################################################
def weatherToWeatherUnderground(dbTemp, dbHum, dbDewPt, dbPress):
	# prepare data for uploading to wunderground
	wuPassword = (cfg.wu['password'])
	wuDate = urllib.quote(str(datetime.utcnow()))
	wuTemp = str(dbTemp)
	wuHum = str(dbHum)
	wuDewPt = str(dbDewPt)
	wuPress = str(dbPress)
	wuPath = cfg.wu['updateURL'] + "?ID=" + cfg.wu['ID']
	wuPath = wuPath + "&PASSWORD=" + wuPassword
	wuPath = wuPath + "&dateutc=" + wuDate
	wuPath = wuPath + "&tempf=" + wuTemp
	wuPath = wuPath + "&humidity=" + wuHum
	wuPath = wuPath + "&dewptf=" + wuDewPt
	wuPath = wuPath + "&baromin=" + wuPress
	wuPath = wuPath + "&softwaretype=RaspberryPi"
	wuPath = wuPath + "&action=updateraw"
			
	try:
		#initiate connection to wunderground.com
		socket.setdefaulttimeout(3)
		w = httplib.HTTPConnection(cfg.wu['server'])
		w.timeout = 3
		w.request('GET', wuPath)
		wr = w.getresponse()
		print "Upload to wunderground.com succeeded"
		print wr.status, wr.reason
		print "----------------------"
	except:
		print "Upload to wunderground.com failed"
		print "----------------------"

##################################################################################
# function to calculate watt hours
##################################################################################
def doWattHours(watts):
	# make these variables global
	global wattStartSeconds
	global wattElapsedSeconds
	global wattSample
	global wattTotal
	global wattAverage
	global wattSeconds
	global wattHours
	global startDay
	#get the hour and minute to calculate if it is a new day
	currentDay = strftime("%d")
	# determine if it is a new day
	# reset all vaiables if it is
	# will not reset start day to current day here!
	# will reset in doAmpHours since that function runs AFTER this one!
	if startDay != currentDay:
		wattStartSeconds = time.time()						# reset start time to now
		wattElapsedSeconds = 0								# reset all variables to 0
		wattSample = 0
		wattTotal = 0
		wattAverage = 0
		wattSeconds = 0
		wattHours = 0
		print 'It is a new day!'
		print 'Resetting all wattHour variables'
		print 'Watt Hours = ', wattHours
		print 'Watt Start Seconds = ', wattStartSeconds
		print"----------------------"
		return wattHours									# return 0 watt hours
	else:
		wattElapsedSeconds = time.time() - wattStartSeconds	# calculate elapsed seconds since start of day
		wattSample = wattSample + 1							# increase sample count by 1
		wattTotal = wattTotal + watts						# add new watts to accumulated watts
		wattAverage = wattTotal/wattSample					# get average by dividing total watts by number of samples
		wattSeconds = wattAverage * wattElapsedSeconds		# calculate watt seconds
		wattHours = wattSeconds/3600						# convert watt seconds to watt hours
		return wattHours									#return watt hours

##################################################################################
# function to calculate amphours
##################################################################################
def doAmpHours(chargeCurrent):
	# make these variables global
	global ampStartSeconds
	global ampElapsedSeconds
	global ampSample
	global ampTotal
	global ampAverage
	global ampSeconds
	global ampHours
	global startDay
	#get the hour and minute to calculate if it is a new day
	currentDay = strftime("%d")
	# determine if it is a new day
	# reset all vaiables if it is
	if startDay != currentDay:
		# reset start day to current day HERE! Not in doWattHours!
		startDay = currentDay
		ampStartSeconds = time.time()						# reset start time to now
		ampElapsedSeconds = 0								# reset all variables to 0
		ampSample = 0
		ampTotal = 0
		ampAverage = 0
		ampSeconds = 0
		ampHours = 0
		print 'It is a new day!'
		print 'Resetting all AmpHour variables'
		print 'Amp Hours = ', ampHours
		print 'Amp Start Seconds = ', ampStartSeconds
		print"----------------------"
		return ampHours										# return 0 amp hours
	else:
		ampElapsedSeconds = time.time() - ampStartSeconds	# calculate elapsed seconds since start of day
		ampSample = ampSample + 1							# increase sample count by 1
		ampTotal = ampTotal + chargeCurrent					# add new amps to accumulated amps
		ampAverage = ampTotal/ampSample						# get average by dividing total amps by number of samples
		ampSeconds = ampAverage * ampElapsedSeconds			# calculate amp seconds
		ampHours = ampSeconds/3600							# convert amp seconds to amp hours
		return ampHours										#return amp hours

##################################################################################
#begin main program
##################################################################################
print "Starting..."					# print to terminal

#setup radio
# CE Pin, CSN Pin, SPI Speed
# Setup for GPIO 22 CE and CE0 CSN for RPi B+ with SPI Speed @ 8Mhz
radio = RF24(22,0)
# setup network
network = RF24Network(radio)

# network address of our node in Octal format (01,021, etc)
this_node = 00

radio.begin()                   # start radio
radio.setDataRate(RF24_250KBPS) # set radio data rate to 250kbps for reliability
radio.printDetails()            # screen dump radio configuration
time.sleep(0.1)                 # slight delay
network.begin(90, this_node)    # our network is on channel 90

#main program loop
while 1:
	try:
		network.update()                                       # must do every loop to check for network traffic
		while network.available():                             # if there's data on the network
			header = RF24NetworkHeader()					   # setup header object to check type of data coming in	
			network.peek(header)                               # peek at header to determine type
			if header.type == 0:								   # this header tells us the data is from the weather node
				header, payload = network.read(16)                 # get network data
				temp, hum, heatI, inHg = unpack('@ffff', payload)  # unpack data into variables
				heatI = checkHeatIndex(temp, heatI)
				weatherToTerminal(header, temp, hum, heatI, inHg)  # print results to terminal
				dPoint = calcDewPoint(temp, hum)                   # get dew point from function
				
				# convert all variables for MySql, SparkFun, and Weather Underground
				# convert FLOATS to 2 decimal places
				dbFromNode = oct(header.from_node)
				dbPacket = header.id
				dbTemp = ("%.2f" % temp)
				dbHum = ("%.2f" % hum)
				dbDewPt = ("%.2f" %dPoint)
				dbHeatIndex = ("%.2f" % heatI)
				dbPress = ("%.2f" % inHg)
		
				weatherToSQL(header, dbTemp, dbHum, dbDewPt, dbHeatIndex, dbPress)
				#weatherToSparkFun(dbTemp, dbHum, dbDewPt, dbHeatIndex, dbPress)
				weatherToWeatherUnderground(dbTemp, dbHum, dbDewPt, dbPress)
		
			elif header.type == 1:
				print"----------------------"
				print 'From Node -> ', oct(header.from_node)       # node data is from
				print 'To Node -> ', header.to_node                # this node
				print 'Header Type -> ', header.type
				print 'Packet ID -> ', header.id
				header, payload = network.read(20)
				batteryVoltage, panelVoltage, chargeCurrent, stateOfCharge, batteryFull, batteryCharging, batteryTemp = unpack('@fffHHHh', payload)
				watts = panelVoltage * chargeCurrent
				dbSolarNode = oct(header.from_node)
				dbSolarPacket = header.id
				dbBattVolt = ("%.2f" % batteryVoltage)
				dbPanelVolt = ("%.2f" % panelVoltage)
				dbChargeCurrent = ("%.2f" % chargeCurrent)
				dbWatts = ("%.2f" % watts)
				dbWattHours = ("%.2f" % doWattHours(watts))
				dbAmpHours = ("%.2f" % doAmpHours(chargeCurrent))
				print 'Battery Voltage -> ', dbBattVolt
				print 'Panel Voltage -> ', dbPanelVolt
				print 'Charge Current -> ', dbChargeCurrent
				print 'Watts -> ', dbWatts
				print 'Watt Hours -> ', dbWattHours
				print 'Amp Hours -> ', dbAmpHours
				print 'State of Charge -> ', stateOfCharge
				print"----------------------"
				solarToSQL(dbSolarNode, dbSolarPacket, dbBattVolt, dbPanelVolt, dbChargeCurrent, dbWatts, dbWattHours, dbAmpHours)
				
				
			elif header.type == 2:
				print"----------------------"
				print 'From Node -> ', oct(header.from_node)       # node data is from
				print 'To Node -> ', header.to_node                # this node
				print 'Header Type -> ', header.type
				print 'Packet ID -> ', header.id
				header, payload = network.read(13)
				greenhouseTemp, greenhouseHum, greenhouseHI, heatOn = unpack('@fff?', payload)
				dbGreenNode = oct(header.from_node)
				dbGreenPacket = header.id
				dbGreenTemp = ("%.2f" % greenhouseTemp)
				dbGreenHum = ("%.2f" % greenhouseHum)
				dbGreenHI = ("%.2f" % greenhouseHI)
				dbGreenHeatOn = heatOn
				print 'Greenhouse Temperature -> ', dbGreenTemp
				print 'Greenhouse Humidity -> ', dbGreenHum
				print 'Greenhouse Heat Index -> ', dbGreenHI
				print 'Heater On/Off -> ', heatOn
				print"----------------------"
				greenhouseToSQL(dbGreenNode, dbGreenPacket, dbGreenTemp, dbGreenHum, dbGreenHI,dbGreenHeatOn)
			
	except:
		print "Error in Network Check"
		print "----------------------"
	
	time.sleep(0.1)  # loop every 100 mS
