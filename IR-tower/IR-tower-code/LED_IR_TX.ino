
#include <Arduino.h>

/*
   Define macros for input and output pin etc.
*/
#include "PinDefinitionsAndMore.h"

//#define SEND_PWM_BY_TIMER
//#define USE_NO_SEND_PWM
//#define NO_LED_FEEDBACK_CODE // saves 418 bytes program memory

#include <IRremote.hpp>

void setup() {
 /*
     The IR library setup.
     
     La broche utilisée par défaut est la numéro 3
     
  */
  IrSender.begin(); // Start with IR_SEND_PIN as send pin and if NO_LED_FEEDBACK_CODE is NOT defined, enable feedback LED at default feedback LED pin
 

}

/*
   Set up the data to be sent.
   For most protocols, the data is build up with a constant 8 (or 16 byte) address
   and a variable 8 bit command.
   There are exceptions like Sony and Denon, which have 5 bit address.
*/
uint16_t sAddress = 0x0102;
uint8_t sCommand = 0x34;
uint8_t sRepeats = 0;


void loop() {

  // Results for the first loop to: Protocol=NEC Address=0x102 Command=0x34 Raw-Data=0xCB340102 (32 bits)
  //IrSender.sendNEC(sAddress, sCommand, sRepeats);

  
  //    Serial.println(F("Send NECRaw 0xCB340102"));
    IrSender.sendNECRaw(0xCB340102, sRepeats);  // code envoyé 0x20134 et reçu par la RPI

   // IrSender.sendNEC(sAddress, sCommand, sRepeats);

  delay(20);  // delay must be greater than 5 ms (RECORD_GAP_MICROS), otherwise the receiver sees it as one long signal
}
