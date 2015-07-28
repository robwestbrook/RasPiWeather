# RasPiWeather.py
# write results every minute to a csv file
import time
import csv
from struct import *
from RF24 import *
from RF24Network import *
import time
from datetime import datetime
from time import gmtime, strftime, sleep
from Tkinter import *
import MySQLdb
import dbConfig as cfg

print cfg.mysql['host']

# CE Pin, CSN Pin, SPI Speed
# Setup for GPIO 22 CE and CE0 CSN for RPi B+ with SPI Speed @ 8Mhz
#radio = RF24(RPI_BPLUS_GPIO_J8_22, RPI_BPLUS_GPIO_J8_24, BCM2835_SPI_SPEED_8MHZ)
radio = RF24(22,0)
network = RF24Network(radio)

# Address of our node in Octal format (01,021, etc)
this_node = 00

#main Tkinter application class
class Application(Frame):
	
	def update(self):
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
			print 'From Node -> ', oct(header.from_node)
			print '-----------------------'
		
			format = "%a, %b %d, %Y - %I:%M %p"
			d = datetime.today()
			s = d.strftime(format)
			
			#update display
			self.theDate_data.set(s)
			
			self.node_data.set("Node: " + oct(header.from_node))
			
			self.temp_data.set(str("%.2f" % temp) + u"\u00b0")
			self.nowTemp = str("%.2f" % temp)
							
			self.hum_data.set(str("%.2f" % hum) + "%")
			self.nowHum = str("%.2f" % hum)
			
			self.heatIndex_data.set(str("%.2f" % heatI) + u"\u00b0")
			self.nowHeatIndex = str("%.2f" % heatI)
			
			self.press_data.set(str("%.2f" % inHg) + " inHg")
			self.nowPressure = str("%.2f" % inHg)
			
			self.idCount_data.set(header.id)
			
			newDay = self.todayRoutines()
			self.yesterdayRoutines(newDay)
			newMonth = self.monthRoutines()
			newYear = self.yearRoutines()
			print 'New Day = ', newDay, '0 = Not a new day and 1 = Is a new day'
			print 'New Month = ', newMonth, '0 = Not a new month and 1 = Is a new month'
			print 'New Year = ', newYear, '0 = Not a new year and 1 = Is a new year'
		
			self.tempRoutines(temp, newDay)
			self.humRoutines(hum, newDay)
			self.heatIRoutines(heatI, newDay)
			self.pressRoutines(inHg, newDay)
			dPoint = self.dewPointRoutines(temp, hum, newDay)
			self.idRoutines(header.id)
			self.minuteFileRoutines()
			root.update()
			self.mySqlRoutines(temp, hum, dPoint, heatI, inHg)
		
		self.after(100,self.update) # 100 milliseconds between reads
		
	# create screen widgets method
	def createWidgets(self):
		
		self.theDate = Label(self, textvariable=self.theDate_data, font=('DroidSerif', 16, 'bold'))
		self.theDate_data.set("")
		self.theDate.grid(row=0, columnspan=14)
		
		self.node = Label(self, textvariable=self.node_data, font=('DroidSerif', 16, 'bold'))
		self.node_data.set("Node")
		self.node.grid(row=1, columnspan=14)
		
		self.temperatureLabel = Label(self, text="Temperature", font=('DroidSerif', 16, 'bold'), padx=10)
		self.temperatureLabel.grid(row=2, column=0, columnspan=2)
		
		self.temp_data_now = Label(self, textvariable=self.temp_data, font=('DroidSerif', 24, 'bold'), padx=10)
		self.temp_data_now.grid(row=3, column=0, columnspan=2)
		
		self.space1 = Label(self, text=" ", font=('DroidSerif', 24, 'bold'), padx=10)
		self.space1.grid(row=3, column=2)
		
		self.humidityLabel = Label(self, text="Humidity", font=('DroidSerif', 16, 'bold'), padx=10)
		self.humidityLabel.grid(row=2, column=3, columnspan=2)
		
		self.hum_data_now = Label(self, textvariable=self.hum_data, font=('DroidSerif', 24, 'bold'), padx=10)
		self.hum_data_now.grid(row=3, column=3, columnspan=2)
		
		self.space2 = Label(self, text=" ", font=('DroidSerif', 24, 'bold'), padx=10)
		self.space2.grid(row=3, column=5)
		
		self.DPLabel = Label(self, text="Dew Point", font=('DroidSerif', 16, 'bold'), padx=10)
		self.DPLabel.grid(row=2, column=6, columnspan=2)
		
		self.DP_data_now = Label(self, textvariable=self.DP_data, font=('DroidSerif', 24, 'bold'), padx=10)
		self.DP_data_now.grid(row=3, column=6, columnspan=2)
		
		self.space3 = Label(self, text=" ", font=('DroidSerif', 24, 'bold'), padx=10)
		self.space3.grid(row=3, column=8)
				
		self.heatIndexLabel = Label(self, text="Heat Index", font=('DroidSerif', 16, 'bold'), padx=10)
		self.heatIndexLabel.grid(row=2, column=9, columnspan=2)
		
		self.heatIndex_data_now = Label(self, textvariable=self.heatIndex_data, font=('DroidSerif', 24, 'bold'), padx=10)
		self.heatIndex_data_now.grid(row=3, column=9, columnspan=2)
		
		self.space4 = Label(self, text=" ", font=('DroidSerif', 24, 'bold'), padx=10)
		self.space4.grid(row=3, column=11)
		
		self.pressureLabel = Label(self, text="Pressure", font=('DroidSerif', 16, 'bold'), padx=10)
		self.pressureLabel.grid(row=2, column=12, columnspan=2)
		
		self.press_data_now = Label(self, textvariable=self.press_data, font=('DroidSerif', 24, 'bold'), padx=10)
		self.press_data_now.grid(row=3, column=12, columnspan=2)
		
		#temp max and min
		self.maximumTempLabel = Label(self, text="Hi Temp:", font=('DroidSerif', 12, 'bold'))
		self.maximumTempLabel.grid(row=4, column=0, sticky=E)
		
		self.maxTemperature = Label(self, textvariable=self.maxTemp_data, font=('DroidSerif', 12, 'bold'), fg='white', bg='red')
		self.maxTemp_data.set("0")
		self.maxTemperature.grid(row=4, column=1, sticky=W)
		
		self.maxTemperatureTime = Label(self, textvariable=self.maxTempTime_data, font=('DroidSerif', 12, 'bold'))
		self.maxTempTime_data.set("")
		self.maxTemperatureTime.grid(row=5, column=0, columnspan=2)
		
		self.minimumTempLabel = Label(self, text="Lo Temp:", font=('DroidSerif', 12, 'bold'))
		self.minimumTempLabel.grid(row=6, column=0, sticky=E)
		
		self.minTemperature = Label(self, textvariable=self.minTemp_data, font=('DroidSerif', 12, 'bold'), fg='white', bg='blue')
		self.minTemp_data.set("200")
		self.minTemperature.grid(row=6, column=1, sticky=W)
		
		self.minTemperatureTime = Label(self, textvariable=self.minTempTime_data, font=('DroidSerif', 12, 'bold'))
		self.minTempTime_data.set("")
		self.minTemperatureTime.grid(row=7, column=0, columnspan=2)
		
		## yesterday temp max and min
		self.temperatureLabelY = Label(self, text="Yesterday", font=('DroidSerif', 12, 'bold'), padx=10)
		self.temperatureLabelY.grid(row=8, column=0, columnspan=2)
		
		self.maximumTempLabelY = Label(self, text="Hi Temp:", font=('DroidSerif', 10, 'bold'))
		self.maximumTempLabelY.grid(row=9, column=0, sticky=E)
		
		self.maxTemperatureY = Label(self, textvariable=self.maxTempYesterday, font=('DroidSerif', 10, 'bold'), fg='white', bg='red')
		self.maxTemperatureY.grid(row=9, column=1, sticky=W)
		
		self.maxTemperatureTimeY = Label(self, textvariable=self.maxTempYesterdayTime, font=('DroidSerif', 10, 'bold'))
		self.maxTemperatureTimeY.grid(row=10, column=0, columnspan=2)
		
		self.minimumTempLabelY = Label(self, text="Lo Temp:", font=('DroidSerif', 10, 'bold'))
		self.minimumTempLabelY.grid(row=11, column=0, sticky=E)
		
		self.minTemperatureY = Label(self, textvariable=self.minTempYesterday, font=('DroidSerif', 10, 'bold'), fg='white', bg='blue')
		self.minTemperatureY.grid(row=11, column=1, sticky=W)
		
		self.minTemperatureTimeY = Label(self, textvariable=self.minTempYesterdayTime, font=('DroidSerif', 10, 'bold'))
		self.minTemperatureTimeY.grid(row=12, column=0, columnspan=2)
		
		#hum max and min
		self.maximumHumLabel = Label(self, text="Hi Hum:", font=('DroidSerif', 12, 'bold'))
		self.maximumHumLabel.grid(row=4, column=3, sticky=E)
		
		self.maxHumidity = Label(self, textvariable=self.maxHum_data, font=('DroidSerif', 12, 'bold'), fg='white', bg='red')
		self.maxHum_data.set("0")
		self.maxHumidity.grid(row=4, column=4, sticky=W)
		
		self.maxHumidityTime = Label(self, textvariable=self.maxHumTime_data, font=('DroidSerif', 12, 'bold'))
		self.maxHumTime_data.set("")
		self.maxHumidityTime.grid(row=5, column=3, columnspan=2)
		
		self.minimumHumLabel = Label(self, text="Lo Hum:", font=('DroidSerif', 12, 'bold'))
		self.minimumHumLabel.grid(row=6, column=3, sticky=E)
		
		self.minHumidity = Label(self, textvariable=self.minHum_data, font=('DroidSerif', 12, 'bold'), fg='white', bg='blue')
		self.minHum_data.set("200")
		self.minHumidity.grid(row=6, column=4, sticky=W)
		
		self.minHumidityTime = Label(self, textvariable=self.minHumTime_data, font=('DroidSerif', 12, 'bold'))
		self.minHumTime_data.set("")
		self.minHumidityTime.grid(row=7, column=3, columnspan=2)
		
		## yesterday hum max and min
		self.humidityLabelY = Label(self, text="Yesterday", font=('DroidSerif', 12, 'bold'), padx=10)
		self.humidityLabelY.grid(row=8, column=3, columnspan=2)
		
		self.maximumHumLabelY = Label(self, text="Hi Hum:", font=('DroidSerif', 10, 'bold'))
		self.maximumHumLabelY.grid(row=9, column=3, sticky=E)
		
		self.maxHumidityY = Label(self, textvariable=self.maxHumYesterday, font=('DroidSerif', 10, 'bold'), fg='white', bg='red')
		self.maxHumidityY.grid(row=9, column=4, sticky=W)
		
		self.maxHumidityTimeY = Label(self, textvariable=self.maxHumYesterdayTime, font=('DroidSerif', 10, 'bold'))
		self.maxHumidityTimeY.grid(row=10, column=3, columnspan=2)
		
		self.minimumHumLabelY = Label(self, text="Lo Hum:", font=('DroidSerif', 10, 'bold'))
		self.minimumHumLabelY.grid(row=11, column=3, sticky=E)
		
		self.minHumidityY = Label(self, textvariable=self.minHumYesterday, font=('DroidSerif', 10, 'bold'), fg='white', bg='blue')
		self.minHumidityY.grid(row=11, column=4, sticky=W)
		
		self.minHumidityTimeY = Label(self, textvariable=self.minHumYesterdayTime, font=('DroidSerif', 10, 'bold'))
		self.minHumidityTimeY.grid(row=12, column=3, columnspan=2)
		
		#dew point max and min
		self.maximumDPLabel = Label(self, text="Hi Dew Pt:", font=('DroidSerif', 12, 'bold'))
		self.maximumDPLabel.grid(row=4, column=6, sticky=E)
		
		self.maxDP = Label(self, textvariable=self.maxDP_data, font=('DroidSerif', 12, 'bold'), fg='white', bg='red')
		self.maxDP_data.set("0")
		self.maxDP.grid(row=4, column=7, sticky=W)
		
		self.maxDPTime = Label(self, textvariable=self.maxDPTime_data, font=('DroidSerif', 12, 'bold'))
		self.maxDPTime_data.set("")
		self.maxDPTime.grid(row=5, column=6, columnspan=2)
		
		self.minimumDPLabel = Label(self, text="Lo Dew Pt:", font=('DroidSerif', 12, 'bold'))
		self.minimumDPLabel.grid(row=6, column=6, sticky=E)
		
		self.minDP = Label(self, textvariable=self.minDP_data, font=('DroidSerif', 12, 'bold'), fg='white', bg='blue')
		self.minDP_data.set("200")
		self.minDP.grid(row=6, column=7, sticky=W)
		
		self.minDPTime = Label(self, textvariable=self.minDPTime_data, font=('DroidSerif', 12, 'bold'))
		self.minDPTime_data.set("")
		self.minDPTime.grid(row=7, column=6, columnspan=2)
		
		## yesterday DP max and min
		self.DPLabelY = Label(self, text="Yesterday", font=('DroidSerif', 12, 'bold'), padx=10)
		self.DPLabelY.grid(row=8, column=6, columnspan=2)
		
		self.maximumDPLabelY = Label(self, text="Hi DP:", font=('DroidSerif', 10, 'bold'))
		self.maximumDPLabelY.grid(row=9, column=6, sticky=E)
		
		self.maxDPY = Label(self, textvariable=self.maxDPYesterday, font=('DroidSerif', 10, 'bold'), fg='white', bg='red')
		self.maxDPY.grid(row=9, column=7, sticky=W)
		
		self.maxDPTimeY = Label(self, textvariable=self.maxDPYesterdayTime, font=('DroidSerif', 10, 'bold'))
		self.maxDPTimeY.grid(row=10, column=6, columnspan=2)
		
		self.minimumDPLabelY = Label(self, text="Lo DP:", font=('DroidSerif', 10, 'bold'))
		self.minimumDPLabelY.grid(row=11, column=6, sticky=E)
		
		self.minDPY = Label(self, textvariable=self.minDPYesterday, font=('DroidSerif', 10, 'bold'), fg='white', bg='blue')
		self.minDPY.grid(row=11, column=7, sticky=W)
		
		self.minDPTimeY = Label(self, textvariable=self.minDPYesterdayTime, font=('DroidSerif', 10, 'bold'))
		self.minDPTimeY.grid(row=12, column=6, columnspan=2)
		
		#heatI max and min
		self.maximumHeatIndexLabel = Label(self, text="Hi Heat I:", font=('DroidSerif', 12, 'bold'))
		self.maximumHeatIndexLabel.grid(row=4, column=9, sticky=E)
		
		self.maxHeatIndex = Label(self, textvariable=self.maxHeatIndex_data, font=('DroidSerif', 12, 'bold'), fg='white', bg='red')
		self.maxHeatIndex_data.set("0")
		self.maxHeatIndex.grid(row=4, column=10, sticky=W)
		
		self.maxHeatIndexTime = Label(self, textvariable=self.maxHeatIndexTime_data, font=('DroidSerif', 12, 'bold'))
		self.maxHeatIndexTime_data.set("")
		self.maxHeatIndexTime.grid(row=5, column=9, columnspan=2)
		
		self.minimumHeatIndexLabel = Label(self, text="Lo Heat I:", font=('DroidSerif', 12, 'bold'))
		self.minimumHeatIndexLabel.grid(row=6, column=9, sticky=E)
		
		self.minHeatIndex = Label(self, textvariable=self.minHeatIndex_data, font=('DroidSerif', 12, 'bold'), fg='white', bg='blue')
		self.minHeatIndex_data.set("200")
		self.minHeatIndex.grid(row=6, column=10, sticky=W)
		
		self.minHeatIndexTime = Label(self, textvariable=self.minHeatIndexTime_data, font=('DroidSerif', 12, 'bold'))
		self.minHeatIndexTime_data.set("")
		self.minHeatIndexTime.grid(row=7, column=9, columnspan=2)
		
		## yesterday Heat Index max and min
		self.HeatIndexLabelY = Label(self, text="Yesterday", font=('DroidSerif', 12, 'bold'), padx=10)
		self.HeatIndexLabelY.grid(row=8, column=9, columnspan=2)
		
		self.maximumHeatIndexLabelY = Label(self, text="Hi Heat I:", font=('DroidSerif', 10, 'bold'))
		self.maximumHeatIndexLabelY.grid(row=9, column=9, sticky=E)
		
		self.maxHeatIndexY = Label(self, textvariable=self.maxHeatIndexYesterday, font=('DroidSerif', 10, 'bold'), fg='white', bg='red')
		self.maxHeatIndexY.grid(row=9, column=10, sticky=W)
		
		self.maxHeatIndexTimeY = Label(self, textvariable=self.maxHeatIndexYesterdayTime, font=('DroidSerif', 10, 'bold'))
		self.maxHeatIndexTimeY.grid(row=10, column=9, columnspan=2)
		
		self.minimumHeatIndexLabelY = Label(self, text="Lo Heat I:", font=('DroidSerif', 10, 'bold'))
		self.minimumHeatIndexLabelY.grid(row=11, column=9, sticky=E)
		
		self.minHeatIndexY = Label(self, textvariable=self.minHeatIndexYesterday, font=('DroidSerif', 10, 'bold'), fg='white', bg='blue')
		self.minHeatIndexY.grid(row=11, column=10, sticky=W)
		
		self.minHeatIndexTimeY = Label(self, textvariable=self.minHeatIndexYesterdayTime, font=('DroidSerif', 10, 'bold'))
		self.minHeatIndexTimeY.grid(row=11, column=10, columnspan=2)
		
		#press max and min
		self.maximumPressLabel = Label(self, text="Hi Press:", font=('DroidSerif', 12, 'bold'))
		self.maximumPressLabel.grid(row=4, column=12, sticky=E)
		
		self.maxPress = Label(self, textvariable=self.maxPress_data, font=('DroidSerif', 12, 'bold'), fg='white', bg='red')
		self.maxPress_data.set("0")
		self.maxPress.grid(row=4, column=13, sticky=W)
		
		self.maxPressTime = Label(self, textvariable=self.maxPressTime_data, font=('DroidSerif', 12, 'bold'))
		self.maxPressTime_data.set("")
		self.maxPressTime.grid(row=5, column=12, columnspan=2)
		
		self.minimumPressLabel = Label(self, text="Lo Press:", font=('DroidSerif', 12, 'bold'))
		self.minimumPressLabel.grid(row=6, column=12, sticky=E)
		
		self.minPress = Label(self, textvariable=self.minPress_data, font=('DroidSerif', 12, 'bold'), fg='white', bg='blue')
		self.minPress_data.set("200")
		self.minPress.grid(row=6, column=13, sticky=W)
		
		self.minPressTime = Label(self, textvariable=self.minPressTime_data, font=('DroidSerif', 12, 'bold'))
		self.minPressTime_data.set("")
		self.minPressTime.grid(row=7, column=12, columnspan=2)
		
		## yesterday pressure max and min
		self.PressLabelY = Label(self, text="Yesterday", font=('DroidSerif', 12, 'bold'), padx=10)
		self.PressLabelY.grid(row=8, column=12, columnspan=2)
		
		self.maximumPressLabelY = Label(self, text="Hi Press:", font=('DroidSerif', 10, 'bold'))
		self.maximumPressLabelY.grid(row=9, column=12, sticky=E)
		
		self.maxPressY = Label(self, textvariable=self.maxPressYesterday, font=('DroidSerif', 10, 'bold'), fg='white', bg='red')
		self.maxPressY.grid(row=9, column=13, sticky=W)
		
		self.maxPressTimeY = Label(self, textvariable=self.maxPressYesterdayTime, font=('DroidSerif', 10, 'bold'))
		self.maxPressTimeY.grid(row=10, column=12, columnspan=2)
		
		self.minimumPressLabelY = Label(self, text="Lo Press:", font=('DroidSerif', 10, 'bold'))
		self.minimumPressLabelY.grid(row=11, column=12, sticky=E)
		
		self.minPressY = Label(self, textvariable=self.minPressYesterday, font=('DroidSerif', 10, 'bold'), fg='white', bg='blue')
		self.minPressY.grid(row=11, column=13, sticky=W)
		
		self.minPressTimeY = Label(self, textvariable=self.minPressYesterdayTime, font=('DroidSerif', 10, 'bold'))
		self.minPressTimeY.grid(row=12, column=12, columnspan=2)
		
		# packet displays
		self.idLabel = Label(self, text="Packet ID:", bd=1, relief=SUNKEN)
		self.idLabel.grid(row=13, column=3, sticky=E)
		
		self.counterRawDisplay = Label(self, textvariable = self.idCount_data, bd=1, relief=SUNKEN)
		self.idCount_data.set("0")
		self.counterRawDisplay.grid(row=13, column=4, sticky=W)
		
		self.idLostLabel = Label(self, text="Lost Packets:", bd=1, relief=SUNKEN)
		self.idLostLabel.grid(row=13, column=6, sticky=E)
		
		self.idLostDisplay = Label(self, textvariable = self.idLost_data, bd=1, relief=SUNKEN)
		self.idLost_data.set("0")
		self.idLostDisplay.grid(row=13, column=7, sticky=W)
		
		# quit button
		self.end_program = Button(self, text = "Quit", command = self.quit)
		self.end_program.grid(row=13, column=9, columnspan=2)
		
		# set today variable
		self.todaySaved.set(0)
		
	def tempRoutines(self, x, newDay):
		format = "%I:%M %p"
		d = datetime.today()
		s = d.strftime(format)
		y = self.maxTemp_data.get()
		z = self.minTemp_data.get()
		print "Current temperature is ", "%.2f" % x
		print "Previous max temperature is ", "%.2f" % y
		print "Previous min temperature is ", "%.2f" % z
		print "----------------------"
		if newDay == 0:
			if x > y:
				self.maxTemp_data.set("%.2f" % x)
				self.maxTempTime_data.set(s)
			if x < z:
				self.minTemp_data.set("%.2f" % x)
				self.minTempTime_data.set(s)
		else:
			self.maxTemp_data.set("%.2f" % x)
			self.maxTempTime_data.set(s)
			self.minTemp_data.set("%.2f" % x)
			self.minTempTime_data.set(s)
		
			
	def humRoutines(self, x, newDay):
		format = "%I:%M %p"
		d = datetime.today()
		s = d.strftime(format)
		y = self.maxHum_data.get()
		z = self.minHum_data.get()
		print "Current Humidity is ", "%.2f" % x
		print "Previous max humidity is ", "%.2f" % y
		print "Previous min humidity is ", "%.2f" % z
		print "----------------------"
		if newDay == 0:
			if x > y:
				self.maxHum_data.set("%.2f" % x)
				self.maxHumTime_data.set(s)
			if x < z:
				self.minHum_data.set("%.2f" % x)
				self.minHumTime_data.set(s)
		else:
			self.maxHum_data.set("%.2f" % x)
			self.maxHumTime_data.set(s)
			self.minHum_data.set("%.2f" % x)
			self.minHumTime_data.set(s)
			
	def heatIRoutines(self, x, newDay):
		format = "%I:%M %p"
		d = datetime.today()
		s = d.strftime(format)
		y = self.maxHeatIndex_data.get()
		z = self.minHeatIndex_data.get()
		print "Current Heat Index is ", "%.2f" % x
		print "Previous max heat index is ", "%.2f" % y
		print "Previous min heat index is ", "%.2f" % z
		print "----------------------"
		if newDay == 0:
			if x > y:
				self.maxHeatIndex_data.set("%.2f" % x)
				self.maxHeatIndexTime_data.set(s)
			if x < z:
				self.minHeatIndex_data.set("%.2f" % x)
				self.minHeatIndexTime_data.set(s)
		else:
			self.maxHeatIndex_data.set("%.2f" % x)
			self.maxHeatIndexTime_data.set(s)
			self.minHeatIndex_data.set("%.2f" % x)
			self.minHeatIndexTime_data.set(s)
			
	def pressRoutines(self, x, newDay):
		format = "%I:%M %p"
		d = datetime.today()
		s = d.strftime(format)
		y = self.maxPress_data.get()
		z = self.minPress_data.get()
		print "Current Pressure is ", "%.2f" % x
		print "Previous max pressure is ", "%.2f" % y
		print "Previous min press is ", "%.2f" % z
		print "----------------------"
		if newDay == 0:
			if x > y:
				self.maxPress_data.set("%.2f" % x)
				self.maxPressTime_data.set(s)
			if x < z:
				self.minPress_data.set("%.2f" % x)
				self.minPressTime_data.set(s)
		else:
			self.maxPress_data.set("%.2f" % x)
			self.maxPressTime_data.set(s)
			self.minPress_data.set("%.2f" % x)
			self.minPressTime_data.set(s)
			
	def dewPointRoutines(self, tmp, hum, newDay):
		# convert temp to celcius
		c = (tmp - 32.0) * 0.555556
		# formula for simplified dew point using just temp and hum
		# formula from http://pydoc.net/Python/weather/0.9.1/weather.units.temp/
		x = 1 - 0.01 * hum
		dewpoint = (14.55 + 0.114 * c) * x
		dewpoint = dewpoint + ((2.5 + 0.007 * c) * x) ** 3
		dewpoint = dewpoint + (15.9 + 0.117 * c) * x ** 14
		dewpoint = c - dewpoint
		# convert dewpoint to fahrenheit
		f = (dewpoint * 1.8) + 32
		self.DP_data.set("%.2f" % f)
		format = "%I:%M %p"
		d = datetime.today()
		s = d.strftime(format)
		y = self.maxDP_data.get()
		z = self.minDP_data.get()
		print "Current Dew Point is ", "%.2f" % f
		print "Previous max dew point is ", "%.2f" % y
		print "Previous min dew point is ", "%.2f" % z
		print "----------------------"
		if newDay == 0:
			if f > y:
				self.maxDP_data.set("%.2f" % f)
				self.maxDPTime_data.set(s)
			if f < z:
				self.minDP_data.set("%.2f" % f)
				self.minDPTime_data.set(s)
		else:
			self.maxDP_data.set("%.2f" % f)
			self.maxDPTime_data.set(s)
			self.minDP_data.set("%.2f" % f)
			self.minDPTime_data.set(s)
		return f
			
	# monitors and reports lost packets
	def idRoutines(self, x):
		self.idCount_data.set(x)
		y = self.idPreviousCount_data.get()
		z = x - y
		if y == 0:
			self.idPreviousCount_data.set(x)
		else:
			if z > 1:
				self.idLost_data.set(z)
				self.idPreviousCount_data.set(x)
			self.idPreviousCount_data.set(x)
		
	def todayRoutines(self):
		#get day by number
		format = "%d"
		d = datetime.today()
		s = int(d.strftime(format))
		# get previously saved day
		x = self.todaySaved.get()
		print "Today number is ", s, " and previous day number is ", x
		print"----------------------"
		if x == s:
			return 0
		else:
			print "New saved day is ", s
			self.todaySaved.set(s)
			return 1
			
	def yesterdayRoutines(self, newDay):
		if newDay == 1:
			self.maxTempYesterday.set(self.maxTemp_data.get())
			self.maxTempYesterdayTime.set(self.maxTempTime_data.get())
			self.minTempYesterday.set(self.minTemp_data.get())
			self.minTempYesterdayTime.set(self.minTempTime_data.get())
			self.maxHumYesterday.set(self.maxHum_data.get())
			self.maxHumYesterdayTime.set(self.maxHumTime_data.get())
			self.minHumYesterday.set(self.minHum_data.get())
			self.minHumYesterdayTime.set(self.minHumTime_data.get())
			self.maxDPYesterday.set(self.maxDP_data.get())
			self.maxDPYesterdayTime.set(self.maxDPTime_data.get())
			self.minDPYesterday.set(self.minDP_data.get())
			self.minDPYesterdayTime.set(self.minDPTime_data.get())
			self.maxHeatIndexYesterday.set(self.maxHeatIndex_data.get())
			self.maxHeatIndexYesterdayTime.set(self.maxHeatIndexTime_data.get())
			self.minHeatIndexYesterday.set(self.minHeatIndex_data.get())
			self.minHeatIndexYesterdayTime.set(self.minHeatIndexTime_data.get())
			self.maxPressYesterday.set(self.maxPress_data.get())
			self.maxPressYesterdayTime.set(self.maxPressTime_data.get())
			self.minPressYesterday.set(self.minPress_data.get())
			self.minPressYesterdayTime.set(self.minPressTime_data.get())
		
			
	def monthRoutines(self):
		format2 = "%m"
		d = datetime.today()
		m = int(d.strftime(format2))
		pm = self.monthSaved.get()
		print "Month number is ", m, " and previous month number is ", pm
		print"----------------------"
		if m == pm:
			return 0
		else:
			print "New saved month is ", m
			self.monthSaved.set(m)
			return 1
			
	def yearRoutines(self):
		format3 = "%Y"
		d = datetime.today()
		yr = int(d.strftime(format3))
		py = self.yearSaved.get()
		print "Year number is ", yr, " and previous year number is ", py
		print"----------------------"
		if yr == py:
			return 0
		else:
			print "New saved year is ", yr
			self.yearSaved.set(yr)
			return 1
			
	def mySqlRoutines(self, temp, hum, dPoint, heatI, inHg):
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
			
	def minuteFileRoutines(self):
		format1 = "%m-%d-%Y"
		format2 = "%H:%M"
		d = datetime.today()
		mDy = d.strftime(format1)
		mH = d.strftime(format2)
		outFile = open('weather.csv', "ab")
		writeFile = csv.writer(outFile, delimiter=',', quoting=csv.QUOTE_ALL)
		tmp = self.nowTemp
		hum = self.nowHum
		dp = self.DP_data.get()
		hI = self.nowHeatIndex
		press = self.nowPressure
		node = self.node_data.get()
		packet = self.idCount_data.get()
		row = mDy, mH, tmp, hum, dp, hI, press, node, packet
		writeFile.writerow(row)
		outFile.close()
		
	# quit program method
	def quit(self):
		root.quit()
		root.destroy()
	
	# start radio and network	
	def setupRadio(self):
		radio.begin()
		radio.setDataRate(RF24_250KBPS)
		radio.printDetails()
		time.sleep(0.1)
		network.begin(90, this_node)    # channel 90
		
		print 'Network up. This is node ', this_node
				
	# initialization	
	def __init__(self, master=None):
		Frame.__init__(self, master)
		root.title("RasPi Weather")
		self.setupRadio()
		self.counter = IntVar()
		self.theDate_data = StringVar()
		self.node_data = StringVar()
		# packet variables
		self.idCount_data = IntVar()
		self.idPreviousCount_data = IntVar()
		self.idLost_data = IntVar()
		# temperature variables
		self.temp_data = StringVar()
		self.nowTemp = DoubleVar()
		self.maxTemp_data = DoubleVar()
		self.maxTempTime_data = StringVar()
		self.minTemp_data = DoubleVar()
		self.minTempTime_data = StringVar()
		self.maxTempYesterday = DoubleVar()
		self.maxTempYesterdayTime = StringVar()
		self.minTempYesterday = DoubleVar()
		self.minTempYesterdayTime = StringVar()
		self.maxTempMonth = DoubleVar()
		self.maxTempMonthTime = StringVar()
		self.minTempMonth = DoubleVar()
		self.minTempMonthTime = StringVar()
		self.maxTempYear = DoubleVar()
		self.maxTempYearTime = StringVar()
		self.minTempYear = DoubleVar()
		self.minTempYearTime = StringVar()
		self.maxTempAll = DoubleVar()
		self.maxTempAllTime = StringVar()
		self.minTempAll = DoubleVar()
		self.minTempAllTime = StringVar()
		# humidity variables
		self.hum_data = StringVar()
		self.nowHum = DoubleVar()
		self.maxHum_data = DoubleVar()
		self.maxHumTime_data = StringVar()
		self.minHum_data = DoubleVar()
		self.minHumTime_data = StringVar()
		self.maxHumYesterday = DoubleVar()
		self.maxHumYesterdayTime = StringVar()
		self.minHumYesterday = DoubleVar()
		self.minHumYesterdayTime = StringVar()
		self.maxHumMonth = DoubleVar()
		self.maxHumMonthTime = StringVar()
		self.minHumMonth = DoubleVar()
		self.minHumMonthTime = StringVar()
		self.maxHumYear = DoubleVar()
		self.maxHumYearTime = StringVar()
		self.minHumYear = DoubleVar()
		self.minHumYearTime = StringVar()
		self.maxHumAll = DoubleVar()
		self.maxHumAllTime = StringVar()
		self.minHumAll = DoubleVar()
		self.minHumAllTime = StringVar()
		# dew point variables
		self.DP_data = StringVar()
		self.nowDP = DoubleVar()
		self.maxDP_data = DoubleVar()
		self.maxDPTime_data = StringVar()
		self.minDP_data = DoubleVar()
		self.minDPTime_data = StringVar()
		self.maxDPYesterday = DoubleVar()
		self.maxDPYesterdayTime = StringVar()
		self.minDPYesterday = DoubleVar()
		self.minDPYesterdayTime = StringVar()
		self.maxDPMonth = DoubleVar()
		self.maxDPMonthTime = StringVar()
		self.minDPMonth = DoubleVar()
		self.minDPMonthTime = StringVar()
		self.maxDPYear = DoubleVar()
		self.maxDPYearTime = StringVar()
		self.minDPYear = DoubleVar()
		self.minDPYearTime = StringVar()
		self.maxDPAll = DoubleVar()
		self.maxDPAllTime = StringVar()
		self.minDPAll = DoubleVar()
		self.minDPAllTime = StringVar()
		# heat index variables
		self.heatIndex_data = StringVar()
		self.nowHeatIndex = DoubleVar()
		self.maxHeatIndex_data = DoubleVar()
		self.maxHeatIndexTime_data = StringVar()
		self.minHeatIndex_data = DoubleVar()
		self.minHeatIndexTime_data = StringVar()
		self.maxHeatIndexYesterday = DoubleVar()
		self.maxHeatIndexYesterdayTime = StringVar()
		self.minHeatIndexYesterday = DoubleVar()
		self.minHeatIndexYesterdayTime = StringVar()
		self.maxHeatIndexMonth = DoubleVar()
		self.maxHeatIndexMonthTime = StringVar()
		self.minHeatIndexMonth = DoubleVar()
		self.minHeatIndexMonthTime = StringVar()
		self.maxHeatIndexYear = DoubleVar()
		self.maxHeatIndexYearTime = StringVar()
		self.minHeatIndexYear = DoubleVar()
		self.minHeatIndexYearTime = StringVar()
		self.maxHeatIndexAll = DoubleVar()
		self.maxHeatIndexAllTime = StringVar()
		self.minHeatIndexAll = DoubleVar()
		self.minHeatIndexAllTime = StringVar()
		# pressure data
		self.press_data = StringVar()
		self.nowPress = DoubleVar()
		self.maxPress_data = DoubleVar()
		self.maxPressTime_data = StringVar()
		self.minPress_data = DoubleVar()
		self.minPressTime_data = StringVar()
		self.maxPressYesterday = DoubleVar()
		self.maxPressYesterdayTime = StringVar()
		self.minPressYesterday = DoubleVar()
		self.minPressYesterdayTime = StringVar()
		self.maxPressMonth = DoubleVar()
		self.maxPressMonthTime = StringVar()
		self.minPressMonth = DoubleVar()
		self.minPressMonthTime = StringVar()
		self.maxPressYear = DoubleVar()
		self.maxPressYearTime = StringVar()
		self.minPressYear = DoubleVar()
		self.minPressYearTime = StringVar()
		self.maxPressAll = DoubleVar()
		self.maxPressAllTime = StringVar()
		self.minPressAll = DoubleVar()
		self.minPressAllTime = StringVar()
		# today month year variables
		self.todayIs = IntVar()
		self.todaySaved = IntVar()
		self.monthSaved = IntVar()
		self.yearSaved = IntVar()
		# set today variable
		#self.todaySaved.set('0')
				
		self.createWidgets()
		self.pack()
		self.update()

# create a Tkinter window
root = Tk()

# initialize the application
app = Application(master=root)

# application loop
app.mainloop()
