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
import dbConfig as cfg
print "Starting..."
# setup for using NRF24L01+ radio
# CE Pin, CSN Pin, SPI Speed
# Setup for GPIO 22 CE and CE0 CSN for RPi B+ with SPI Speed @ 8Mhz
#radio = RF24(RPI_BPLUS_GPIO_J8_22, RPI_BPLUS_GPIO_J8_24, BCM2835_SPI_SPEED_8MHZ)
radio = RF24(22,0)
network = RF24Network(radio)

# Address of our node in Octal format (01,021, etc)
this_node = 00

radio.begin()
radio.setDataRate(RF24_250KBPS)
radio.printDetails()
time.sleep(0.1)
network.begin(90, this_node)    # channel 90
while 1:
	network.update() # must do every loop to check for network traffic
	while network.available():
		header, payload = network.read(16)
		temp, hum, heatI, inHg = unpack('@ffff', payload)
		print 'From Node -> ', oct(header.from_node)
		print 'To Node -> ', header.to_node
		print 'ID ->', header.id
		print 'Header Type ->', header.type
		print 'Temperature -> ', ("%.2f" % temp),u'\u00b0'
		print 'Humidity -> ', ("%.2f" % hum),'%'
		print 'Heat Index -> ', ("%.2f" % heatI),u'\u00b0'
		print 'Pressure -> ', ("%.2f" % inHg),'inHg'
		
		
		# convert temp to celcius
		c = (temp - 32.0) * 0.555556
		# formula for simplified dew point using just temp and hum
		# formula from http://pydoc.net/Python/weather/0.9.1/weather.units.temp/
		x = 1 - 0.01 * hum
		dewpoint = (14.55 + 0.114 * c) * x
		dewpoint = dewpoint + ((2.5 + 0.007 * c) * x) ** 3
		dewpoint = dewpoint + (15.9 + 0.117 * c) * x ** 14
		dewpoint = c - dewpoint
		# convert dewpoint to fahrenheit
		dPoint = (dewpoint * 1.8) + 32
		print 'Dew Point -> ', ("%.2f" %dPoint),u'\u00b0'
		print '-----------------------'
		
		# mysql setup
		db = MySQLdb.connect(cfg.mysql['host'], cfg.mysql['user'], cfg.mysql['passwd'], cfg.mysql['db'])
		cur = db.cursor()
		datetimeWrite = (time.strftime("%Y-%m-%d ") + time.strftime("%H:%M:%S"))
		sql = ("""INSERT INTO weatherLog (datetime, temperature, humidity, dewpoint, heatindex, pressure) VALUES (%s,%s,%s,%s,%s,%s)""", (datetimeWrite, temp, hum, dPoint, heatI, inHg))
		try:
			print "Writing to MySql database..."
			cur.execute(*sql)
			db.commit()
			print "Writing to MySql database complete..."
			print"----------------------"
		except:
			#rollback if error
			db.rollback()
			print"Failed to write to MySql database!!!"
			print"----------------------"
		cur.close()
		db.close()
	
