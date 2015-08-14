#RasPiWeather

**RasPiWeather** is a project using a Raspberry Pi as a hub for gathering data from Arduino weather nodes, storing the data in a MySQL database, and uploading the data to Weather Underground and a Sparkfun cloud database. The data is transmitted from the weather nodes to the Raspberry Pi via a wireless NRF24L01+ network.

The Raspberry Pi is a **Model B**, running Raspian. Presently there are two Arduino nodes used in the wireless network. The weather node is an **Arduino Pro Mini** with an NRF24L01+ transceiver, a DHT22 temperature and humidity sensor, and a BMP085 pressure sensor. The second node is used as a repeater to extend the distance of the weather node. The repeater node is an **Arduino Pro Mini** with an NRF24L01+ transceiver.
