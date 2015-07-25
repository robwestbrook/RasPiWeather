/******************************
 * Send weather data via the
 * RF24Network to the
 * Raspberry Pi
 */

// libraries
#include <Wire.h>
#include <SPI.h>
#include <RF24Network.h>
#include <RF24.h>
#include "DHT.h"
#include <SFE_BMP180.h>

// altitude for Becker, MS
#define ALTITUDE 71.0

// object for barometric pressure sensor
SFE_BMP180 pressure;


#define DHTPIN 6          // what pin we're connected to
#define DHTTYPE DHT22     // DHT 22  (AM2302)
DHT dht(DHTPIN, DHTTYPE); // DHT 22 object

float temperature = 0.0;
float humidity = 0.0;
float heatIndex = 0.0;
float inHg = 0.0;

// variables for BMP180 data
 double T,P,p0,a;
 char status;

unsigned long previousMillis = 0;
const long interval = 60000;          // 60 second interval

RF24 radio(9,10);                     // NRF24L01+ on pins 9 & 10

RF24Network network(radio);           // Network uses that radio

const uint16_t this_node = 011;       // Address of our node in Octal format
const uint16_t other_node = 00;       // Address of the other node in Octal format

unsigned long last_sent;              // When did we last send?
unsigned long packets_sent;           // How many have we sent already

struct payload_t {                    // Structure of our payload
  float t;        // temperature
  float h;        // humidity
  float hi;       // heat index
  float p;        // pressure
};

void setup() {
  Serial.begin(9600);

  // start DHT 22
  dht.begin();
  
  // start BMP180
  pressure.begin();
    
  SPI.begin();
  radio.begin();
  radio.setDataRate(RF24_250KBPS);
  network.begin(/*channel*/ 90, /*node address*/ this_node);

}

void loop() {

  network.update();                          // Check the network regularly

  
  unsigned long currentMillis = millis();
  
  if(currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;    
    readDHT22();
    
    status = pressure.startTemperature();
    if (status != 0)
    {
      // Wait for the measurement to complete:
      delay(status);

      // Retrieve the completed temperature measurement:
      // Note that the measurement is stored in the variable T.
      // Function returns 1 if successful, 0 if failure.

      status = pressure.getTemperature(T);
      if (status != 0)
      {
        // Start a pressure measurement:
        // The parameter is the oversampling setting, from 0 to 3 (highest res, longest wait).
        // If request is successful, the number of ms to wait is returned.
        // If request is unsuccessful, 0 is returned.

        status = pressure.startPressure(3);
        if (status != 0)
        {
          // Wait for the measurement to complete:
          delay(status);

          // Retrieve the completed pressure measurement:
          // Note that the measurement is stored in the variable P.
          // Note also that the function requires the previous temperature measurement (T).
          // (If temperature is stable, you can do one temperature measurement for a number of pressure measurements.)
          // Function returns 1 if successful, 0 if failure.

          status = pressure.getPressure(P,T);
          if (status != 0)
          {
            // The pressure sensor returns abolute pressure, which varies with altitude.
            // To remove the effects of altitude, use the sealevel function and your current altitude.
            // This number is commonly used in weather reports.
            // Parameters: P = absolute pressure in mb, ALTITUDE = current altitude in m.
            // Result: p0 = sea-level compensated pressure in mb

            p0 = pressure.sealevel(P,ALTITUDE); // we're at 1655 meters (Boulder, CO)
            inHg = p0*0.0295333727,2;
            
            // On the other hand, if you want to determine your altitude from the pressure reading,
            // use the altitude function along with a baseline pressure (sea-level or other).
            // Parameters: P = absolute pressure in mb, p0 = baseline pressure in mb.
            // Result: a = altitude in m.

            a = pressure.altitude(P,p0);
           
          }
          else Serial.println("error retrieving pressure measurement\n");
        }
        else Serial.println("error starting pressure measurement\n");
      }
      else Serial.println("error retrieving temperature measurement\n");
    }
    else Serial.println("error starting temperature measurement\n");
    
    
    // add values to struct
    payload_t payload = { temperature, humidity, heatIndex, inHg };
    // prepare header
    RF24NetworkHeader header(/*to node*/ other_node);
    // send
    bool ok = network.write(header,&payload,sizeof(payload));
    if (ok)
    {
      Serial.println("ok.");
      }
    else
    {
      Serial.println("failed.");
    }
  }
}

void readDHT22() {
    temperature = dht.readTemperature(true);
    humidity = dht.readHumidity();
    heatIndex = dht.computeHeatIndex(temperature, humidity);
}
