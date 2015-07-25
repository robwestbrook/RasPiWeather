
#include <RF24Network.h>
#include <RF24.h>
#include <SPI.h>

RF24 radio(9,10);                    // nRF24L01(+) radio attached using Getting Started board 

RF24Network network(radio);          // Network uses that radio

const uint16_t this_node = 01;        // Address of our node in Octal format
const uint16_t other_node = 00;       // Address of the other node in Octal format

void setup(void)
{
  Serial.begin(9600);
  Serial.println("RF24Network/examples/helloworld_tx/");
  SPI.begin();
  radio.begin();
  radio.setRetries(15,15);
  radio.setPALevel(RF24_PA_HIGH);
  radio.setDataRate(RF24_250KBPS);
  radio.printDetails();
  network.begin(/*channel*/ 90, /*node address*/ this_node);
}

void loop() {
  network.update();                          // Check the network regularly
}


