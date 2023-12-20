// --------------------------------------------------------------
// Standard Libraries
// --------------------------------------------------------------

#include <HID-Project.h>
#include <Keypad.h>
// This library is for interfacing with the 3x4 Matrix
// Can be installed from the library manager, search for "keypad"
// and install the one by Mark Stanley and Alexander Brevig
// https://playground.arduino.cc/Code/Keypad/

const byte ROWS = 3; //four rows
const byte COLS = 4; //four columns

char keys[ROWS][COLS] = {
  {'1', '2', '3', '4'},  //  the keyboard hardware is  a 3x4 grid... 
  {'5', '6', '7', '8'},
  {'9', '0', 'A', 'B'},  // these values need  to be single char, so...
};
// The library will return the character inside this array when the appropriate
// button is pressed then look for that case statement. This is the key assignment lookup table.
// Layout(key/button order) looks like this
//     |----------------------------|
//     |                  [2/3]*    |     *TRS breakout connection. Keys 5 and 6 are duplicated at the TRS jack
//     |      [ 1] [ 2] [ 3] [ 4]   |     * Encoder A location = key[1]      
//     |      [ 5] [ 6] [ 7] [ 8]   |     * Encoder B location = Key[4]
//     |      [ 9] [10] [11] [12]   |      NOTE: The mode button is not row/column key, it's directly wired to A0!!
//     |----------------------------|




// Variables that will change:
int modePushCounter = 0;       // counter for the number of button presses
int buttonState = 0;           // current state of the button
int lastButtonState = 0;       // previous state of the button
int mouseMove;


const int ModeButton = A0;     // the pin that the Modebutton is attached to
//const int Mode1= A2;
//const int Mode2= A3; //Mode status LEDs

byte rowPins[ROWS] = {4, 5, A3 };    //connect to the row pinouts of the keypad
byte colPins[COLS] = {6, 7, 8, 9 };  //connect to the column pinouts of the keypad
Keypad keypad = Keypad( makeKeymap(keys), rowPins, colPins, ROWS, COLS );


int RXLED = 17; 

void setup() {
  pinMode(ModeButton, INPUT_PULLUP);  // initialize the button pin as a input:  
  pinMode(RXLED, OUTPUT); // that is the red led on the board
  
  Serial.begin(9600); // initialize serial communication:
  //Serial.begin(9600);
}



void loop() {

// turns red leds off
digitalWrite(RXLED, HIGH);
TXLED1;

char key = keypad.getKey();

checkModeButton();

  switch (modePushCounter) {                  // switch between keyboard configurations:
    case 0:                                   //Application Alpha or MODE 0. Example = Every button ends your Zoom call
    // setColorsMode0();                         //indicate what mode is loaded by changing the key colors
     
       if (key) {
    Serial.println(key);
    switch (key) {
      case '1': Serial.println("Button 1") ;  break;
      case '2': Serial.println("Button 2") ;  break;
      case '3': Serial.println("Button 3") ;  break;
      case '4': Serial.println("Button 4") ;  break;
      case '5': Serial.println("Button 5") ;  break;
      case '6': Serial.println("Button 6") ;  break;
      case '7': Serial.println("Button 7") ;  break;
      case '8': Serial.println("Button 8") ;  break;
      case '9': Serial.println("Button 9") ;  break;
      case '0': Serial.println("Button 10") ;  break;
      case 'A': Serial.println("Button 11") ;  break;
      case 'B': Serial.println("Button 12") ;  break;

    }
  }
      break;
      break;
  }

}

void checkModeButton(){
    buttonState = digitalRead(ModeButton);
    if (buttonState == LOW) { // if the state has changed, increment the counter
        // if the current state is LOW then the button cycled:
        // modePushCounter++;
        Serial.println("Mode Button Pressed");
        // Serial.print("number of button pushes: ");
        // Serial.println(modePushCounter);
        // colorUpdate = 0;      // set the color change flag ONLY when we know the mode button has been pressed. 
                            // Saves processor resources from updating the neoPixel colors all the time
    } 

//   if (buttonState != lastButtonState) { // compare the buttonState to its previous state
//     if (buttonState == LOW) { // if the state has changed, increment the counter
//       // if the current state is LOW then the button cycled:
//       modePushCounter++;
//       Serial.println("pressed");
//       Serial.print("number of button pushes: ");
//       Serial.println(modePushCounter);
//       colorUpdate = 0;      // set the color change flag ONLY when we know the mode button has been pressed. 
//                             // Saves processor resources from updating the neoPixel colors all the time
//     } 
//     delay(50); // Delay a little bit to avoid bouncing
//   }
//   lastButtonState = buttonState;  // save the current state as the last state, for next time through the loop
//    if (modePushCounter >3){       //reset the counter after 4 presses CHANGE THIS FOR MORE MODES
//       modePushCounter = 0;}
}


