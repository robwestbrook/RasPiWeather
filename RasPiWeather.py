#RasPiWeather.py
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
print "Starting..."					# print to terminal

# array holding my sparkfun data fields
fields = ['temperature', 'humidity', 'dewpoint', 'heatindex', 'pressure']

# function to calculate simplified dew point using only temperature and humidity
# formula from http://pydoc.net/Python/weather/0.9.1/weather.units.temp/
# requires temperature and humidity
def calcDewPoint(temp, hum):
 	c = (temp - 32.0) * 0.555556 # convert temp to celcius
	# begin formula
	x = 1 - 0.01 * hum
	dewpoint = (14.55 + 0.114 * c) * x
	dewpoint = dewpoint + ((2.5 + 0.007 * c) * x) ** 3
	dewpoint = dewpoint + (15.9 + 0.117 * c) * x ** 14
	dewpoint = c - dewpoint
	dPoint = (dewpoint * 1.8) + 32 # convert dewpoint to fahrenheit
	return dPoint

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
	network.update()                                       # must do every loop to check for network traffic
	while network.available():                             # if there's data on the network
		header, payload = network.read(16)                 # get network data
		temp, hum, heatI, inHg = unpack('@ffff', payload)  # unpack data into variables
		#print results to terminal
		print 'From Node -> ', oct(header.from_node)       # node data is from
		print 'To Node -> ', header.to_node                # this node
		print 'ID ->', header.id                           # packet ID number
		print 'Header Type ->', header.type                # type of network header
		print 'Temperature -> ', ("%.2f" % temp),u'\u00b0' # temperature to 2 places and degree symbol
		print 'Humidity -> ', ("%.2f" % hum),'%'           # humidity to 2 places and percent symbol
		print 'Heat Index -> ', ("%.2f" % heatI),u'\u00b0' # heat index to 2 places and degree symbol
		print 'Pressure -> ', ("%.2f" % inHg),'inHg'       # pressure to 2 places and inHg symbol
			
		dPoint = calcDewPoint(temp, hum)                   # get dew point from function
		print 'Dew Point -> ', ("%.2f" %dPoint),u'\u00b0'  # dew point to 2 places and degree symbol
		
		# convert all variables for MySql insertion
		# convert FLOATS to 2 decimal places
		dbFromNode = oct(header.from_node)
		dbPacket = header.id
		dbTemp = ("%.2f" % temp)
		dbHum = ("%.2f" % hum)
		dbDewPt = ("%.2f" %dPoint)
		dbHeatIndex = ("%.2f" % heatI)
		dbPress = ("%.2f" % inHg)
		
		# mysql setup
		db = MySQLdb.connect(cfg.mysql['host'], cfg.mysql['user'], cfg.mysql['passwd'], cfg.mysql['db'])
		
		# mysql insertion object
		cur = db.cursor()
		
		# get date and time
		dbDate = time.strftime("%Y-%m-%d")
		dbTime = time.strftime("%H:%M")
		
		# construct sql statement
		sql = ("""INSERT INTO weatherLog (date, time, temperature, humidity, dewpoint, heatindex, pressure, packetid, node) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""", (dbDate, dbTime, dbTemp, dbHum, dbDewPt, dbHeatIndex, dbPress, dbPacket, dbFromNode))
		
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
		
		# prepare data for upload to sparkfun and weatherunderground
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
			c = httplib.HTTPConnection(cfg.upload['server'])
			c.request('POST', '/input/' + cfg.upload['publicKey'] + '.txt', params, headers)
			r = c.getresponse()
			print "Upload to data.sparkfun.com succeeded"
			print r.status, r.reason
			print "----------------------"
		except:
			print "Upload to data.sparkfun.com failed"
			print "----------------------"
			
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
			w = httplib.HTTPConnection(cfg.wu['server'])
			w.request('GET', wuPath)
			wr = w.getresponse()
			print "Upload to wunderground.com succeeded"
			print wr.status, wr.reason
			print "----------------------"
		except:
			print "Upload to wunderground.com failed"
			print "----------------------"
			
		
	time.sleep(0.1)
