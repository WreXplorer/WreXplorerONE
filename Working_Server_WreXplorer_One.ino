#include <Dhcp.h>
#include <Dns.h>
#include <Ethernet.h>
#include <EthernetClient.h>
#include <EthernetServer.h>
#include <EthernetUdp.h>
#include <util.h>
#include <SPI.h>

boolean lights = false; // whether lights are on or off
float setDepth = 0.0;
char setDepthChar[5];
float myDepth = 0.0;
char myDepthChar[5];
float volts = 0.0;
char voltsChar[5];
char msg = 'j';
char ltsSts = '-';
char lock = '-';

// Enter a MAC address and IP address for your controller below.
// The IP address will be dependent on your local network.
byte mac[] = {
  0x90, 0xA2, 0xDA, 0x00, 0xDF, 0xA5};
IPAddress ip(192,168,1,122);

EthernetServer server(8080);
boolean gotAMessage = false; // whether or not you got a message from the client yet

// digital pins 4, 10-13 cannot be used for standard i/o, used for ethernet board
void setup() {
  for(int x=2; x<4; x++){
    pinMode(x, OUTPUT);
  }
  for(int x=5; x<10; x++){
    pinMode(x, OUTPUT);
  }
  pinMode(A0, OUTPUT);
  pinMode(A1, INPUT);
  pinMode(A2, INPUT);
  // initialize the ethernet device
  Ethernet.begin(mac, ip);
  // start listening for clients
  server.begin();
  // open the serial port
  Serial.begin(9600);
}

void setPins(){
  for(int x=2; x<4; x++){
    digitalWrite(x, LOW);
  }
  for(int x=5; x<7; x++){
    digitalWrite(x, LOW);
  }
  if(lock=='-'){
    digitalWrite(7, LOW);
    digitalWrite(8, LOW);
  }

}

void loop() {
  // wait for a new clients:
  EthernetClient client = server.available();

  // when the client sends the first byte, say hello:
  if (client) {
    if (!gotAMessage) {
      Serial.println("We have a new client");
      gotAMessage = true;
    }

    // read the bytes incoming from the client:
    char thisChar = client.read();
    // determine the action:
    msg = 'j';
    if (thisChar == 'w')
    {
      msg = 'w';
      Serial.println("forward");
      setPins();
      digitalWrite(2, HIGH);
      digitalWrite(5, HIGH);
      digitalWrite(A0, HIGH);
    }
    else if (thisChar == 'x')
    {
      msg = 'x';
      Serial.println("backward");
      setPins();
      digitalWrite(3, HIGH);
      digitalWrite(6, HIGH);
      digitalWrite(A0, HIGH);
    }
    else if (thisChar == 'a')
    {
      msg = 'a';
      Serial.println("left");
      digitalWrite(A0, HIGH);
    }
    else if (thisChar == 'd')
    {
      msg = 'd';
      Serial.println("right");
      digitalWrite(A0, HIGH);
    }
    else if (thisChar == 'q')
    {
      msg = 'q';
      Serial.println("counter-clockwise");
      setPins();
      digitalWrite(3, HIGH);
      digitalWrite(5, HIGH);
      digitalWrite(A0, HIGH);
    }
    else if (thisChar == 'e')
    {
      msg = 'e';
      Serial.println("clockwise");
      setPins();
      digitalWrite(2, HIGH);
      digitalWrite(6, HIGH);
      digitalWrite(A0, HIGH);
    }
    else if (thisChar == 'z') // ascend
    {
      msg = 'z';
      setPins();
      if(lock=='+')
      {
        if (setDepth>1)
        {
          setDepth = setDepth - 1;
        }
      }
      else
      {
        digitalWrite(7, HIGH);
        digitalWrite(8, LOW);
        Serial.println("up");
      }
      digitalWrite(A0, HIGH);
    }
    else if (thisChar == 'c')
    {
      msg = 'c';
      setPins();
      if(lock=='+')
      {
        setDepth = setDepth + 1;

      }
      else
      {
        digitalWrite(7, LOW);
        digitalWrite(8, HIGH);
        Serial.println("down");
      }
      digitalWrite(A0, HIGH);
    }
    else if (thisChar == 'b')
    {
      if (lock == '-')
      {
        msg = 'b';
        Serial.println("lock on");
        digitalWrite(7, LOW);
        digitalWrite(8, LOW);
        digitalWrite(A0, HIGH);
        lock = '+';
      }
      else
      {
        msg = 'b';
        Serial.println("lock off");
        digitalWrite(A0, HIGH);
        lock = '-';
      }
    }
    else if (thisChar == 's')
    {
      msg = 's';
      Serial.println("stop bot");
      setPins();
      digitalWrite(A0, LOW);
    }
    else if (thisChar == 'l')
    {
      if (lights == false)
      {
        msg = 'l';
        Serial.println("lights on");
        digitalWrite(9, HIGH);
        digitalWrite(A0, HIGH);
        lights = true;
        ltsSts = '+';
      }
      else
      {
        msg = 'l';
        Serial.println("lights already on");
        digitalWrite(A0, HIGH);
      }
    }
    else if (thisChar == 'k')
    {
      if (lights == true)
      {
        msg = 'k';
        Serial.println("lights off");
        digitalWrite(9, LOW);
        digitalWrite(A0, HIGH);
        lights = false;
        ltsSts = '-';
      }
      else
      {
        msg = 'k';
        Serial.println("lights already off");
        digitalWrite(A0, HIGH);
      }
    }
    else
    {
      msg = '?';
      Serial.println("unknown");
    }
  }
  if(gotAMessage == true)
  {
    //Send data to controller
    // Get depth
    myDepth = (analogRead(A1)* (5.0 / 1024.0));
    myDepth = round((((myDepth-1)*30)/14.7)*33);
    delay(100);
    // Get voltage
    volts = (analogRead(A2)* (5.0 / 1024.0));
    delay(100);
    if(lock=='+')
    {
      if(setDepth<myDepth)
      {
        Serial.println("ascend");
        digitalWrite(7, HIGH);
      }
      else if(setDepth>myDepth)
      {
        Serial.println("descend");
        digitalWrite(8, HIGH);
      }
      else
      {
        digitalWrite(7, LOW);
        digitalWrite(8, LOW);
      }
    }
    else
    {
      setDepth=myDepth;
    }

    // convert numbers to char arrays for sending to the client
    itoa(myDepth, myDepthChar, 10);
    itoa(setDepth, setDepthChar, 10);
    volts = volts*100;
    itoa(volts, voltsChar, 10);

    //send the message to the client
    server.write('$');
    server.write(myDepthChar);
    server.write(',');
    server.write(msg);
    server.write(',');
    server.write(setDepthChar);
    server.write(',');
    server.write(ltsSts);
    server.write(',');
    server.write(voltsChar);
    server.write(',');
    server.write(lock);
    server.write(',');
    server.write(heading);
    server.write('@');
  }
}







