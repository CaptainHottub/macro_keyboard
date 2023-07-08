#include <Keypad.h>
//https://wokwi.com/projects/361758088356902913

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

const int ModeButton = A0;     // the pin that the Modebutton is attached to

byte rowPins[ROWS] = {4, 5, A3};    //connect to the row pinouts of the keypad
byte colPins[COLS] = {6, 7, 8, 9};  //connect to the column pinouts of the keypad
Keypad keypad = Keypad( makeKeymap(keys), rowPins, colPins, ROWS, COLS );

int buttonState = 0; 
int RXLED = 17; 


String str; // for serial inputs

void setup() {
  pinMode(ModeButton, INPUT_PULLUP);  // initialize the button pin as a input:  
  pinMode(RXLED, OUTPUT); // that is the red led on the board
  
  Serial.begin(9600); // initialize serial communication:
}


// ((1,1) red, (2,1) blue)
void loop() {
  if (digitalRead(ModeButton) == LOW) {
    Serial.println("Mode Button");
    delay(150);
  }

  char key = keypad.getKey();
  if (key) {
    Serial.println(key);
    delay(150);
  }

  // for serial inputs
  //https://www.norwegiancreations.com/2017/12/arduino-tutorial-serial-inputs/
  // if(Serial.available()){
  //         str = Serial.readStringUntil('\n');
  //         Serial.print("You typed: " );
  //         Serial.println(str);
  //     }

}

