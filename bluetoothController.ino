#include <ArduinoBLE.h>



// Bluetooth definitions
BLEService controlService("180A"); // BLE LED Service

BLEIntCharacteristic controlCharacteristic("e5c9e235-7cee-4640-ba95-7073c4afbbf8",BLERead | BLEWrite);
// Controll definitions

// Josystick
#define VRX_PIN A0
#define VRY_PIN A1

int xValue=0;
int yValue=0;


// Buttons
const int stickClickPin=12;
const int buttonClick1Pin=3;
const int buttonClick2Pin=4;
const int buttonClick3Pin=5;
const int buttonClick4Pin=6;


int stickClick=0;
int buttonClick1=0;
int buttonClick2=0;
int buttonClick3=0;
int buttonClick4=0;

// Led

const int ledPin=2;



void setup() {
  Serial.begin(9600);
  


  //Set pin states
  pinMode(stickClickPin,INPUT_PULLUP);
  pinMode(buttonClick1Pin,INPUT);
  pinMode(buttonClick2Pin,INPUT);

  pinMode(ledPin,OUTPUT);
  digitalWrite(ledPin,LOW);

  
  // begin initialization
  if (!BLE.begin()) {
    Serial.println("starting Bluetooth® Low Energy failed!");

    while (1);
  }

  // set advertised local name and service UUID:
  BLE.setLocalName("Nano 33 IoT");
  BLE.setAdvertisedService(controlService);

  // add the characteristic to the service
  controlService.addCharacteristic(controlCharacteristic);

  // add service
  BLE.addService(controlService);

  // set the initial value for the characteristic:
  controlCharacteristic.writeValue(0);
  
  // start advertising
  BLE.advertise();

  Serial.println("BLE LED Peripheral");
}

void loop() {
  
  
  
  
  // listen for BLE peripherals to connect:
  BLEDevice central = BLE.central();
  
  // if a central is connected to peripheral:
  if (central) {
    Serial.print("Connected to central: ");
    // print the central's MAC address:
    Serial.println(central.address());

    //Turn on light when connected
    digitalWrite(ledPin,HIGH);

    // while the central is still connected to peripheral:
    while (central.connected()) {
      // Joystick
      xValue=analogRead(VRX_PIN);
      yValue=analogRead(VRY_PIN);

    
      //Button logic
      
      
      stickClick=digitalRead(stickClickPin);
      buttonClick1=digitalRead(buttonClick1Pin);
      buttonClick2=digitalRead(buttonClick2Pin);
      buttonClick3=digitalRead(buttonClick3Pin);
      buttonClick4=digitalRead(buttonClick4Pin);
      //Write value over bluetooth
      controlCharacteristic.writeValue(xValue/4+yValue/4*256+stickClick*256*256+buttonClick1*2*256*256+buttonClick2*4*256*256+buttonClick3*8*256*256+buttonClick4*16*256*256); //Divide by 4 so values fit in a byte
      
      
    }
    
    // when the central disconnects, print it out:
    Serial.print(F("Disconnected from central: "));
    Serial.println(central.address());

    // Turn off light when disconnected
    digitalWrite(ledPin,LOW);
  }
}
